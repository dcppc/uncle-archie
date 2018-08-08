from hooks.private_www import process_payload as private_www

def process_payload(payload,meta):
    private_www(payload,meta)

if __name__=="__main__":
    process_payload({'type':'test','name':'process_payload'},{'a':1,'b':2})

