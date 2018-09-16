from .handlers import \
        BasePayloadHandler, \
        DumpPayloadHandler, \
        DCPPCPayloadHandler


class PayloadHandlerFactory(object):
    payload_handlers = {
            'default': DumpPayloadHandler,
            'dcppc':   DCPPCPayloadHandler
    }
    def factory(self,handler_type,config,**kwargs):
        if handler_type in self.payload_handlers.keys():
            return self.payload_handlers[handler_type](config,**kwargs)
        else:
            err = "ERROR: PayloadHandlerFactory: factory(): "
            err += "Received an invalid handler type \"%s\"\n"%handler_type
            err += "Handler type must be one of: %s"%(", ".join(self.payload_handlers.keys()))
            raise Exception(err)

