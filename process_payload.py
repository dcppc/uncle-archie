from hooks.dump_payload import process_payload as dump_payload
from hooks.rubber_stamp import process_payload as rubber_stamp

def process_payload(payload,meta,config):
    dump_payload(payload,meta,config)
    rubber_stamp(payload,meta,config)

if __name__=="__main__":
    process_payload({'type':'test','name':'process_payload'},{'a':1,'b':2})

