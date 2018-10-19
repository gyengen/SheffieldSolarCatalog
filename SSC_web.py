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

                            www.ssc.sheffield.ac.uk

SSC_web.py

    The Flask framework is used to develop web applications.
    http://flask.pocoo.org

----------------------------------------------------------------------------'''

import web.framework


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

# STEP 4: SSL certificate folder. If no certificate needed: SSL = FALSE

SSL = True

# SETUP -------------------------------------------------------------------'''

# Start the Flask server
web.framework.start(ip, port, directory, SSL)
