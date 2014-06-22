from redmine import Redmine
from redmine import exceptions

redmine_obj = None


def setup(url):
    global redmine_obj
    redmine_obj = Redmine(url)


def url_from_issue(issue):
    global redmine_obj
    return redmine_obj.url + "/issues/" + str(issue.id)


def redmine_usage():
    return "redmine [command [args]]\n\n" \
           "Available commands:\n" \
           "<issue number>   --> Get info and link for single issue number\n" \
           "bugs [<project>] --> Get info on all issues in the bug tracker [for <project>]\n" \
           "help             --> This help text\n" \
           "listp            --> List all available projects\n" \
           "\n"


def parse_command(cmd):
    """
    Parse a redmine command

    cmd -- list of strings

    returns a list of strings containing
    a (potential) answer from the redmine server
    """

    global redmine_obj

    if not cmd:
        return [redmine_usage()]

    if isinstance(cmd, list) is False:
        return ["%s: 'cmd' must be a list of strings" % __name__]

    if isinstance(cmd[0], str) is False:
        return ["%s: 'cmd' must be a list of strings" % __name__]

    if cmd[0].isdigit() is True:
        try:
            res = redmine_obj.issue.get(int(cmd[0]))
            return [res.subject + " @ " + url_from_issue(res)]
        except exceptions.ResourceNotFoundError:
            return ["Issue with id '" + cmd[0] + "' does not exist!"]

    supported_commands = ["bugs", "help", "listp"]
    if cmd[0] not in supported_commands:
        return ["'" + cmd[0] + "'" + " is not a supported command!",
                redmine_usage()]

    if cmd[0] == "bugs":
        try:
            bugs_arg = cmd[1]
        except IndexError:
            bugs_arg = ""
        if bugs_arg is not "":
            proj = redmine_obj.project.get(bugs_arg)
            all_bugs = redmine_obj.issue.filter(
                tracker_id=1, project_id=proj.id, subproject_id='!*')
        else:
            all_bugs = redmine_obj.issue.filter(tracker_id=1)

        bug_list = []
        for b in all_bugs:
            bug_list.append("#" + str(b.id) + ": " + b.subject)

        return bug_list

    if cmd[0] == "help":
        return [redmine_usage()]

    if cmd[0] == "listp":
        plist = []
        for project in redmine_obj.project.all():
            plist.append(project.name)

        return plist
