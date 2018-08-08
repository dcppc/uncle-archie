from hooks.just_print import process_payload as just_print

def process_payload(payload,meta):
    just_print(payload,meta)

if __name__=="__main__":
    process_payload({'type':'test','name':'process_payload'},{'a':1,'b':2})

