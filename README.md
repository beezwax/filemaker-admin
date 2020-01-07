![Beezwax Logo](https://blog.beezwax.net/wp-content/uploads/2016/01/beezwax-logo-github.png)

# FileMaker-Admin

A Python class for managing a FileMaker 17 Server or FileMaker Cloud 17 server using its REST interface. Tested against Python verison 2.7.10.

A version including support for working with the fmsadmin command line tool is planned, but not yet implemented.

## USAGE EXAMPLE

The following example will display all available database, schedule, and client information for a server.

```#!/usr/bin/python

# Used to format output & exceptions
import pprint, sys
pp = pprint.PrettyPrinter(indent=4)

####################################
hostname="hostname.domain.com"
account="youraccount"
password="serverpass"
cloudServer=True
####################################

try:
    fac = filemaker_admin_rest (hostname, account, password, usingCloud=cloudServer)
    pp.pprint (fac.list_databases())
    pp.pprint (fac.list_schedules())
    pp.pprint (fac.list_clients())
except:
    exType, exValue, exTraceback = sys.exc_info()
    print
    print "Error running script"
    print("Type : %s " % exType.__name__)
    print("Message : %s" %exValue)
    print

# If login was succesful be sure we kill session.
if 'fac' in globals():
    fac.logout()
```

=======
>>>>>>> parent of 73f6b43... added example to README
### References
* https://fmhelp.filemaker.com/docs/18/en/admin-api/
* ```/Library/FileMaker Server/Documentation/Admin API Documentation```  (macOS, on-premise)

- - -
<h6>Built by <a href="http://beezwax.net">Beezwax</a</h6>
