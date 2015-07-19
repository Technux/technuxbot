#!/usr/bin/python

"""
Author: Technux
website: http://www.technux.se
mail:   support@technux.se
"""

import argparse
import os
import socket
import sys
import threading
import time
import ConfigParser

try:
    import redmine_interface
    REDMINE_MAX_RESULTS = 15
    redmine_enabled = True
except ImportError as ie:
    print "Redmine support modules not loaded (reason: %s)" % ie
    print "'pip install python-redmine' prerequisite to enable Redmine support"
    redmine_enabled = False

SOCKET_IRC = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connected_to_irc = False


def bot_setup(config_dict):
    global connected_to_irc

    technux_bot_name = config_dict['technux_bot']

    """ bot_setup() - Setup basic stuffs like nick and what channel to join"""
    SOCKET_IRC.connect((config_dict['ircserver'], 6667))
    SOCKET_IRC.send("USER " + technux_bot_name + " " + technux_bot_name +
                    " " + technux_bot_name + " :" +
                    config_dict['realname'] + "\n")
    SOCKET_IRC.send("NICK %s\n" % (technux_bot_name))

    """ Authenticate with NICKSERV if nick is registred """
    if config_dict['passwd']:
        SOCKET_IRC.send("PRIVMSG NICKSERV :IDENTIFY %s\n" %
                       (config_dict['passwd']))

    SOCKET_IRC.send("JOIN %s\n" % config_dict['channel'])
    connected_to_irc = True


def keep_alive(msg):
    """ keep_alive() - If the ircserver pings us, make sure to respond"""
    if msg.find("PING :") != -1:
        SOCKET_IRC.send("PONG :alive\n")
        return False
    else:
        return True


def send_msg(channel, nickname, msg):
    """ send_msg() - Send a PRIVMSG message to channel or channel + nick"""
    if nickname == "":
        SOCKET_IRC.send("PRIVMSG %s : %s\n" % (channel, msg))
    else:
        SOCKET_IRC.send("PRIVMSG %s :%s: %s\n" % (channel, nickname, msg))


def send_priv_msg(nickname, msg):
    """ send_priv_msg() - Send PRIVMSG message to nick """
    SOCKET_IRC.send("PRIVMSG %s :%s\n" % (nickname, msg))


def usage(channel, nick, usagemsg):
    """ usage() - Print usage for the bot"""
    send_msg(channel, nick, usagemsg)


def parse_nick(msg):
    """ parse_nick() - Parse nickname from irc msg log"""
    return msg.split('!')[0][1:]


def leave_irc_network():
    """ leave_irc_network() - Gracefully disconnect from IRC server"""

    global connected_to_irc

    if connected_to_irc is True:
        print "Sending quit"
        SOCKET_IRC.send("QUIT")


def handle_msg(ircmsg, config_dict):
    """ handle_msg() - parse and handle an irc msg"""

    if ircmsg.find("Hello %s" % config_dict['technux_bot']) != -1:
        nick = parse_nick(ircmsg)
        send_msg(config_dict['channel'], nick, config_dict['greeting'])
    elif ircmsg.find("%s: help" % (config_dict['technux_bot'])) != -1:
        nick = parse_nick(ircmsg)
        usage(config_dict['channel'], nick, config_dict['usagemsg'])
    elif ircmsg.find("%s: info" % (config_dict['technux_bot'])) != -1:
        nick = parse_nick(ircmsg)
        send_msg(config_dict['channel'], nick, config_dict['info'])
    elif ircmsg.find("%s: redmine" % (config_dict['technux_bot'])) != -1:
        nick = parse_nick(ircmsg)
        if redmine_enabled is False:
            send_msg(config_dict['channel'], nick,
                     "Redmine commands not enabled")
        else:
            index = ircmsg.find("%s: redmine" % (config_dict['technux_bot']))
            cmd = ircmsg[index:].split()
            res = redmine_interface.parse_command(cmd[2:])
            if len(res) > REDMINE_MAX_RESULTS:
                tmpmsg = "More than %d results, only sending first %d" % \
                    (REDMINE_MAX_RESULTS, REDMINE_MAX_RESULTS)
                send_priv_msg(nick, tmpmsg)
                res = res[:REDMINE_MAX_RESULTS]
            for r in res:
                for line in r.strip().split('\n'):
                    send_priv_msg(nick, line)
                    time.sleep(0.5)  # avoid flooding the IRC server


def _main():
    global redmine_enabled

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--conf', help='specify path to custom config file')
    args = parser.parse_args()

    if args.conf:
        if os.path.isfile(args.conf):
            conf_file = args.conf
        else:
            print "Specified config file %s not found!" % args.conf
            exit(64)

        if not os.access(conf_file, os.R_OK):
            print "Can't read %s!" % conf_file
            exit(65)
    else:
        conf_file = "%s/conf/bot.conf" % os.path.dirname(
            os.path.abspath(__file__))

    print "Using config file %s" % conf_file

    config = ConfigParser.ConfigParser()
    config_dict = {}
    if config.read(conf_file):
        config_dict['channel'] = config.get('settings', 'channel')
        config_dict['technux_bot'] = config.get('settings', 'botname')
        config_dict['realname'] = config.get('settings', 'realname')
        config_dict['ircserver'] = config.get('settings', 'server')
        logfile = config.get('settings', 'logfile')
        config_dict['passwd'] = config.get('settings', 'passwd')
        config_dict['greeting'] = config.get('text', 'greeting')
        config_dict['usagemsg'] = config.get('text', 'usage')
        config_dict['info'] = config.get('text', 'info')
        redmine_url = config.get('redmine', 'url')
        redmine_trackers = config.get('redmine', 'trackers')
    else:
        print "ERROR: %s could not be found!" % (conf_file)
        sys.exit(66)

    if redmine_enabled is True and redmine_url is not "":
        redmine_interface.setup(redmine_url, redmine_trackers.split(','))
    else:
        print "Redmine url not specified. " \
              "Support for redmine commands disabled"
        redmine_enabled = False

    try:
        bot_setup(config_dict)

        ''' If logfile is set, redirect console printouts to logfile'''
        if logfile:
            sys.stdout = open(logfile, 'w')

        # variables frequently accessed below
        channel = config_dict['channel']
        technux_bot = config_dict['technux_bot']

        while True:
            ircmsg = SOCKET_IRC.recv(2048)
            ircmsg = ircmsg.strip('\n\r')  # Remove linebreaks
            print(ircmsg)  # Log irc msg to console or file

            # messages from the IRC server
            if keep_alive(ircmsg) is False:
                continue

            # don't start a thread unless the msg is directed
            # to the bot by a nick
            if (ircmsg.find("PRIVMSG %s :%s: " % (channel, technux_bot)) != -1) \
            or (ircmsg.find("PRIVMSG %s :Hello %s" %
                            (channel, technux_bot)) != -1):
                t = threading.Thread(target=handle_msg,
                                     args=(ircmsg, config_dict))
                t.start()

    except KeyboardInterrupt:
        print "\n\n'Ctrl + C' detected"
    except socket.gairerror as (err, msg):
        print msg

    leave_irc_network()
    print "Exiting"

if __name__ == "__main__":
    _main()
