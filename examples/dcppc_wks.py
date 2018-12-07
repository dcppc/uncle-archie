import archie
import logging
import os
import json

from secrets import GITHUB_ACCESS_TOKEN

# logging stuff
logging.basicConfig(level=logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
annoying = logging.getLogger('urllib3.connectionpool')
annoying.disabled=True

# archie app
app = archie.webapp.get_flask_app()
app.config['DEBUG'] = True
app.config['GITHUB_ACCESS_TOKEN'] = GITHUB_ACCESS_TOKEN
app.set_payload_handler('dcppc')

# archie test client
client = app.test_client()


############################
# workshops

logging.debug("-"*40)
logging.debug("sync")
r = archie.tests.dcppc_workshops_sync(client)

logging.debug("-"*40)
logging.debug("closed (merged)")
r = archie.tests.dcppc_workshops_closed_merged(client)

logging.debug("-"*40)
logging.debug("closed (unmerged)")
r = archie.tests.dcppc_workshops_closed_unmerged(client)

logging.debug("-"*40)
logging.debug("push")
r = archie.tests.dcppc_workshops_push(client)

