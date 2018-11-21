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
        config = self.config
        self.payload_handler = None

    def set_payload_handler(self,handler_id,**kwargs):
        config = self.config
        self.payload_handler = PayloadHandlerFactory(
                handler_id,
                config,
                **kwargs
        )

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
config = archie.webapp.app.config
# optional modification of tests
config['private_www_build_test'] = {
        'repo_whitelist' : ['dcppc/private-www','charlesreid1/private-www']
}
app.set_payload_handler('dcppc')
app.run()

