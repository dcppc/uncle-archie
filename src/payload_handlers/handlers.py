from ..tasks import *
import pprint


class BasePayloadHandler(object):
    """
    we need a constructor
    the construct constructs each task
    we pass the config into the constructor
    that sets up each task's temp dir, name, etc.
    """
    def __init__(self,config,**kwargs):
        pass

    def process_payload(self, payload, meta, config):
        """Virtual method"""
        err = "ERROR: BasePayloadHandler: process_payload() method is "
        err += "virtual and cannot be called directly. Use a different "
        err += "PayloadHandler object that defines process_payload()."
        raise Exception(err)


class TaskPayloadHandler(BasePayloadHandler):
    def __init__(self,config,**kwargs):
        """
        Create a tasks container
        """
        self.tasks = []

    def process_payload(self, payload, meta, config):
        """
        Call the parent method (to dump the payload)
        then run all the DCPPC tasks.
        """
        # Run all tasks on the payload
        for t in self.tasks:
            t.run(payload,meta,config)


class LoggingPayloadHandler(TaskPayloadHandler):
    def __init__(self,config,**kwargs):
        """
        Create a logging task and store it in the task container
        """
        super().__init__(config,**kwargs)

        self.tasks.append(LoggingTask(config,**kwargs))


class PRTestingPayloadHandler(TaskPayloadHandler):
    def __init__(self,config,**kwargs):
        """
        Create a PR test task and store it in the task container
        """
        super().__init__(config,**kwargs)

        self.tasks.append(TestPRTask(config,**kwargs))


class MCTestingPayloadHandler(TaskPayloadHandler):
    def __init__(self,config,**kwargs):
        """
        Create a merge commit test task and store it in the task container
        """
        super().__init__(config,**kwargs)

        self.tasks.append(TestMergeCommitTask(config,**kwargs))


class NBTestingPayloadHandler(TaskPayloadHandler):
    def __init__(self,config,**kwargs):
        """
        Create a new branch test task and store it in the task container
        """
        super().__init__(config,**kwargs)

        self.tasks.append(TestNewBranchTask(config,**kwargs))


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


