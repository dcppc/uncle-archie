import logging
logging.basicConfig(level=logging.DEBUG)

import archie
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
#app.config['TESTING'] = True
app.config['GITHUB_ACCESS_TOKEN'] = GITHUB_ACCESS_TOKEN

client = app.test_client()

app.set_payload_handler('dcppc')



logging.debug("-"*40)
logging.debug("sync")
r = archie.tests.dcppc_private_www_sync(client)

logging.debug("-"*40)
logging.debug("closed (merged)")
r = archie.tests.dcppc_private_www_closed_merged(client)

### logging.debug("-"*40)
### logging.debug("closed (unmerged)")
### r = archie.tests.dcppc_private_www_closed_unmerged(client)
### 
### logging.debug("-"*40)
### logging.debug("push")
### r = archie.tests.dcppc_private_www_push(client)


############################


#logging.debug("-"*40)
#logging.debug("post_pr_opened(client)")
#r = archie.tests.post_pr_opened(client)
#
#logging.debug("-"*40)
#logging.debug("post_pr_closed_merged(client)")
#r = archie.tests.post_pr_closed_merged(client)
#
#logging.debug("-"*40)
#logging.debug("post_pr_closed_unmerged(client)")
#r = archie.tests.post_pr_closed_unmerged(client)
#
#logging.debug("-"*40)
#logging.debug("post_pr_sync(client)")
#r = archie.tests.post_pr_sync(client)

