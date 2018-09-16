import archie

# webapp
app = archie.webapp.app

# set config
config = archie.webapp.app.config
config['private_www_build_test'] = {
        'repo_whitelist' : ['dcppc/private-www','charlesreid1/private-www']
}
config['debug'] = True

# set payload handler
app.set_payload_handler('dcppc')

# dooooo it
app.run()

