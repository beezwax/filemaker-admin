#!/usr/bin/python

# https://github.com/requests

import os
import sys
import pprint


if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append (path.dirname (path.dirname (path.abspath (__file__))))
        from filemaker_admin.rest import filemaker_admin_rest
    else:
        from ..filemaker_admin.rest import filemaker_admin_rest
        
        
#######
import secrets
#######


def run_test():

     print
     print
     
     fa = filemaker_admin_rest (secrets.HOSTNAME, secrets.AUTHUSER, secrets.AUTHPASS, usingCloud=False)
     pprint.pprint (fa.list_databases(), indent=4)
     fa.logout()

     print
     print

##########
run_test()
##########
