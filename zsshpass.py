#!/usr/bin/env python
import os
import sys
import signal
import termios
import struct
import fcntl
import pexpect
from optparse import OptionParser

SSH_NEWKEY = r'Are you sure you want to continue connecting \(yes/no\)\?'
TIMEOUT = 10
Term = None
Password = None


def sigwinch_passthrough (sig, data):
    s = struct.pack("HHHH", 0, 0, 0, 0)
    size = struct.unpack('hhhh', fcntl.ioctl(sys.stdout.fileno(),
                                             termios.TIOCGWINSZ , s))
    Term.setwinsize(size[0], size[1])


def parse_args():
    """
        Usage: zsshpass [-f|-p|-e] [-h] command parameters
           -f filename   Take password to use from file
           -p password   Provide password as argument (security unwise)
           -e            Password is passed as env-var "SSHPASS"

        At most one of -f, -p or -e should be used
    """
    usage = "zsshpass [-f|-p|-e] [-h] command parameters"
    parser = OptionParser(usage=usage, version="zsshpass 1.0")
    parser.add_option("-f", dest="filename",
                      help="Take password to use from file")
    parser.add_option("-p", dest="password",
                      help="Provide password as argument (security unwise)")
    parser.add_option("-e", dest="varname",
                      help="Password is passed as env-var \"SSHPASS\"")

    (options, args) = parser.parse_args()

    global Password
    is_set_option = False
    if options.filename and not is_set_option:
        is_set_option = True
        try:
            f = open(options.filename, "r")
            Password = f.readline()
        except IOError, e:
            print("No such file or directory")
            exit(1)
    if options.password and not is_set_option:
        is_set_option = True
        Password = options.password
    if options.varname and not is_set_option:
        is_set_option = True
        Password = os.getenv(options.varname, None)
        if not Password:
            print("Can not get pass from env-var.")
            exit(1)
    if not is_set_option:
        print("At most one of -f, -p or -e should be used")
        exit(1)
    if len(args) < 2:
        parser.print_help()
        exit(2)
    return options, args


def main(options, args):
    global Term
    Term = pexpect.spawn(" ".join(args))
    signal.signal(signal.SIGWINCH, sigwinch_passthrough)
    sigwinch_passthrough(None, None)
    i = Term.expect([pexpect.TIMEOUT, SSH_NEWKEY, '[Pp]assword:'])
    if i == 0: # Timeout
        print('ERROR!')
        print('SSH could not login. Here is what SSH said:')
        print(Term.before, Term.after)
        exit(1)
    if i == 1: # SSH does not have the public key. Just accept it.
        Term.sendline('yes')
    Term.sendline(Password)
    print(Term.before, Term.after)
    print "[PASSWORD TYPED.]"

    Term.interact()

if __name__ == '__main__':
    opt, arg =  parse_args()
    main(opt, arg)
