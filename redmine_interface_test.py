#!/usr/bin/python

try:
    import redmine_interface
except ImportError as ie:
    print ie
    exit(1)

redmineurl="http://www.redmine.org"

redmine_interface.setup(redmineurl)

def perform_command_test(cmd):
    res = redmine_interface.parse_command(cmd)
    print "".join(res)

perform_command_test("")
perform_command_test([])
perform_command_test("17113")
perform_command_test(["17113"])
perform_command_test(["help"])

#res = redmine_interface.parse_command(["bugs"])
#for r in res:
#    print r

res = redmine_interface.parse_command(["listp"])
for r in res:
    print r
