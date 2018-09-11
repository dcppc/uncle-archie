
class DumpPayloadTask(GithubTask):
    """
    The simplest possible Github task:
    this task just dumps out the payload
    received from Github to a file.

    This doesn't use any features like
    htdocs hosting of the output file
    or assembling a permanent link.
    """
    def process_payload(self,payload):
        """
        Just save every webhook payload
        """
        # This is going to be called by every function
        # If you want to filter when you dump the payload,
        # do it here.
        msg = "DumpPayloadTask: process_payload(): Saving webhook payload"
        logging.debug(msg)

        self.save_payload(payload)

