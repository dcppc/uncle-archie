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


class PRBuildPayloadHandler(TaskPayloadHandler):
    def __init__(self,config,**kwargs):
        """
        Create a PR build task and store it in the task container
        """
        super().__init__(config,**kwargs)

        self.tasks.append(BuildPRTask(config,**kwargs))


