from .handlers import \
        BasePayloadHandler, \
        DefaultPayloadHandler, \
        DCPPCPayloadHandler

class PayloadHandlerFactory(object):
    payload_handlers = {
            'default': DefaultPayloadHandler,
            'dcppc':   DCPPCPayloadHandler
    }
    def __init__(self,handler_type,**kwargs):
        return payload_handlers[handler_type](**kwargs)

