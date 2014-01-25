"""
Author: Technux
webste: http://www.technux.se
mail:   support@technux.se
"""
#!/usr/bin/python

import os
import socket
import sys
import ConfigParser

SOCKET_IRC = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def bot_setup(ircserver, channel, technux_bot, passwd):
    """ bot_setup() - Setup basic stuffs like nick and what channel to join"""
    SOCKET_IRC.connect((ircserver, 6667))
    SOCKET_IRC.send("USER " + technux_bot + " " + technux_bot + \
                   " " + technux_bot + " :Technux irc bot\n")
    SOCKET_IRC.send("NICK %s\n" % (technux_bot))

    """ Authenticate with NICKSERV if nick is registred """
    if passwd:
        SOCKET_IRC.send("PRIVMSG NICKSERV :IDENTIFY %s\n" % (passwd))

    SOCKET_IRC.send("JOIN %s\n" % (channel))


def keep_alive(msg):
    """ keep_alive() - If the ircserver ping us, make sure to respond"""
    if msg.find("PING :") != -1:
        SOCKET_IRC.send("PONG :alive\n")


def send_msg(channel, nickname, msg):
    """ send_msg() - Send a PRIVMSG message to channel or channel and nick"""
    if nickname == "":
        SOCKET_IRC.send("PRIVMSG %s : %s\n" % (channel, msg))
    else:
        SOCKET_IRC.send("PRIVMSG %s :%s: %s\n" % (channel, nickname, msg))


def usage(channel, nick, usagemsg):
    """ usage() - Print usage for the bot"""
    send_msg(channel, nick, usagemsg)


def parse_nick(msg):
    """ parse_nick() - Parse nickname from irc msg log"""
    return msg.split('!')[0][1:]


def _main():

    conf_file = ("%s/conf/bot.conf" %
                (os.path.dirname(os.path.abspath(__file__))))
    config = ConfigParser.ConfigParser()
    if config.read(conf_file):
        channel = config.get('settings', 'channel')
        technux_bot = config.get('settings', 'botname')
        ircserver = config.get('settings', 'server')
        logfile = config.get('settings', 'logfile')
        passwd = config.get('settings', 'passwd')
        greeting = config.get('text', 'greeting')
        usagemsg = config.get('text', 'usage')
        info = config.get('text', 'info')
    else:
        print "ERROR: %s could not be found!" % (conf_file)
        sys.exit(66)

    bot_setup(ircserver, channel, technux_bot, passwd)

    ''' If logfile is set, redirect console printouts to logfile'''
    if logfile:
        sys.stdout = open(logfile, 'w')

    while True:
        ircmsg = SOCKET_IRC.recv(2048)
        ircmsg = ircmsg.strip('\n\r') # Remove linebreaks
        print(ircmsg) # Log irc msg to console or file

        if ircmsg.find(":Hello %s" % technux_bot) != -1:
            nick = parse_nick(ircmsg)
            send_msg(channel, nick, greeting)
        elif ircmsg.find("%s: help" % (technux_bot)) != -1:
            nick = parse_nick(ircmsg)
            usage(channel, nick, usagemsg)
        elif ircmsg.find("%s: info" % (technux_bot)) != -1:
            nick = parse_nick(ircmsg)
            send_msg(channel, nick, info)

        keep_alive(ircmsg)

if __name__ == "__main__":
    _main()