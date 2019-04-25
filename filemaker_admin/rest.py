#!/usr/bin/python

# https://github.com/requests

import json
import re
import sys
import ssl
import requests
import pprint

######

# https://docs.python.org/2/library/ssl.html
# https://github.com/requests/requests/issues/2118
# http://docs.python-requests.org/en/master/user/advanced/#session-objects
# https://fmhelp.filemaker.com/cloud/17/en/adminapi/index.html

# CLOUD
#   Admin: gateway/lib/fmsadminapi/apis/
#   Data: Web Publishing/publishing-engine/node-wip/routes/api.js

#from requests_ntlm import HttpNtlmAuth
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

# This is the 2.11 Requests cipher string.
CIPHERS = (
    'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
    'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:'
    '!eNULL:!MD5'
)

requests.packages.urllib3.disable_warnings()

class Ssl3HttpAdapter(HTTPAdapter):
    """"Transport adapter" that allows us to use SSLv3."""

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_version=ssl.PROTOCOL_TLSv1_1)
#            block=block, ssl_version=ssl.PROTOCOL_SSLv3)

class DESAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False,*args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_version=ssl.PROTOCOL_SSLv3,*args, **kwargs)

#######


class filemaker_admin_rest (object):
    """Manage a FileMaker server using the FileMaker Admin API."""
    
    JSONHEADER = {'Content-Type': 'application/json'}
    MAXMESSAGELEN = 200 # as defined in API spec
    DATETIME_REGEX = '[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}'

    
    ###  DE/CONSTRUCTORS  ##
    
    def __init__(self, hostname, user, password, usingCloud=False, port=443, verify_ssl=True, timeout=10.0):

        _verify_ssl = verify_ssl
        ## Set the default timeout when this becomes available, probably Requests 3.0:
        ##    https://github.com/requests/requests/pull/4560/commits/a91f34038e48652e4aefb949c532014c0b2be81d
        self._timeout = timeout
        self.login (hostname, user, password, usingCloud)
    
    def __del__(self):

        self.logout()
        self._url_prefix = None
        self._url_base = None
    
    ##
    ##   C O N N E C T I O N   C A L L S
    ##
    
    #
    #  l o g i n
    #
    
    #  hostname: 
    def login (self, hostname, user, password, usingCloud=False, port=443):
        
        # Set up some convenience variables.
        self._url_prefix = 'https://' + hostname + ':' + str (port)
        if usingCloud:
            self._url_base = self._url_prefix + '/admin/api/v1/'
        else:
            self._url_base = self._url_prefix + '/fmi/admin/api/v1/'
        self._user_and_pass = json.dumps ({'username': user, 'password': password})
        
        return self.reconnect()
    
    #
    #  r e c o n n e c t
    #
    
    def reconnect (self):
        # _user_and_pass should already have credential info from login call.
        
        # Session used for all subsequent access.
        self._session = requests.Session()

        # HttpAdapter can be used for some unusual SSL/TLS requirement.
        #session.mount(URL_prefix, Ssl3HttpAdapter())
        response = self._session.post(
            self._url_base + 'user/login',
            headers=self.JSONHEADER,
            data=self._user_and_pass,
            timeout=self._timeout )    
        print response.text
        response.raise_for_status()

        # Create a new header that includes our token for later use.
        # Starting with 17 we also need to include Content-Length: 0 for PUT/POSTs with no data.
        self._GET_header = dict (self.JSONHEADER)
        self._GET_header ['Authorization'] = 'Bearer ' + response.json()['token']
        self._PUT0_header = dict (self._GET_header)
        self._PUT0_header ['Content-Length'] = '0'
        return response.json()['result']
    
    #
    #  l o g o u t
    #
    
    def logout (self):
        response = None
        try:
            if self._session != None:
                # Close remote connection.
                response = self._session.post(self._url_base + 'user/logout', headers=self._GET_header, timeout=self._timeout)
        except NameError, AttributeError:
            pass
        
        self._session = None
        
        # We'll leave instance values intact in case of reconnect.
        if response != None:
            return response.json()['result']
        else:
            return None
    
    #
    #   D A T A B A S E   A C C E S S
    #
    
    #
    #  l i s t _ d a t a b a s e s
    #
    
    def list_databases (self):
        response = self._session.get(self._url_base + 'databases', headers=self._GET_header, timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    #
    #  l i s t _ d a t a b a s e _ n a m e s
    #
    
    def list_database_names (self):
    	# Files are nested inside of files?!
    	file_list = self.list_databases()['files']['files']
    	# Return stripped version with just file names.
    	print "file_list:", file_list
    	return map (lambda fi: fi['filename'], file_list)

    #
    #  o p e n _ d a t a b a s e
    #
    
    #  database_id: ID as returned by list_databases, or 0 to open all
    #  passphrase: the EAR (Encryption At Rest) password (optional)
    
    def open_database (self, database_id, passphrase=None):
                
        if passphrase!=None:
            pass_data = {'key': passphrase}
            response = self._session.put (self._url_base + 'databases/' + str(database_id) + '/open', data=pass_data, timeout=self._timeout)
        else:
            response = self._session.put (self._url_base + 'databases/' + str(database_id) + '/open', headers=self._PUT0_header, timeout=self._timeout)
    
        response.raise_for_status()
        return response.json()['result']
    
    #
    #  c l o s e _ d a t a b a s e 
    #
    
    #  database_id: ID as returned by list_databases, or 0 to open all
    #  message: text message to send to users (optional)
    
    def close_database (self, database_id, message=None):
        if message != None:
            message_data = {'message': message [:self.MAXMESSAGELEN]}
            response = self._session.put (
                self._url_base + 'databases/' + str(database_id) + '/close',
                data=message_data,
                timeout=self._timeout )
        else:
            response = self._session.put (self._url_base + 'databases/' + str(database_id) + '/close',
                headers=self._PUT0_header,
                timeout=self._timeout)
        
        response.raise_for_status()
        return response.json()['result']
    
    #
    #  p a u s e _ d a t a b a s e
    #
    
    #  database_id: ID as returned by list_databases, or 0 to pause all
    
    def pause_database (self, database_id):
        
        response = self._session.put (self._url_base + 'databases/' + str(database_id) + '/pause',
            headers=self._PUT0_header,
            timeout=self._timeout )
        response.raise_for_status()
        return response.json()['result']

    #
    #  r e s u m e _ d a t a b a s e
    #
    
    #  database_id: ID as returned by list_databases, or 0 to resume all
    
    def resume_database (self, database_id):
        
        response = self._session.put (self._url_base + 'databases/' + str(database_id) + '/resume',
            headers=self._PUT0_header,
            timeout=self._timeout )
        response.raise_for_status()
        return response.json()['result']
    
    ##
    ##   U S E R S
    ##
    
    #
    #  d i s c o n n e c t _ u s e r
    #
    
    def disconnect_user (self, client_id, message=None, gracetime=None):

        du_data = {}
        
        if message != None:
            du_data ['message'] = message [:self.MAXMESSAGELEN]
        if gracetime != None:
            ## if gracetime is a float round up?
            du_data ['gracetime'] = int (gracetime)

        if du_data == {}:
            response = self._session.put (_url_base + str(database_id) + '/close', headers=PUT0_header, timeout=_timeout)
        else:
            response = self._session.put (_url_base + str(database_id) + '/close', data=du_data, timeout=_timeout)
        
        response.raise_for_status()
        return response.json()['result']

    #
    #  s e n d _ m e s s a g e
    #
    
    def send_message (self, client_id, message=None):

        sm_data = {}
        
        if message != None:
            sm_data = {'message': message[:self.MAXMESSAGELEN]}

        response = self._session.put (self._url_base + 'clients/' + int (client_id) + '/message', data=sm_data, timeout=self._timeout)
        
        response.raise_for_status()
        return response.json()['result']

    ##
    ##   S E R V E R   M A N A G E M E N T
    ##
    
    #
    #  g e t _ g e n e r a l _ c o n f i g u r a t i o n
    #
    
    #  Not available in FMC 16
    
    def get_general_configuration (self):
    
        response = self._session.get(
            self._url_base + 'server/config/general',
            headers=self._GET_header,
            timeout=self._timeout )
        response.raise_for_status()
        return result.json()

    #
    #  g e t _ s e c u r i t y _ c o n f i g u r a t i o n
    #
    
    #  Not available in FMC
    
    def get_security_configuration (self):
    
        response = self._session.get(self._url_base + 'server/config/security', headers=self._GET_header, timeout=self._timeout)
        response.raise_for_status()
        return result.json()['requireSecureDB']

    #
    #  g e t _ s t a t u s
    #
    
    #  Not available in FMC
    
    def get_status (self):
    
        response = self._session.get(
            self._url_base + 'server/server/status',
            headers=self._GET_header,
            timeout=self._timeout )
        response.raise_for_status()
        return result.json()['running']

    ##
    ##   S C H E D U L E S
    ##

    #
    #  c r e a t e _ m e s s a g e _ s c h e d u l e
    #
    
    # Parameters
    #  frequency: 1 = Once Only, 2 = Daily or Every n Days, 3 = Weekly
    #  target: 2 - all databases, 3 - some databases under a subfolder, 4 - single database
    #  from_target: (target=3) folder path, (target=4) database name  (optional)
    #  repeat: False to only run once (overrides end, frequency)  (optional)
    #  repeat_interval: 1 for minute, 2 for hour  (optional)
    #  repeat_frequency: 1 to 60 when repeatInterval = 1 or from 1 to 24 when repeatInterval=2  (optional)
    #  days_of_week: 7-digit binary string, each digit's 1 or 0 represents on or off for the corresponding day of the week  (optional)
    #  daily_days: how many days between runs of schedule  (OPTIONAL)
    #  enable_end_date: use end date/time for schedule
    #  end_date: Schedule end date/time
    #  send_email: True to send email on schedule comppletion
    #  email_addresses: Email addresses separated by comma
    #  enabled: True if schedule enabled
    
    def create_message_schedule (self, name, frequency, start_date, target, message, from_target=None, repeat=True, repeat_interval=2, repeat_frequency=24,days_of_week=None, daily_days=1, enable_end_date=None, end_date=None, send_email=None, email_addresses=None, enabled=True):
        
        # Due to the number of possible parameters, will step through parameters to build request.
        
        # First the required parameters.
        # Validate date format, throws exception if no match.
        re.match(self.DATETIME_REGEX).group(0)
        cms_params = {
           'taskType': 3,
           'name': str (name),
           'freqType': int (frequency),
           'startDate': start_date,
           'target': target,
           'message': str (message)
        }
        
        if from_target:
            cms_params['fromTarget'] = int (from_target)

        if repeat:
            cms_params['repeatTask'] = bool (repeat)

        if repeat_interval:
            cms_params['repeatInterval'] = int (repeat_interval)
        
        if repeat_frequency:
            cms_params['repeatFrequency'] = int (repeat_frequency)
        
        if days_of_week:
            cms_params['daysOfTheWeek'] = str (days_of_week)
        
        if daily_days:
            cms_params['dailyDays'] = int (daily_days)
        
        if enable_end_date:
            cms_params['enableEndDate'] = bool (enable_end_date)
        
        if end_date:
            re.match(self.DATETIME_REGEX, end_date).group(0)
            cms_params['endDate'] = end_date
        
        if send_email:
            cms_params['sendEmail'] = bool (send_email)
        
        if email_addresses:
            cms_params['emailAddresses'] = str (email_addresses)
        
        if enabled:
            cms_params['enabled'] = enabled
            
        response = self._session.put (
            self._url_base + 'schedules/' + str(schedule_id) + '/disable',
            headers=self._GET_header,
            data=cms_params,
            timeout=self._timeout )
        
        response.raise_for_status()
        return response.json()['schedules']

    #
    #  d i s a b l e _ s c h e d u l e
    #
    
    #  schedule_id: ID as returned by list_schedules
    
    # Will return an exception if the schedule # does not exist:
    #    requests.exceptions.HTTPError: 477 Client Error: unknown for url
    
    def disable_schedule (self, schedule_id):
        
        response = self._session.put (
            self._url_base + 'schedules/' + str(schedule_id) + '/disable',
            headers=self._PUT0_header,
            timeout=self._timeout )
        response.raise_for_status()
        return response.json()

    #
    #  d u p l i c a t e _ s c h e d u l e
    #

    #  schedule_id: ID as returned by list_schedules
    
    def duplicate_schedule (self, schedule_id):
        
        response = self._session.put (
            self._url_base + 'schedules/' + str(schedule_id) + '/duplicate',
            headers=self._PUT0_header,
            timeout=self._timeout )
        response.raise_for_status()
        return response.json()['schedule']

    #
    #  e n a b l e _ s c h e d u l e
    #
    
    #  schedule_id: ID as returned by list_schedules
    
    def enable_schedule (self, schedule_id):
        
        response = self._session.put (
            self._url_base + 'schedules/' + str(schedule_id) + '/enable',
            headers=self._PUT0_header,
            timeout=self._timeout )
        response.raise_for_status()
        return response.json()['schedules']

    #
    #  g e t _ s c h e d u l e
    #
    
    #  schedule_id: ID as returned by list_schedules
    
    def run_schedule (self, schedule_id):
        
        response = self._session.put (
            self._url_base + 'schedules/' + str(schedule_id),
            headers=self._PUT0_header,
            timeout=self._timeout )
        response.raise_for_status()
        return response.json()['schedule']

    #
    #  l i s t _ s c h e d u l e s
    #
    
    def list_schedules(self):
    
        response = self._session.get(self._url_base + 'schedules', headers=self._GET_header, timeout=self._timeout)
        response.raise_for_status()
        return response.json()['schedules']

    #
    #  r u n _ s c h e d u l e
    #
    
    #  database_id: ID as returned by list_databases, or 0 to resume all
    
    def run_schedule (self, schedule_id):
        
        response = self._session.put (
            self._url_base + 'schedules/' + str(schedule_id) + '/run',
            headers=self._PUT0_header,
            timeout=self._timeout )
        response.raise_for_status()
        return response.json()['schedule']

    #
    #  s e t _ s c h e d u l e _ c r e d e n t i a l s
    #
    
    #  schedule_id: ID as returned by list_schedules
    
    def set_schedule_credentials (self, schedule_id, account, password):
        
        # We need to specify all required parameters if even just modifying the credentials,
        # so we'll first get the current settings.
        response = self._session.get(self._url_base + 'schedules/' + str(schedule_id), headers=self._GET_header, timeout=self._timeout)
        response.raise_for_status()
        cur_sched = response.json()['schedules']
        
        # Flatten the keys (a difference between getting & setting schedules).
        sched_script_items = cur_sched[0]['filemakerScriptType']
        del cur_sched[0]['filemakerScriptType']
        sched_script_items = cur_sched[0].update (sched_script_items)
        
        # Remove everything but required values.
        required_sched_keys = ['taskType','name','startDate','freqType','filemakerScriptType','fromTarget','fmScriptName','fmScriptAccount','fmScriptPassword']
        #required_script_keys = ['fromTarget', 'fmScriptName', 'fmScriptAccount', 'fmScriptPassword']
        unwanted = set(cur_sched[0]) - set (required_sched_keys)
        for unwanted_key in unwanted:
           del cur_sched[0][unwanted_key]
        
        # Set the two values to be changed.
        cur_sched[0]['fmScriptAccount'] = account
        cur_sched[0]['fmScriptPassword'] = password
        
        response = self._session.put (
            self._url_base + 'schedules/' + str(schedule_id),
            data=cur_sched,
            timeout=self._timeout )
        response.raise_for_status()
        return response.json()['schedules']



	##
	##   P H P
	##
	
    #
    #  g e t _ p h p _ c o n f i g u r a t i o n
    #
    
    #  Not available in FMC
    
    def get_php_configuration (self):
    
        response = self._session.get(self._url_base + 'php/config', headers=self._GET_header, timeout=self._timeout)
        response.raise_for_status()
        return result.json()

    #
    #  s e t _ p h p _ c o n f i g
    #

    #  enable_flag: True to enable the PHP interface

    #  Not available in FMC
    
    
    def set_php_config (self, enable_flag):
        
        spc_data = {'enabled': bool (enable_flag))
        
        response = self._session.patch (
            self._url_base + 'php/config',
            headers=self._GET_header,
            timeout=self._timeout )
        response.raise_for_status()
        return response.json()['result']



    ##
    ##   X M L
    ##

    #
    #  g e t _ x m l _ c o n f i g u r a t i o n
    #
    
    #  Not available in FMC
    
    def get_xml_configuration (self):
    
        response = self._session.get(self._url_base + 'xml/config', headers=self._GET_header, timeout=self._timeout)
        response.raise_for_status()
        return result.json()['enabled']


    #
    #  s e t _ x m l _ c o n f i g
    #

    #  enable_flag: True to enable the XML interface

    #  Not available in FMC
    
    
    def set_xml_config (self, enable_flag):
        
        sxc_data = {'enabled': bool (enable_flag))
        
        response = self._session.patch (
            self._url_base + 'xml/config',
            headers=self._GET_header,
            timeout=self._timeout )
        response.raise_for_status()
        return response.json()['result']
