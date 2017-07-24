"""
Author: Technux
website: http://www.technux.se
mail:   support@technux.se
"""

from redminelib import Redmine
from redminelib import exceptions

redmine_obj = None
tracker_dict = {}


def setup(url, trackers):
    """
    setup()

    Setup singleton redmine object

    url -- redmine server url
    trackers -- [tracker_1|command_1, tracker_2|command_2, ...]
    """
    global redmine_obj
    global tracker_dict

    redmine_obj = Redmine(url)

    tracker_namecmd_dict = {}
    for t in trackers:
        tmp = t.split('|')
        tracker_namecmd_dict[tmp[0]] = tmp[1]

    all_trackers = redmine_obj.tracker.all()

    # maps tracker commands to tracker id numbers
    for t in all_trackers:
        for tn in tracker_namecmd_dict.keys():
            if t.name == str(tn):
                tracker_dict[tracker_namecmd_dict[tn]] = t.id


def url_from_issue(issue):
    """
    url_from_issue()

    Get the link to a specified redmine issue
    """
    global redmine_obj
    return redmine_obj.url + "/issues/" + str(issue.id)


def redmine_usage():
    """
    redmine_usage()

    Print the usage text for the redmine interface
    """
    return "redmine [command [args]]\n\n" \
           "Available commands:\n" \
           "<issue number>   --> Get info and link for single issue number\n" \
           "bugs [<project>] --> Get info on all issues in the bug tracker "\
           "[for <project>]\n" \
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
    global tracker_dict

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

    supported_commands = ["help", "listp"]
    supported_commands += tracker_dict.keys()
    if cmd[0] not in supported_commands:
        return ["'" + cmd[0] + "'" + " is not a supported command!",
                redmine_usage()]

    if cmd[0] in tracker_dict.keys():
        try:
            cmd_arg = cmd[1]
        except IndexError:
            cmd_arg = ""
        if cmd_arg is not "":
            proj = redmine_obj.project.get(cmd_arg)
            all_tickets = redmine_obj.issue.filter(
                tracker_id=tracker_dict[cmd[0]], project_id=proj.id,
                subproject_id='!*')
        else:
            all_tickets = redmine_obj.issue.filter(
                tracker_id=tracker_dict[cmd[0]])

        ticket_list = []
        for t in all_tickets:
            ticket_list.append("#" + str(t.id) + ": " + t.subject)

        return ticket_list

    if cmd[0] == "help":
        return [redmine_usage()]

    if cmd[0] == "listp":
        plist = []
        for project in redmine_obj.project.all():
            plist.append(project.name)

        return plist
