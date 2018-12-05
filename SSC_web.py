#!/usr/bin/env python

'''----------------------------------------------------------------------------

License:

    This program is free software: you can redistribute it and/or modify
    it. This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

    If you use this software (or a part of it) in your research, please cite
    the authors. For more information how to cite this work properly please
    visit the official webside. THANKS!

                            http://ssc.sheffield.ac.uk

SSC_web.py

    The Flask framework is used to develop web applications.
    http://flask.pocoo.org

----------------------------------------------------------------------------'''

import web.framework
import datetime
import smtplib
import sys
import os

__author__ = ["Gyenge, Norbert", "Yu, Haidong"]
__email__ = ["n.g.gyenge@sheffield.ac.uk", "hyu31@sheffield.ac.uk"]


# SETUP -------------------------------------------------------------------'''

# STEP 1: Define the ip address of the server. 127.0.0.1 for local server.

ip = '143.167.2.57'

# STEP 2: Define the port. Must be integer.

port = 5000

# STEP 3: Define the path of the sql database file.
# The parameter 'default' initalises the default location of the sql database
# in the parent folder of the project
# Any other diractory can be defined, e.g., \home\user\subdir\subdir\project

directory = 'default'

# STEP 4: SSL certificate folder. If no certificate needed: SSL = False

SSL = True

# SETUP -------------------------------------------------------------------'''

# Switching off the maintenance site
if os.path.isfile('web/templates/maintenance.html') is True:
    os.rename('web/templates/maintenance.html', 'web/templates/maintenance_off.html')

try:

    # Start the Flask server
    web.framework.start(ip, port, directory, SSL)

except:

    # Do not send email if KeyboardInterrupt()
    if "KeyboardInterrupt()" not in str(sys.exc_info()):

        # Send an email if server fails 
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("sheffield.solar.catalogue@gmail.com", "sscerror1234")
 
        # Compose the email
        SUBJECT = "SSC Server failed at " + str(datetime.datetime.now())

        TO = "n.g.gyenge@sheffield.ac.uk"

        FROM = "sheffield.solar.catalogue@gmail.com"

        text1 = "Dear SSC Admins,\n\n" 
        text2 = "The SSC server is terminated due an unexpected error:\n\n" 
        text3 = str(sys.exc_info()) + "\n" + str(datetime.datetime.now()) 
        text4 = "\n\n SSC Web Service"

        BODY = "\r\n".join(["From: %s" % FROM, "To: %s" % __email__[0],
                            "Subject: %s" % SUBJECT , "", text1+text2+text3+text4])

        server.sendmail(FROM, __email__[0], BODY)
        server.quit()

    # Maintenance page activation
    os.rename('web/templates/maintenance_off.html', 'web/templates/maintenance.html')



