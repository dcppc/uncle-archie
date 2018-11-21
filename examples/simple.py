import logging
logging.basicConfig(level=logging.DEBUG)

import archie
import os
import json

from secrets import GITHUB_ACCESS_TOKEN

"""
Uncle Archie: Simple Example

This is a simple example of running the Uncle Archie
webapp after creating a Flask app, loading a config file
(specified by UNCLE_ARCHIE_CONFIG env var), and updating
the config with any additional settings.

This sets a DCPPC payload handler and simply listens for
incoming webhooks.

To run:

    $ UNCLE_ARCHIE_CONFIG="../config.py" python simple.py

"""

app = archie.webapp.get_flask_app()

app.config['DEBUG'] = True
app.config['TESTING'] = True
app.config['GITHUB_ACCESS_TOKEN'] = GITHUB_ACCESS_TOKEN

app.set_payload_handler('dcppc')

# set payload handler
app.set_payload_handler('dcppc')

# listen for incoming webhooks
app.run()

