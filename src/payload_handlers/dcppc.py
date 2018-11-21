from .handlers import LoggingPayloadHandler

from ..tasks import *
import pprint

class DCPPCPayloadHandler(LoggingPayloadHandler):
    """
    The DCPPC Payload Handler handles payloads
    by running all available DCPPC Tasks on 
    each payload it receives.
    """
    def __init__(self,config,**kwargs):
        """
        Create all DCPPC tasks and store them in the task container
        """
        super().__init__(config,**kwargs)

        ## private www PR builder
        self.tasks.append(private_www_PR_builder(config,**kwargs))

        ### private www submodule integration PR builder
        #self.tasks.append(private_www_submodule_integration_PR_builder(config))

        ### private www submodule update PR opener
        #self.tasks.append(private_www_submodule_update_PR_opener(config))

        ### private www (heroku) deployer
        #self.tasks.append(private_www_deployer(config))

        ### use case library PR builder
        #self.tasks.append(use_case_library_PR_builder(config))

        ### use case library (gh-pages) deployer
        #self.tasks.append(use_case_library_deployer(config))

        # centillion CI tasks
        # 
        # uncle-archie meta-CI tasks
        # 
        # private-www CI tasks
        # 
        # use-case-library CI tasks


