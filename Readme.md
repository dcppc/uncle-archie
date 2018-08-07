# uncle-jenkins

<img src="docs/images/unclejenkinsbk.svg" width="100px" />

**Uncle Jenkins** is a home-brewed continuous integration server.
It handles pull request checks (build-test) and push-to-deploy 
functionality (build-test-deploy).

**Uncle Jenkins** is intended to run behind an nginx reverse proxy
so that SSL can be used. This requires the server running 
Uncle Jenkins be accessible at a domain name, and not just be
a bare IP address.

Documentation: <https://pages.charlesreid1.com/uncle-jenkins> or [`docs/index.md`](docs/index.md)

Source code: <https://git.charlesreid1.com/bots/uncle-jenkins>

Source code mirror: <https://github.com/charlesreid1/uncle-jenkins>

