import unittest

class payload_handler_base(unittest.TestCase):

    def verify_in_logs(self,client,func,log_statements):
        r = func(client)
        for log_statement in log_statements:
            self.assertLogs(log_statement)
