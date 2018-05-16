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
        
        
######

import secrets

#######

##
##   T E S T S
##

##Switch to using unittest or pyTest

def run_tests():

     fa = filemaker_admin_rest (secrets.HOSTNAME, secrets.AUTHUSER, secrets.AUTHPASS,True)
     print
     print "list_databases:"
     pprint.pprint (fa.list_databases())
     print
     print "list_database_names:"
     pprint.pprint (fa.list_database_names())
     print
     print "get_general_configuration:"
     try:
         pprint.pprint (fa.get_general_configuration())
     except:
         print "   general configuration unavialable"
     print "get_security_configuration:"
     print
     try:
         pprint.pprint (fa.get_security_configuration())
     except:
         print "   security configuration unavialable"
     print
     print "get_status:"
     try:
         pprint.pprint (fa.get_status())
     except:
         print "   status unavialable"
     print
     print "disable_schedule:"
     print "  ", fa.disable_schedule (1)
     print
     print "enable_schedule:"
     print "  ", fa.enable_schedule (1)
     print
     print "list_schedules:"
     print "  ", fa.list_schedules ()
     print
     print "pause_database:"
     print "  ", fa.pause_database (1)
     print
     print "resume_database"
     print "  ", fa.resume_database (1)
     print
     print "close_database"
     try:
         print "  ", fa.close_database(1)
     except:
         print "   could not close"
     print
     print "open_database:"
     print "  ", fa.open_database(1)
     print
     print "logout:"
     print "  ",fa.logout()


print
print "Starting"
run_tests()
print
print "Done"
