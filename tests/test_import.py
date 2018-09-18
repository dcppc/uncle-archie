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
    assert isinstance(archie.webapp.get_flask_app(),Flask)

    # import method 2
    from flask import Flask
    from archie.webapp import get_flask_app
    app = get_flask_app()
    assert isinstance(app,Flask)

def test_import_payload_handler():
    """
    Test that we can import and use the
    Payload Handler class
    """
    app = archie.webapp.get_flask_app()
    phf = archie.payload_handlers.PayloadHandlerFactory()
    assert isinstance(phf.factory('default',app.config), archie.payload_handlers.LoggingPayloadHandler)
    assert isinstance(phf.factory('dcppc',  app.config), archie.payload_handlers.DCPPCPayloadHandler)

    # import method 2
    from archie.payload_handlers import PayloadHandlerFactory
    from archie.payload_handlers import LoggingPayloadHandler
    from archie.payload_handlers import DCPPCPayloadHandler
    from archie.webapp import get_flask_app
    app = get_flask_app()
    config = app.config
    phf = PayloadHandlerFactory()
    assert isinstance(phf.factory('default',config),LoggingPayloadHandler)
    assert isinstance(phf.factory('dcppc',  config),DCPPCPayloadHandler)

