import archie

"""
Uncle Archie Smoke Test

This tests that we can import everything.
"""

def test_import_webapp():
    """
    Test that we can import/use the webapp
    """
    # import method 1
    from flask import Flask
    assert isinstance(archie.webapp.app,Flask)

    # import method 2
    from archie.webapp import app
    from flask import Flask
    assert isinstance(app,Flask)

def test_import_payload_handler():
    """
    Test that we can import and use the
    Payload Handler class
    """
    phf = archie.payload_handlers.PayloadHandlerFactory()
    assert isinstance(phf.factory('default',archie.webapp.app.config), archie.payload_handlers.DumpPayloadHandler)
    assert isinstance(phf.factory('dcppc',archie.webapp.app.config),   archie.payload_handlers.DCPPCPayloadHandler)

    # import method 2
    from archie.payload_handlers import PayloadHandlerFactory
    from archie.payload_handlers import DumpPayloadHandler
    from archie.payload_handlers import DCPPCPayloadHandler
    from archie.webapp import app
    config = app.config
    phf = PayloadHandlerFactory()
    assert isinstance(phf.factory('default',config),DumpPayloadHandler)
    assert isinstance(phf.factory('dcppc',config),DCPPCPayloadHandler)
    


