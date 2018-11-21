import archie

# webapp
app = archie.webapp.get_flask_app()

# set config
app.config['private_www_build_test'] = {
        'repo_whitelist' : ['dcppc/private-www']
}
app.config['debug'] = True

# set payload handler
app.set_payload_handler('dcppc')

# dooooo it
app.run()

