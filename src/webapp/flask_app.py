from ..payload_handlers import PayloadHandlerFactory
from .const import base, call

from flask import Flask, request, abort, render_template
import os, sys
import json
import logging

from .const import base
from .const import call


class UAFlask(Flask):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        logging.debug("="*40)
        logging.debug("="*40)
        logging.debug("flask __init__()")
        logging.debug("="*40)
        logging.debug("="*40)

        self.payload_handler = None
        self.phf = PayloadHandlerFactory()

        # ----------------------------
        # Load config
        msg = "UAFlask: __init__: Preparing to load webapp config file.\n"
        loaded_config = False
        if 'UNCLE_ARCHIE_CONFIG' in os.environ:
            if os.path.isfile(os.path.join(call,os.environ['UNCLE_ARCHIE_CONFIG'])):
                # relative path
                self.config.from_pyfile(os.path.join(call,os.environ['UNCLE_ARCHIE_CONFIG']))
                loaded_config = True
                msg = "UAFlask: __init__: Succesfuly loaded webapp config file from UNCLE_ARCHIE_CONFIG variable.\n"
                msg += "Loaded config file at %s"%(os.path.join(call,os.environ['UNCLE_ARCHIE_CONFIG']))
                logging.info(msg)
        
            elif os.path.isfile(os.environ['UNCLE_ARCHIE_CONFIG']):
                # absolute path
                self.config.from_pyfile(os.environ['UNCLE_ARCHIE_CONFIG'])
                loaded_config = True
                msg = "UAFlask: __init__: Succesfuly loaded webapp config file from UNCLE_ARCHIE_CONFIG variable.\n"
                msg += "Loaded config file at %s"%(os.environ['UNCLE_ARCHIE_CONFIG'])
                logging.info(msg)
        
        else:
            err = "UAFlask: __init__: Warning: No UNCLE_ARCHIE_CONFIG environment variable defined, "
            err += "looking for 'config.py' in current directory."
            logging.info(err)

            # hail mary: look for config.py in the current directory
            default_name = 'config.py'
            if os.path.isfile(os.path.join(call,default_name)):
                self.config.from_pyfile(os.path.join(call,default_name))
                loaded_config = True
                msg = "UAFlask: __init__: Succesfuly loaded webapp config file with a hail mary.\n"
                msg += "Loaded config file at %s"%(os.path.join(call,'config.py'))
                logging.info(msg)

        if not loaded_config:
            err = "ERROR: UAFlask: __init__(): Problem setting config file with UNCLE_ARCHIE_CONFIG environment variable:\n"
            try:
                err += "UNCLE_ARCHIE_CONFIG value : %s\n"%(os.environ['UNCLE_ARCHIE_CONFIG'])
            except:
                pass
            err += "Missing config file : %s\n"%(os.environ['UNCLE_ARCHIE_CONFIG'])
            err += "Missing config file : %s\n"%(os.path.join(call, os.environ['UNCLE_ARCHIE_CONFIG']))
            logging.error(err)
            raise Exception(err)


    def set_payload_handler(self,handler_id,**kwargs):
        """
        Given a (string) payload handler ID,
        save it for later.
        
        Eventually we will pass it to the factory 
        to get a corresponding Payload Handler 
        object of the correct type.
        """
        self.payload_handler = None
        self.payload_handler_id = handler_id


    def get_payload_handler(self):
        if self.payload_handler is None:
            err = "ERROR: UAFlask: get_payload_handler(): "
            err += "No payload handler has been set!"
            logging.error(err)
            raise Exception(err)
        return self.payload_handler


    def del_payload_handler(self):
        """
        Delete the payload handler when we're done with the webhook
        """
        del self.payload_handler


    def init_payload_handler(self):
        """
        Use the PayloadHandler factory to initialize
        an instance of the payload handler that is 
        specified with self.payload_handler_id
        """
        if self.payload_handler_id is None:
            err = "ERROR: UAFlask: init_payload_handler(): "
            err += "No payload handler has been set!"
            logging.error(err)
            raise Exception(err)

        self.payload_handler = self.phf.factory(
                self.payload_handler_id,
                self.config,
        )

        return self.payload_handler


