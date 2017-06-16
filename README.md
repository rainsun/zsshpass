    Usage: zsshpass [-f|-p|-e] [-h] command parameters
       -f filename   Take password to use from file
       -p password   Provide password as argument (security unwise)
       -e            Password is passed as env-var "SSHPASS"
     
    At most one of -f, -p or -e should be used