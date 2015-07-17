#!/usr/bin/python

import argparse
import redmine_interface
import unittest

redmine_url = "http://www.redmine.org"
testtrackers = ["Defect|bugs", "Feature|features", "Patch|patches"]

DEFAULT_VERBOSITY_LEVEL = 0


class TestRedmineIfFunctions(unittest.TestCase):
    def setUp(self):
        global redmine_url

        redmine_interface.setup(redmine_url, testtrackers)

    def test_help(self):
        res = redmine_interface.parse_command(["help"])
        self.assertRegexpMatches("".join(res), "Available commands:")

    def test_empty_string(self):
        res = redmine_interface.parse_command("")
        self.assertRegexpMatches("".join(res), "Available commands:")

    def test_empty_list(self):
        res = redmine_interface.parse_command([])
        self.assertRegexpMatches("".join(res), "Available commands:")

    def test_single_issue_not_list_formatted(self):
        res = redmine_interface.parse_command("17113")
        self.assertIn("'cmd' must be a list of strings", "".join(res))

    def test_single_issue_list_formatted(self):
        res = redmine_interface.parse_command(["17113"])
        self.assertEqual("".join(res), "Parent task invalid although type ahead shows ticket @ http://www.redmine.org/issues/17113")

    def test_listp(self):
        res = redmine_interface.parse_command(["listp"])
        for r in res:
            self.assertEqual(r, "Redmine")


def _main():

    global DEFAULT_VERBOSITY_LEVEL
    global redmine_url

    verbosity_level = DEFAULT_VERBOSITY_LEVEL

    argparser = argparse.ArgumentParser()
    argparser.add_argument('-u', '--url', help='Specify a redmine URL \
                           (do not forget http(s):// !)')
    argparser.add_argument('-v', '--verbosity', help='Specify verbosity for \
                           printouts during test execution. \
                           Valid values = 0,1,2,3. Default value = 0')
    args = argparser.parse_args()

    if args.verbosity:
        verbosity_level = int(args.verbosity)
    if args.url:
        redmine_url = args.url

    print("Verbosity level = %d" % verbosity_level)
    print("Redmine URL = %s" % redmine_url)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestRedmineIfFunctions)
    print "###################"
    unittest.TextTestRunner(verbosity=verbosity_level).run(suite)

    print "###################"
    print " Tests yet to be made into unit test cases"
    print "###################"

#    print "FETCH BUGS"
#    res = redmine_interface.parse_command(["bugs"])
#    for r in res:
#        print r

#    print "FETCH FEATURES"
#    res = redmine_interface.parse_command(["features"])
#    for r in res:
#        print r

if __name__ == '__main__':
    _main()
