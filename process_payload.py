from hooks.dump_payload                 import process_payload as dump_payload
from hooks.rubber_stamp                 import process_payload as rubber_stamp
from hooks.test_mkdocs                  import process_payload as test_mkdocs
from hooks.private_www_integration_test import process_payload as private_www_integration_test

def process_payload(payload,meta,config):
    dump_payload(payload,meta,config)
    rubber_stamp(payload,meta,config)
    test_mkdocs( payload,meta,config)
    private_www_integration_test(payload,meta,config)

if __name__=="__main__":
    process_payload({'type':'test','name':'process_payload'},{'a':1,'b':2})

