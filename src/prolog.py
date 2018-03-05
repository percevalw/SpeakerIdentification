# Bridge between Prolog and Python
# Not really stable but good enough for this project
# A real solution would be to help the contributors of "swipy"
# to port their project to py3, which is not supported by their
# code at the moment

import pexpect
import re
import types 

MAP_REGEX = "([A-Z]+) = (\w+)"

def change_func_args(function, new_args):
    """Dynamicly change a Python function skeleton, not stable
    Create a new function with its arguments renamed to new_args."""
    code_obj = getattr(function, 'func_code', getattr(function, '__code__'))
    # assert(0 <= len(new_args) <= code_obj.co_argcount)
    # the arguments are just the first co_argcount co_varnames
    # replace them with the new argument names in new_args
    new_varnames = tuple(["self"]+list(new_args[:code_obj.co_argcount+1]) +
                         list(code_obj.co_varnames[code_obj.co_argcount+1:]))
    # type help(types.CodeType) at the interpreter prompt for information
    # print(code_obj.co_argcount, code_obj.co_varnames, new_varnames)
    new_code_obj = types.CodeType(code_obj.co_argcount,
                                  code_obj.co_kwonlyargcount,
                                  code_obj.co_nlocals,
                                  code_obj.co_stacksize,
                                  code_obj.co_flags,
                                  code_obj.co_code,
                                  code_obj.co_consts,
                                  code_obj.co_names,
                                  new_varnames,
                                  code_obj.co_filename,
                                  code_obj.co_name,
                                  code_obj.co_firstlineno,
                                  code_obj.co_lnotab,
                                  code_obj.co_freevars,
                                  code_obj.co_cellvars)
    # print(test.__kwdefaults__, test.__closure__)
    modified = types.FunctionType(
        new_code_obj,
        getattr(function, 'func_globals', getattr(function, '__globals__')),
        function.__name__,
        function.__kwdefaults__,
        function.__closure__
    )
    
    function.__code__ = modified.__code__  # replace code portion of original

class Prolog:
    def __init__(self, path, command="/usr/bin/env swipl", bind_rules=False):
        self.path = path
        self.command = command
        self._interp = None
        self.closed = True
        self.bind_rules = bind_rules
        
    def run(self):
        self._interp = pexpect.spawnu("{} {}".format(self.command, self.path))
        self._interp.expect("\n\?- ", timeout=5)
        self.closed = False
        if self.bind_rules:
            self.do_bind_rules()
        
    def close(self):
        # make sure the dbconnection gets closed
        if self._interp and not self._interp.closed:
            self._interp.close()
            self.closed = True
        
    def __enter__(self):
        # make a database connection and return it
        self.run()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _query(self, s, debug=False, newline=True, return_stdout=False):
        if newline:
            self._interp.sendline(s)
        else:
            self._interp.send(s)
        i = self._interp.expect(["\.(.*?)true\.\\x1b\[0m\\r\\n\\r\\n\?- ",
                      "\.(.*?)false\.\\x1b\[0m\\r\\n\\r\\n\?- ",
                      "([A-Z]+) = (\w+)\..*\?- ",
                      "([A-Z]+) = (\w+) ",
                      "(ERROR\: .*)\?- ",
                      "\?- ", pexpect.TIMEOUT], timeout=2)
        if (debug):
            print(i)
            print("BEFORE")
            print(repr(self._interp.before))
            print(self._interp.before)
            print("AFTER")
            print(repr(self._interp.after))
            print(self._interp.after)
        if i == 2 or i == 3:
            res = [{}]
            for var_map in re.findall(MAP_REGEX, self._interp.before+self._interp.after):
                res[0][var_map[0]] = var_map[1];
            if i == 3:
                next_query = self._query(";", debug=debug, newline=False)
                if next_query is False or next_query is None:
                    return res
                res += next_query
            return res
        if i == 0 or i == 1:
            if debug:
                print("FINALY")
                print(repr(self._interp.before))
            if return_stdout:
                return self._interp.match.group(1)
            return i == 0
        if i == 4:
            raise Exception(self._interp.match.group(1))
            
    def query(self, s, debug=False, return_stdout=False):
        result = self._query(s, debug=debug, return_stdout=return_stdout)
        if type(result) is list:
            return list({str(sorted(v.items())):v for v in result}.values())
        else:
            return result
        
    def assert_facts(self, s, debug=False, return_stdout=False):
        assertions = [a.strip() for a in s.split('.')]
        assertions = [a for a in assertions if len(a)>0]
        assertions = ["assert({}).".format(assertion) for assertion in assertions]
        for a in assertions:
            self.query(a, debug, return_stdout)
#        print("\n".join(assertions))
#        return self.query("\n".join(assertions), debug, return_stdout)
        
    def do_bind_rules(self):
        global code_obj
        listing = self.query("listing.", return_stdout=True)
        
        # for all rules matching our rule regex in the listing output of Prolog
        rules = set([(x, param.count(',')+1, param, full)
         for (full, x, param)
         in re.findall("\r\n((\w+)\(([A-Z, ]+)\)(?:.|\n)*?\.)", listing)])
        
        # make a custom query and add it as a bound method to the list
        for name, arity, args_name, full in rules:
            def make_query_string(*args):
                return "{}({}).".format(name, ", ".join(args))
            def rule(self, A, B, C, D):
                return self.query(make_query_string(A, B, C, D))
            
            # inspect(rule.__code__)
            # type help(types.CodeType) at the interpreter prompt for information
            codestring = (b'|\x00\x00j\x00\x00\x88\x00\x00|'+
                b'|'.join(bytes((i+1, 0)) for i in range(arity)) +
                b'\x83'+bytes((arity,))+
                b'\x00\x83\x01\x00S')
            new_code_obj = types.CodeType(
                arity+1, # argcount
                0, # kwonlyargcount
                arity+2, # nlocals
                5, # stacksize
                19, # flags
                codestring, # codestring
                (None,), # constants
                ('query',), # names
                ("self", ) + tuple(args_name.split(', ')), # varnames
                "see code of Prolog-do_bind_rules", # filename
                name, # name
                4, #firstlineno,
                b'\x00\x01\x15\x01', # lnottab
                ('make_query_string',), # freevars
                (), # cellvars
             )
            
            # see https://github.com/python/cpython/blob/2.7/Lib/inspect.py
            # for more insight
            modified = types.FunctionType(
                new_code_obj,
                rule.__globals__,
                closure=rule.__closure__
            )
            modified.__doc__ = full
            
            setattr(self,name,modified.__get__(self, Prolog))
            