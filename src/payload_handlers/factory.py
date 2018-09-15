from .handlers import \
        BasePayloadHandler, \
        DumpPayloadHandler, \
        DCPPCPayloadHandler

class PayloadHandlerFactory(object):
    payload_handlers = {
            'default': DumpPayloadHandler,
            'dcppc':   DCPPCPayloadHandler
    }
    def __init__(self,handler_type,**kwargs):
        return payload_handlers[handler_type](**kwargs)

