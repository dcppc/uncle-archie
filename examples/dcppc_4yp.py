import archie
import logging
import os
import json

from secrets import GITHUB_ACCESS_TOKEN

logging.basicConfig(level=logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
annoying = logging.getLogger('urllib3.connectionpool')
annoying.disabled=True

app = archie.webapp.get_flask_app()

app.config['DEBUG'] = True
app.config['GITHUB_ACCESS_TOKEN'] = GITHUB_ACCESS_TOKEN

client = app.test_client()

app.set_payload_handler('dcppc')


############################
# 4yp

logging.debug("-"*40)
logging.debug("sync")
r = archie.tests.dcppc_4yp_sync(client)

logging.debug("-"*40)
logging.debug("closed (merged)")
r = archie.tests.dcppc_4yp_closed_merged(client)

logging.debug("-"*40)
logging.debug("closed (unmerged)")
r = archie.tests.dcppc_4yp_closed_unmerged(client)

logging.debug("-"*40)
logging.debug("push")
r = archie.tests.dcppc_4yp_push(client)

