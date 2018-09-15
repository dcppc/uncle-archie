from ..tasks import 

class BasePayloadHandler(object):
    def process_payload(self, payload, meta, config):
        """Virtual method"""
        err = "ERROR: BasePayloadHandler: process_payload() method is "
        err += "virtual and cannot be called directly. Use a different "
        err += "PayloadHandler object that defines process_payload()."
        raise Exception(err)

class DumpPayloadHandler(BasePayloadHandler):
    def process_payload(self, payload, meta, config):
        """
        Process the payload using the default
        task/action: dumping the payload
        to a file.
        """
        pass

class DCPPCPayloadHandler(DumpPayloadHandler):
    def process_payload(self, payload, meta, config):
        """
        Call the parent method (to dump the payload)
        then create and run all DCPPC tasks with the
        given payload.
        """
        self.super(payload,meta,config)

        # private-www PR mkdocs build test
        t = private_www_build_test(
                repo = 'dcppc/private-www',
        )
        t.run(payload,meta,config)

        # private-www submodule integration PR mkdocs build test
        t = private_www_integration_test()
        t.run(payload,meta,config)

        # private-www submodule update PR creator
        t = private_www_build_test()
        t.run(payload,meta,config)

        # private-www commit to master heroku deployer

        # use-case-library PR mkdocs build test

        # use-case-library commit to master gh-pages deployer

        # centillion CI tests
        # 
        # uncle-archie meta-CI tests
        # 
        # private-www CI tests
        # 
        # use-case-library CI tests






