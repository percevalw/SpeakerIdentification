import pexpect

import re

MAP_REGEX = "([A-Z]+) = (\w+)"

class Prolog:
    def __init__(self, path, command="/usr/bin/env swipl"):
        self.path = path
        self.command = command
        self.child = None
        self.closed = True
        
    def run(self):
        self.child = pexpect.spawnu("{} {}".format(self.command, self.path))
        self.child.expect("\n\?- ", timeout=5)
        self.closed = False
        
    def close(self):
        # make sure the dbconnection gets closed
        if self.child and not self.child.closed:
            self.child.close()
            self.closed = True
        
    def __enter__(self):
        # make a database connection and return it
        self.run()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def query(self, s, debug=False, newline=True):
        if newline:
            self.child.sendline(s)
        else:
            self.child.send(s)
        i = self.child.expect(["\..*?true.*\?- ",
                      "\..*?false.*\?- ",
                      "([A-Z]+) = (\w+)\..*\?- ",
                      "([A-Z]+) = (\w+) ",
                      "(ERROR\: .*)\?- ",
                      "\?- ", pexpect.TIMEOUT], timeout=2)
        if (debug):
            print(i)
            print("BEFORE")
            print(repr(self.child.before))
            print(self.child.before)
            print("AFTER")
            print(repr(self.child.after))
            print(self.child.after)
        if i == 2 or i == 3:
            res = {}
            for var_map in re.findall(MAP_REGEX, self.child.before+self.child.after):
                res[var_map[0]] = {var_map[1]};
            if i == 3:
                next_query = self.query(";", debug=debug, newline=False)
                if next_query is False:
                    return res
                for key, values in next_query.items():
                    res[key] = values | res.get(key, set())
            return res
        if i == 0 or i == 1:
            if debug:
                print("FINALY")
                print(repr(self.child.before))
        if i == 4:
            raise Exception(self.child.match.group(1))

        return i==0
    

