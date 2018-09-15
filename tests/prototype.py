import archie

exit(1)


################################
# in payload handler factory:

payload_handlers = {
        'default': DefaultPayloadHandler,
        'dcppc':   DCPPCPayloadHandler
}

def create_payload_handler(self,handler_type):        
    return payload_handlers[handler_type]()



################################
# in archie flask webapp:

class UAFlask(Flask):
    def __init__(self,**kwargs):
        self.super(**kwargs)
        self.payload_handler = PayloadHandlerFactory('default')

    def set_payload_handler(self,handler_id):
        self.payload_handler = PayloadHandlerFactory(handler_id)

    def get_payload_handler(self,):
        return self.payload_handler

#...


@app.route('/webhook')
def webhook():
    ...
    payload_handler = app.get_payload_handler()
    payload_handler.process_payload(payload, meta, config)



################################
# meanwhile...

app = archie.webapp.app
app.set_payload_handler('dcppc')
app.run()

