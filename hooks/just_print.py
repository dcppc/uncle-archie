"""
just_print CI Hook for Uncle Archie
"""

def process_payload(payload,meta):
    print("*"*40)
    print(payload)
    print("*"*40)
    print(meta)
    print("*"*40)
    print("\n")

if __name__=="__main__":
    process_payload({'type':'test','name':'private_www'},{'a':1,'b':2})

