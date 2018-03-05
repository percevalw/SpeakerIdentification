import string
import nltk
from nltk.parse import stanford
import os
import re

# Some english 'constants' to guide the parsing and help the algorithm find if a term is
# related to the speaker or the other locutor for example
subj_prp = ["i", "you", "he", "she", "we", "they", "somebody", "anybody", "noone", "anyone", "it"]
obj_prp = ["me", "you", "him", "her", "us", "them", "somebody", "anybody", "noone", "anyone", "it"]
expression_verbs = ['said', 'ad', 'cri', 'ask', 'repli', 'return', 'continu', 'observ', 'cal', 'read']
true_roles = {
    "husband": "husband",
    "ladi": "wife",
    "wife": "wife",
    "aunt": "aunt",
    "uncl": "uncle",
    "father": "father",
    "sister": "sister",
    "mother": "mother",
    "daughter": "daughter",
    "girl": "daughter",
    "son": "son",
    "cousin": "cousin",
    "fiance": "married"
}


def load_parser(p, version="3.8.0"):
    """Loads the Stanford Parser located under the path `p`"""
    jar = os.path.join(p, 'stanford-parser.jar')
    model = os.path.join(p, 'stanford-parser-{}-models.jar'.format(version))
    dep_parser = stanford.StanfordDependencyParser(model, jar, model_path='edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz', encoding='utf8')    
    return dep_parser


def custom_triples(root, tree):
    """The Stanford parser function extracts triples from the tree but loses the source index in the tokenized
    sentence: we need to keep it in order to make inferences based on distances between words and to work on 
    differents arrays a the same time, so this function return a list of triples who tagged token are in the form
    (index, ctag)"""
    for dep, child_addresses in root['deps'].items():
        for child_address in child_addresses:
            child = tree.get_by_address(child_address)
            yield (root['address']-1, root['ctag']), dep, (child_address-1, child['ctag'])
            yield from custom_triples(child, tree)
            

def extract_features_from_narration(text, parser, stemmer, people, debug=False):
    """Returns two pairs of sets, a pair for the speaker and a pair for the destinator.
    Each pair is composed of a first set gathering the names (matched with those in `people`)
    found for the locutor, and a set of facts in the Prolog syntax that could apply to this locutor
    
    The variable X and U in the Prolog facts refers to the speaker, whereas Y and V refers to other people
    
    The `parser` is an nltk parser
    The `stemmer` parameter is an nltk stemmer to transform each token into its semantical root to make
    the keyword matching easier
    
    Example:
    > extract_features_from_narration("said her daugther to Mr_Bennet", ...)
    
    `({}, {"related(X, Y, daughter)", "status(Y, female)}), ({Mr_Bennet}, {})
    """
    text = text if text.strip()[0] in string.ascii_uppercase else 'XXX ' + text
    try:
        tree = next(parser.raw_parse(text))
    except Exception as e:
        return (set(), set()), (set(), set())
            
    token_count = max(a for a in tree.nodes)
    stemmed = ['']*token_count
    tagged = [('', '') for i in range(token_count)]
    for i, n in tree.nodes.items():
        if i != 0:
            # If the first letter of this sentence is in lowercase, then we consider that it is following another
            # piece of sentence, most likely an utterance, and we put a fake subject "XXX" to help the parser
            # find the real subject as a temporary fake complement.
            # We need to do this because the Stanford parser has shown strong difficulties parsing these kind of sentence
            # correctly
            stemmed[i-1] = stemmer.stem(n['word']) if n['word'] not in people and n['word'] != 'XXX' else n['word']
            tagged[i-1] = (n['word'], n['ctag'])

    triples = list(custom_triples(tree.root, tree))

    if debug:
        print("--- triples ---")
        display(triples)
        print("--- stemmed ---")
        display(stemmed, token_count)

    subj_score, subj, subj_ranks = extract_subj_from_triples(triples, stemmed, return_ranks=True)
    if debug:
        display(list(enumerate(zip(subj_ranks, stemmed))))

    parser_nsubj_triples = [t for t in triples if t[1].startswith('nsubj')]

    # Puts the true subject at the right place (most of the time at the beginning)
    # If the fake subject was picked, then switch it with the dobj and remove it from the sentence
    if stemmed[subj] == 'XXX':
        parser_verb = next((t[0][0] for t in triples if t[2][0] == subj and t[1].startswith('nsubj')), None)
        parser_dobj = next((t[2][0] for t in triples if t[0][0] == parser_verb and t[1].startswith('dobj')), None)

        if parser_dobj is not None and parser_verb is not None:
            tagged, stemmed = tuple(switch_tokens_in_tree(subj, parser_dobj, tree, (tagged, stemmed), remove1=True))
            tree = next(parser.tagged_parse(tagged))
            triples = list(custom_triples(tree.root, tree))

            subj_score, subj, subj_ranks = extract_subj_from_triples(triples, stemmed, return_ranks=True)
            if debug:
                print("re-parsing with", stemmed)
                print("--- triples ---")
                display(triples)
                print("--- stemmed ---")
                display(stemmed, token_count)
                display(list(enumerate(zip(subj_ranks, stemmed))))


    dest_score, dest, dest_ranks = extract_dest_from_triples(triples, stemmed, return_ranks=True)
    if debug:
        display(list(enumerate(zip(dest_ranks, stemmed))))
    if dest == subj or dest_score < 3 or abs(dest-subj) > 40:
        dest = None

    subj_names, subj_properties = set(), set()
    dest_names, dest_properties = set(), set()

    if subj is not None:
        # + 1 because the 0 node is for the empty root only
        for sub_subj in get_tree_leaves(tree, subj):
            subj_token = stemmed[sub_subj]
            if subj_token in people:
                subj_names.add(subj_token)
            if subj_token in ['he', 'man', 'boy', 'lad', 'him']:
                subj_properties.add('status(X, male)')
            elif subj_token in ['she', 'ladi', 'girl']:
                subj_properties.add('status(X, female)')
            if subj_token in true_roles:
                subj_properties.add('related(X, Y, {})'.format(true_roles[subj_token]))

            subj_nmod_score, subj_nmod = extract_relational_mod_from_triples(triples, stemmed, subj)
            if subj_nmod_score >= 1:
                subj_nmod_token = stemmed[subj_nmod]
                if subj_nmod_token in ['his', 'he', 'him']:
                    subj_properties.add('status(Y, male)')
                elif subj_nmod_token in ['her', 'she']:
                    subj_properties.add('status(Y, female)')


    if dest is not None:
        # + 1 because the 0 node is for the empty root only
        for sub_dest in get_tree_leaves(tree, dest):
            dest_token = stemmed[sub_dest]

            if dest_token in people:
                dest_names.add(dest_token)
            if dest_token in ['he', 'man', 'boy', 'lad', 'him']:
                dest_properties.add('status(U, male)')
            elif dest_token in ['she', 'ladi', 'girl']:
                dest_properties.add('status(U, female)')
            if dest_token in true_roles:
                dest_properties.add('related(U, V, {})'.format(true_roles[dest_token]))

            dest_nmod_score, dest_nmod = extract_relational_mod_from_triples(triples, stemmed, dest)
            if dest_nmod_score >= 1:
                dest_nmod_token = stemmed[dest_nmod]
                if dest_nmod_token in ['his', 'he', 'him']:
                    dest_properties.add('status(V, male)')
                elif dest_nmod_token in ['her', 'she']:
                    dest_properties.add('status(V, female)')
                
    return (subj_names, subj_properties), (dest_names, dest_properties)


def extract_features_from_utterance(text, parser, stemmer, people_to_code, debug=False):
    """Returns two pairs of sets, a pair for the speaker and a pair for the destinator.
    Each pair is composed of a first set gathering the names (matched with those in `people`)
    found for the locutor, and a set of facts in the Prolog syntax that could apply to this locutor
    
    The variable X and U in the Prolog facts refers to the speaker, whereas Y and V refers to other people
    
    The `parser` is an nltk parser
    The `stemmer` parameter is an nltk stemmer to transform each token into its semantical root to make
    the keyword matching easier
    
    Example:
    > extract_features_from_utterance("Dear Mr_Bennet, you should know that my uncle is mean", ...)
    
    `({}, {"related(Y, X, uncle)"}), ({Mr_Bennet}, {})
    """
    text = re.sub('([A-Z][a-z])*s+([^\w])', r'\1\2', text)
            
    try:
        tree = next(parser.raw_parse(text))
    except Exception as e:
        return (tuple([None]*4), tuple([None]*4))
        
    token_count = max(a for a in tree.nodes)
    stemmed = ['']*token_count
    tagged = [('', '') for i in range(token_count)]
    for i, n in tree.nodes.items():
        if i != 0:
            stemmed[i-1] = stemmer.stem(n['word']) if n['word'] not in people_to_code else n['word']
            tagged[i-1] = (n['word'], n['ctag'])

    triples = list(custom_triples(tree.root, tree))

    if debug:
        print("--- triples ---")
        display(sorted(triples, key=lambda x: (x[0][0], x[2][0])))
        print("--- stemmed ---")
        display(list(enumerate(stemmed)), token_count)

    subj_names, subj_properties = set(), set()
    dest_names, dest_properties = set(), set()

        # + 1 because the 0 node is for the empty root only
    for_subj = True
    non_anaphore = set()
    for i, triple in enumerate(triples):
        if triple[1] == 'nsubj' and triple[0][1].startswith('VB'):
            non_anaphore.add(triple[2][0])
        if triple[1] == 'nmod:poss':
            if stemmed[triple[2][0]] in ('my', 'our'):
                for_subj = True
            elif stemmed[triple[2][0]] == 'your':
                for_subj = False
            else:
                continue
            
            poss = triple[0][0]
            for sub in get_tree_leaves(tree, poss):
                token = stemmed[sub]
                if token in true_roles:
                    if for_subj:
                        subj_properties.add('related(Y{}, X, {})'.format(i, true_roles[token]))
                    else:
                        dest_properties.add('related(V{}, U, {})'.format(i, true_roles[token]))
                elif token in people_to_code:
                    if for_subj:
                        subj_properties.add('Y{}={}'.format(i, people_to_code[token]))
                    else:
                        dest_properties.add('V{}={}'.format(i, people_to_code[token]))
    other_mentions = [i for i, t in enumerate(stemmed) if t in ('you', 'your', 'dear')]
    people_names = [(t, min([abs(i-j) for j in other_mentions])) for i, t in enumerate(stemmed)
                    if t in people_to_code and
                       i not in non_anaphore]
    
    if len(people_names) > 0:
        dest_names.add(min(people_names, key=lambda x: x[1])[0])
                
    return (subj_names, subj_properties), (dest_names, dest_properties)



def extract_subj_from_triples(triples, stemmed, return_ranks=False):
    """Extract the subject from the `triples` list
    Rank each token with score to find the best candidate to be the sentence subject
    
    Example:
    "she said to her father" -> "she"
    
    """
    subj_ranks = [0] * len(stemmed)
    for (p1, t1), dep, (p2, t2) in triples:
        p1, p2 = int(p1), int(p2)
        if t2.startswith("NN"):
            subj_ranks[p2] += 1
        if t2.startswith("PRP") and stemmed[p2] in subj_prp:
            subj_ranks[p2] += 1
        if dep == 'nsubj': # word is marked as subject
            # if the verb is in first position, there may be mistakes
            if p1 == 0: 
                subj_ranks[p2] += 1
            else:
                subj_ranks[p2] += 2
        if t1.startswith("VB"): # if it is a dependency toward a verb
            subj_ranks[p2] += 1
            if p1 == 0: # first verb after utterance
                subj_ranks[p2] += 1
                if dep.startswith("dobj"):
                    subj_ranks[p2] += 1
        if stemmed[p1] in expression_verbs:
            subj_ranks[p2] += 1
    subj_score, subj = max(zip(subj_ranks, range(len(stemmed))))
    if return_ranks:
        return subj_score, subj, subj_ranks
    return subj_score, subj


def extract_dest_from_triples(triples, stemmed, return_ranks=False):
    """Extract the destinator from the `triples` list
    Rank each token with score to find the best candidate to be the sentence destinator
    
    Example:
    "she said to her father" -> "father"
    
    """
    dest_ranks = [0] * len(stemmed)
    for (p1, t1), dep, (p2, t2) in triples:
        p1, p2 = int(p1), int(p2)
        if t2.startswith("NN"):
            dest_ranks[p2] += 1
        if t2.startswith("PRP") and stemmed[p2] in obj_prp:
            dest_ranks[p2] += 1
        if t1.startswith("VB"): # if it is a dependency toward a verb
            dest_ranks[p2] += 1
            if p1 == 0: # first verb after utterance
                dest_ranks[p2] += 1
        if dep.startswith("nmod"):
            dest_ranks[p2] += 1
        if stemmed[p1] in expression_verbs:
            dest_ranks[p2] += 1
    dest_score, dest = max(zip(dest_ranks, range(len(stemmed))))
    if return_ranks:
        return dest_score, dest, dest_ranks
    return dest_score, dest


#Extract the relation
def extract_relational_mod_from_triples(triples, stemmed, token_i, return_ranks=False):
    """Extract the relational modifier of a specific token, if any
    Rank each token with score to find the best candidate
    
    Example:
    "she said to her father", "father" -> "her"
    
    """
    nmod_ranks = [0] * len(stemmed)
    for (p1, t1), dep, (p2, t2) in triples:
        p1, p2 = int(p1), int(p2)
        if p1 != token_i:
            continue
        if t2.startswith("NN"):
            nmod_ranks[p2] += 1
        if t2.startswith("PRP"):
            nmod_ranks[p2] += 1
        if dep.startswith("nmod"):
            nmod_ranks[p2] += 1
        if stemmed[p1] in expression_verbs:
            nmod_ranks[p2] += 1
    nmod = max(range(len(nmod_ranks)), key=lambda x: nmod_ranks[x])
    nmod_score, nmod = max(zip(nmod_ranks, range(len(stemmed))))
    if return_ranks:
        return nmod_score, nmod, nmod_ranks
    return nmod_score, nmod


def get_tree_leaves(tree, root_i):
    """Get the nltk tree leaves, relative to the token of at position `root_i`"""
    def _rec(i):
        node = tree.get_by_address(i)
        yield node['address'] - 1
        for deps in node['deps'].values():
            for v in deps:
                yield from _rec(v)
    
    return sorted(list(_rec(root_i+1)))


def switch_tokens_in_tree(token1_root, token2_root, tree, lists, remove1=False, remove2=False):
    """Switch to subtrees of tokens, contiguous or not in a tree, by transforming the `lists`
    accordingly
    
    Example:
    
    > "XXX said Mr_Bennet to his daughter", 0 (XXX) <--> 2 (Mr_Bennet), remove1 (remove XXX)
    Mr_Bennet said to his daughter
    """
    
    tokens1 = [t for t in get_tree_leaves(tree, token1_root)]
    tokens2 = [t for t in get_tree_leaves(tree, token2_root)]
    f1, f2 = tokens1[0], tokens2[0]
    tokens1, tokens2 = sorted((tokens1, tokens2))
    for l in lists:
        newl = []
        for i in range(len(l)):
            if i == f1 and not remove2:
                newl.extend([l[t] for t in tokens2])
            if i == f2 and not remove1:
                newl.extend([l[t] for t in tokens1])
            if i not in tokens1 and i not in tokens2:
                newl.append(l[i])
        yield newl
