from .handlers import \
        BasePayloadHandler, \
        PRTestingPayloadHandler, \
        LoggingPayloadHandler

from .dcppc import DCPPCPayloadHandler


class PayloadHandlerFactory(object):
    """
    Given the string name of a payload handler,
    the factory returns an instance of that
    payload handler.
    """
    payload_handlers = {
            'default': LoggingPayloadHandler,
            'pr_test': PRTestingPayloadHandler,
            'dcppc':   DCPPCPayloadHandler
    }

    def factory(self,handler_type,config,**kwargs):
        """
        Given a payload handler type 
        (must be key in dictionary above),
        create and return an instance of it.
        """
        if handler_type in self.payload_handlers.keys():
            # return user-specified payload handler type
            return self.payload_handlers[handler_type](config,**kwargs)

        elif handler_type=='':
            # empty payload handler type => default
            return self.payload_handlers['default'](config,**kwargs)

        else:
            err = "ERROR: PayloadHandlerFactory: factory(): "
            err += "Received an invalid handler type \"%s\"\n"%handler_type
            err += "Handler type must be one of: %s"%(", ".join(self.payload_handlers.keys()))
            raise Exception(err)

