#!/usr/bin/python

# https://github.com/requests

import json
import re
import sys
import ssl
import pprint

######


URLPREFIX = "https://" + HOSTNAME
URLBASE = URLPREFIX + "/admin/api/v1/"

#######

# https://docs.python.org/2/library/ssl.html
# https://github.com/requests/requests/issues/2118

class filemaker_admin_cli (object):
    """Manage a FileMaker server using the FileMaker Admin Command."""
    
    JSONHEADER = {'Content-Type': 'application/json'}
    MAXMESSAGELEN = 200 # as defined in API spec
    DATETIME_REGEX = '[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}'
    
    ###  DE/CONSTRUCTORS  ##
    
    def __init__(self, hostname, user, password, usingCloud, verify_ssl=True, timeout=10.0):

        _verify_ssl = verify_ssl
        ## Set the default timeout when this becomes available, probably Requests 3.0:
        ##    https://github.com/requests/requests/pull/4560/commits/a91f34038e48652e4aefb949c532014c0b2be81d
        self._timeout = timeout
        self.login (hostname, user, password, usingCloud)
    
    def __del__(self):

        self.logout()
        self._url_prefix = None
        self._url_base = None
    
    
    ###  CONNECTION CALLS  ###
    
    #
    #  l o g i n
    #
    
    #  hostname: 
    def login (self, hostname, user, password, usingCloud, port=443):
        print "login: starting",hostname,user,password,port
        # Set up some convenience variables.
        self._url_prefix = 'https://' + hostname + ':' + str (port)
        if usingCloud:
            self._url_base = self._url_prefix + '/admin/api/v1/'
        else:
            self._url_base = self._url_prefix + '/fmi/admin/api/v1/'
        self._user_and_pass = json.dumps ({'username': user, 'password': password})
        
        return self.reconnect()
    

