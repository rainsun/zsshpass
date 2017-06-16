#!/usr/bin/env python
import os
import pexpect
from optparse import OptionParser

SSH_NEWKEY = r'Are you sure you want to continue connecting \(yes/no\)\?'
TIMEOUT = 10


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

isSetOption = False
if options.filename and not isSetOption:
    isSetOption = True
    try:
        f = open(options.filename, "r")
        password = f.readline()
    except IOError, e:
        print("No such file or directory")
        exit(1)
if options.password and not isSetOption:
    isSetOption = True
    password = options.password
if options.varname and not isSetOption:
    isSetOption = True
    password = os.getenv(options.varname, None)
    if not password:
        print("Can not get pass from env-var.")
        exit(1)
if not isSetOption:
    print("At most one of -f, -p or -e should be used")
    exit(1)
if len(args) < 2:
    parser.print_help()
    exit(2)


child = pexpect.spawn(" ".join(args))
i = child.expect([pexpect.TIMEOUT, SSH_NEWKEY, '[Pp]assword:'])
if i == 0: # Timeout
    print('ERROR!')
    print('SSH could not login. Here is what SSH said:')
    print(child.before, child.after)
    exit(1)
if i == 1: # SSH does not have the public key. Just accept it.
    child.sendline('yes')
child.sendline(password)
print(child.before, child.after)
print "[PASSWORD TYPED.]"


child.interact()