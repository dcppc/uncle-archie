import json, os, re
"""
Dump Payload CI Hook for Uncle Archie
"""

def process_payload(payload,meta,config):

    from datetime import datetime
    fname = datetime.now().isoformat()
    with open('/tmp/archie/dump_payload_%s'%(fname),'w') as f:
        f.write(json.dumps(payload,indent=4))

if __name__=="__main__":
    process_payload({'type':'test','name':'private_www'},{'a':1,'b':2})

