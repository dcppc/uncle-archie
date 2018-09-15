from flask import Flask, render_template
import os

base = os.path.split(os.path.abspath(__file__))[0]

class UAFlask(Flask):
    def __init__(self,**kwargs):
        self.super(**kwargs)
        self.payload_handler = PayloadHandlerFactory('default')

    def set_payload_handler(self,handler_id):
        self.payload_handler = PayloadHandlerFactory(handler_id)

    def get_payload_handler(self,):
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


