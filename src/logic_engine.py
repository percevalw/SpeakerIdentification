import time
import re
import numpy as np

def top_level_split(a, sep=','):
    res = []
    cur = ""
    splits = re.split('\s*([{}\(\)])\s*'.format(sep), a)
    level = 0
    for s in splits:
        if s == '':
            continue
        if s in sep and level == 0:
            res.append(cur)
            cur = ""
            continue
        cur += s 
        if s == '(':
            level += 1
        if s == ')':
            level -= 1
    if cur != '':
        res.append(cur)
    return res

def get_perm(*args):
    ref = np.unique([e for arg in args for e in arg])
    inv_ref = {str(k): i for i, k in enumerate(ref)}
    args = [[inv_ref[str(e)] for e in arg] for arg in args]
    return args

def make_operation(skeleton):
    full_in_subscripts = sum(skeleton['deps_args'], [])
    curated_out_subscripts = [i if i in full_in_subscripts else Ellipsis for i in skeleton['rule_args']]
    def _op(matrices):
        args = [i
               for name, subs in zip(skeleton['deps_name'], skeleton['deps_args'])
               for i in (matrices[name], subs)] + [curated_out_subscripts]
        new_val = np.logical_or(matrices[skeleton['rule_name']], np.einsum(*args))
        delta = np.bitwise_xor(new_val, matrices[skeleton['rule_name']])
        matrices[skeleton['rule_name']] = new_val
        return delta.sum() != 0
        
    return _op

def extract_expression(expr_str):
    deps = [d for d in top_level_split(expr_str, sep='!,') if d != '']

    operation_dep_names = []
    operation_dep_args = []
    for dep in deps:
        try:
            name, args = re.match('(\w+)\(([\w, ]+)\)', dep).groups()
        except Exception as e:
            raise Exception("Error parsing {}".format(dep))
        words = re.findall('\w+', dep)

        operation_dep_names.append(name)
        operation_dep_args.append(re.split('\s*,\s*', args))
    return operation_dep_names, operation_dep_args

def extract_rules(rules_str, reciprocal=False):
    rules_list = re.findall('\w+\([\w,\[\]| ]+\)+:-.*?\.', rules_str)
    new_rules = []
    rules = {}
    operation_skeletons = []
    for rule in rules_list:
        try:
            base, base_args, deps_str = re.match('(\w+)\(([\w, ]+)\):-(.*)\.', rule).groups()
        except Exception as e:
            raise Exception("Error parsing {}".format(rule))

        rules[base] = base_args.count(',')+1

        operation_dep_names, operation_dep_args = extract_expression(deps_str)
        
        for n, a in zip(operation_dep_names, operation_dep_args):
            rules[n] = len(a)
        
        [base_subscripts, *dep_subscripts] = get_perm(re.split('\s*,\s*', base_args), *operation_dep_args)
        operation_skeletons.append({
            "rule_args": base_subscripts,
            "deps_args": dep_subscripts,
            "rule_name": base,
            "deps_name": operation_dep_names
        })
        if reciprocal:
            for dep_name, dep_args in zip(operation_dep_names, dep_subscripts):
                if dep_name != base and dep_name not in ("diff",) and set(dep_args) <= set(base_subscripts):
                    operation_skeletons.append({
                        "rule_args": dep_args,
                        "deps_args": [base_subscripts],
                        "rule_name": dep_name,
                        "deps_name": [base]
                    })
    return operation_skeletons, rules

def extract_facts(facts_str, entities=None):
    facts = []
    entities = list(entities) if entities is not None else []
    rules = {}
    for name, args_str in re.findall("([\w_]+)\(([\w,_\s]+)\).", facts_str):
        args = re.split('\s*,\s*', args_str)
        entities.extend(args)
        facts.append((name, args))
        rules[name] = len(args)
    entities = np.unique(entities)
    entities_inv = {v: i for i, v in enumerate(entities)}
    facts = [{"rule_name": name, "args": [entities_inv[a] for a in args]} for name, args in facts]
    return facts, rules, entities

def register_facts(matrices, facts):
    for fact in facts:
        matrices[fact["rule_name"]][tuple(fact['args'])] = True

def query(matrices, entities, query_str, *args):
    # Comments will be documented with the following example mother(X,Y),aunt(X,lizzy).
    
    # Build the entity name -> entity matrix index mappings
    entities_mapping = {n: i for i, n in enumerate(entities)}
    
    # Extract the query without the . at the end
    query_str = re.match('(.*)\.?', query_str).group(0)
    
    # and split in into rule names and rule args names (its dependencies)
    deps_names, deps_args = extract_expression(query_str)
    
    # Detect which vars are free, ie not bound to a specific entity (cap. 1st letter)
    all_vars = [v for args in deps_args for v in args]
    free_vars = np.unique([v for v in all_vars if re.match('[A-Z]', v[0])])
    
    # evaluate the matrices for the bound arguments: aunt (shape NxN) -> aunt[:, idx(lizzy)] (shape N)
    bound_matrices = {
        name: matrices[name][tuple(slice(None) if a in free_vars else entities_mapping[a] for a in args)]
        for name, args in zip(deps_names, deps_args)
    }
    
    # Transform the arguments into normalized indices
    free_dep_args = [[v for v in args if v in free_vars] for args in deps_args]
    [*free_dep_idx, base_idx] = get_perm(*free_dep_args, free_vars)
    
    # And apply the multi dot product on the matrices (einsum)
    einsum_args = [i
           for name, subs in zip(deps_names, free_dep_idx)
           for i in (bound_matrices[name], subs)] + [base_idx]
    einsum_res = np.einsum(*einsum_args)
    
    # We want the indices on the free_vars axis (that's all of the axis actually) that led to True values
    # The result axes are in the order given by the permutation on 'free_vars', so we get the var_name -> axis index mapping
    reordered_arg_names = sorted(enumerate(free_vars), key=lambda x: base_idx[x[0]])
    
    # and apply it on the result, as well as the mapping on entities to have entity names in the output
    res = [
        {arg_name: entities[entity_idx] for (_, arg_name), entity_idx in zip(reordered_arg_names, true_tuple)}
        for true_tuple in np.argwhere(einsum_res)
    ]

    return res

class LogicEngine:
    def __init__(self, rules_str, facts_str=None, entities=None, verbose=1, reciprocal=False):
        operation_skeletons, rules_1 = extract_rules(rules_str, reciprocal=reciprocal)
        rules = dict(rules_1)
        
        facts, self.entities = [], entities if entities is not None else []
        if facts_str is not None:
            facts, rules_2, self.entities = extract_facts(facts_str, self.entities)
            rules.update(rules_2)
        
        rules["diff"] = 2
        
        entities_count = len(self.entities)
        
        self.matrices = {name: np.zeros((entities_count,)*arity, dtype='bool') for name, arity in rules.items()}

        # Special matrices, used for the X \= Y operation
        self.matrices['diff'][:] = 1
        self.matrices['diff'][range(entities_count),range(entities_count)] = 0
        
        if facts is not None:
            register_facts(self.matrices, facts)
        
        self.operations = [make_operation(o)
                      for o in operation_skeletons]
        
        if verbose > 0:
            print("Defined {} properties for {} entities, and {} operations".format(len(self.matrices), len(self.entities), len(self.operations)))
        
    def run(self, max_iter=50, verbose=1):
        if verbose > 0:
            start_time = time.time()
        for i in range(max_iter):
            has_changed = False
            for j, operation in enumerate(self.operations):
                change = operation(self.matrices)
                has_changed = has_changed or change
            if not has_changed:
                break
        if verbose > 0:
            end_time = time.time()
            print("Total: {:.4f}s".format(end_time-start_time))
            print("Stopped after {} iterations".format(i))
    
    def assert_facts(self, facts_str):
        facts, rules, entities = extract_facts(facts_str, self.entities)
        assert set(entities) <= set(self.entities), "Cannot define new entities after initialization {}".format(set(entities) - set(self.entities))
        assert set(rules) <= set(self.matrices), "Cannot define new rules after initialization {}".format(set(entities) - set(self.entities))
        register_facts(self.matrices, facts)
    
    def query(self, query_str):
        return query(self.matrices, self.entities, query_str)