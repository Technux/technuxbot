#!/usr/bin/python

try:
    import redmine_interface
except ImportError as ie:
    print ie
    exit(1)

redmineurl = "http://www.redmine.org"
testtrackers = ["Defect|bugs","Feature|features","Patch|patches"]
redmine_interface.setup(redmineurl, testtrackers)


def perform_command_test(cmd):
    res = redmine_interface.parse_command(cmd)
    print "".join(res)

perform_command_test("")
perform_command_test([])
perform_command_test("17113")
perform_command_test(["17113"])
perform_command_test(["help"])

print "FETCH BUGS"
res = redmine_interface.parse_command(["bugs"])
for r in res:
    print r
print "FETCH FEATURES"
res = redmine_interface.parse_command(["features"])
for r in res:
    print r

res = redmine_interface.parse_command(["listp"])
for r in res:
    print r
