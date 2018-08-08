"""
private-www CI Hook for Uncle Archie

This script is a continuous integration hook for 
Uncle Archie. This function is called with all 
received webhooks, so it must use payload and meta
to determin when to run.

payload and meta are JSON containers with info about
the repository in them.
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

