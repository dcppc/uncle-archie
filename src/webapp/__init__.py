from .flask_app import UAFlask
from .flask_routes import setup_routes
from .const import base

from flask import Flask, request, abort, render_template
import os, sys
import json
import logging


def get_flask_app():
    app = UAFlask(
            __name__,
            template_folder = os.path.join(base,'templates'),
            static_folder = os.path.join(base,'static')
    )
    setup_routes(app)
    return app

