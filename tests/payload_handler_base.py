import archie
import unittest

class payload_handler_base(unittest.TestCase):

    def doit(self,payload_handler_id,func,log_statements):
        """
        Generic pattern for running a test
        """
        app = archie.webapp.get_flask_app()
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        app.set_payload_handler(payload_handler_id)
        client = app.test_client()
        self.verify_in_logs(client,func,log_statements)
        
    def verify_in_logs(self,client,func,log_statements):
        r = func(client)
        self.assertTrue(len(log_statements)>0)
        for log_statement in log_statements:
            self.assertLogs(log_statement)
