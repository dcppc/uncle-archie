from ..payload_handlers import PayloadHandlerFactory
from flask import Flask, render_template
import os

base = os.path.split(os.path.abspath(__file__))[0]

class UAFlask(Flask):
    def __init__(self,**kwargs):
        self.super(**kwargs)
        self.payload_handler = None
        self.FactoryClass = PayloadHandlerFactory

    def set_payload_handler_factory_class(self,NewFactoryClass):
        """
        This allows the user to set a new
        Payload Handler Factory class type.

        Checking if this is a derived type
        of the PayloadHandlerFactory is a
        TODO item.
        """
        # Check if NewFactoryClass is in the
        # class hierarchy of PayloadHandlerFactory
        self.FactoryClass = NewFactoryClass

    def set_payload_handler(self,handler_id):
        """
        Given a (string) payload handler ID,
        pass it to the factory to get a
        corresponding Payload Handler object
        of the correct type.
        """
        self.payload_handler = PayloadHandlerFactory(
                handler_id,
                self.config,
                **kwargs
        )

    def get_payload_handler(self,):
        """
        Get the payload handler that we have set
        """
        if self.payload_handler is None:
            err = "ERROR: UAFlask: get_payload_handler(): "
            err += "No payload handler has been set!"
            raise Exception(err)
        return self.payload_handler


app = UAFlask(
        __name__,
        #template_folder = os.path.join(base,'templates'),
        #static_folder = os.path.join(base,'static')
)

@app.route('/')
def index():
    payload_handler = app.get_payload_handler()
    payload_handler.process_payload(payload, meta, config)
    return "Hello world!"


