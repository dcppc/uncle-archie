from ..tasks import 

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

class DumpPayloadHandler(BasePayloadHandler):
    def __init__(self,config,**kwargs):
        pass
    def process_payload(self, payload, meta, config):
        """
        Process the payload using the default
        task/action: dumping the payload
        to a file.
        """
        pass

class DCPPCPayloadHandler(DumpPayloadHandler):
    def __init__(self,config,**kwargs):
        """
        Create all tests and store them in a container
        """
        tests = []

        ## private www PR builder
        tests.append(private_www_pr_builder(config))

        ## private www submodule integration PR builder
        tests.append(private_www_submodule_integration_PR_builder(config))

        ## private www submodule update PR opener
        tests.append(private_www_submodule_update_PR_opener(config))

        ## private www (heroku) deployer
        tests.append(private_www_deployer(config))

        ## use case library PR builder
        tests.append(use_case_library_PR_builder(config))

        ## use case library (gh-pages) deployer
        tests.append(use_case_library_deployer(config))

        # centillion CI tests
        # 
        # uncle-archie meta-CI tests
        # 
        # private-www CI tests
        # 
        # use-case-library CI tests


    def process_payload(self, payload, meta, config):
        """
        Call the parent method (to dump the payload)
        then run all the DCPPC tasks.
        """
        # Dump payload
        self.super(payload,meta,config)

        t.run(payload,meta,config)

        t.run(payload,meta,config)

        t.run(payload,meta,config)






