# uncle-jenkins

**Uncle Jenkins** is a homebrew continuous integration server.
It handles pull request checks (build-test) and push-to-deploy 
functionality (build-test-deploy).

Uncle Jenkins is intended to run behind an nginx reverse proxy
so that SSL can be used. This requires the server running 
Uncle Jenkins be accessible at a domain name, and not just be
a bare IP address.

## Table of Contents


Preparing Jenkins:

- Preparing Jenkins
  - [Installing Jenkins](installing.md)
  - [Nginx and Jenkins](nginx.md)
  - [Configuring Jenkins](configuring.md)

- Jenkins Plugins: 
  - [Installing Plugins](plugins.md)
  - [Github Pull Request Builder](plugins_ghprb.md)

- Pipelines:
  - [Pull Request Reviews](#) (in progress)

## Links

Documentation (you are here): <https://pages.charlesreid1.com/uncle-jenkins>

Source code: <https://git.charlesreid1.com/bots/uncle-jenkins>

Source code mirror: <https://github.com/charlesreid1/uncle-jenkins>


