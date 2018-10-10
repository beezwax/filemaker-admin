#!/usr/bin/python

import json
import re
import subprocess
import sys
import pprint


######

URLPREFIX = "https://" + HOSTNAME
URLBASE = URLPREFIX + "/admin/api/v1/"

#######


# https://docs.python.org/2/library/subprocess.html

class filemaker_admin_cli (object):
    """Manage a FileMaker server using the FileMaker Admin Command."""
    
    MAXMESSAGELEN = 200 # as defined in API spec
    DATETIME_REGEX = '[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}'
    
    ###  DE/CONSTRUCTORS  ##
    
    def __init__(self, user, password):

        self._fmsadmin_path = '/usr/local/bin/fmsadmin'
        
        ## Set the default timeout when this becomes available, probably Requests 3.0:
        ##    https://github.com/requests/requests/pull/4560/commits/a91f34038e48652e4aefb949c532014c0b2be81d
        self._timeout = timeout
        self.login (hostname, user, password, usingCloud)
    
    def __del__(self):

        self.logout()
        self._url_prefix = None
        self._url_base = None
    
    
    ###  COMMANDS  ###
    
    # subprocess.check_output(args, *, stdin=None, stderr=None, shell=False, universal_newlines=False)
    
    #
    #  s t o p
    #
    
    #  hostname: 
    def stop (self, user, password, process, force=False, message=None, seconds=None):
    
        response = subprocess.check_output (self._fmsadmin_path, '-y', 'stop', process)

    #
    #  s t a r t
    #
    
    # process: possible values are 'ADMINSERVER', 'SERVER', 'FMSE', 'FMSIB', 'XDBC', 'WPE', 'FMDAPI'
    # OS account running command should be a member of fmsadmin group.
    
    def start (self, user, password, process):
    
        response = subprocess.check_output (self._fmsadmin_path, 'start', process)
        
        return response
    
    
    def status_client (self, user, password, client_id=None):
    
        pass
    
    def status_file (self, user, password, file_name=None):
    
        pass

    def status_file (self, user, password, file_reference=None):
    
        pass
    
    
