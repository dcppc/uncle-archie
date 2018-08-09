"""
just_print CI Hook for Uncle Archie
"""

def process_payload(payload,meta):
    from datetime import datetime
    fname = datetime.now().isoformat()
    with open('/tmp/%s'%(fname),'w') as f:
        f.write(json.dumps(payload,indent=4))

if __name__=="__main__":
    process_payload({'type':'test','name':'private_www'},{'a':1,'b':2})

