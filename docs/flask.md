# Flask Webhook Server

The front end component of Uncle Archie is the flask webhook server.
This is a server with one endpoint. It receives webhooks and passes
them on to Python hook functions on the back end.


## Port and Bind Address

The Flask server listens on port 5005.

Uncle Archie binds to `127.0.0.1:5005` on the host it runs on.

(Note: this is important for the [Nginx](nginx.md) setup.)


## Routes

Send all webhooks to Uncle Archie's `/webhook` endpoint.

If your Uncle Archie server is running at `archie.mydomain.com`,
then the URL for your webhook (the one you will install into Github
repositories) will be `https://archie.mydomain.com/webhook`.

(Also see the [Nginx](nginx.md) page.)

Github webhooks are just JSON payloads, so `/webhook` should expect to
receive POST requests and convert them to JSON objects.

There are example webhook payloads in the [`museum/`](https://github.com/charlesreid1/uncle-archie/tree/master/museum)
directory of this repository.

There are also examples of [webhook payloads](https://developer.github.com/webhooks/)
in the Github documentation.


## Installing Uncle Archie Webhooks in a Github Repo

To install Uncle Archie in a Github repo you must be an admin
or owner of that repo. Go to the repository's Settings page
and pick Webhooks on the left side. Click the Add Webhook button.

This will ask you for the webhook format, the webhook URL endpoint,
the webhook secret, and which events you want to send.

The webhook format should be JSON - that's the drop-down menu.

The webhook URL endpoint is, as mentioned above, the URL of the
Uncle Archie server plus `/webhook`.

The webhook secret is set in `config.json`, loaded by the Flask
application. This is used to verify that incoming webhooks are,
in fact, legitimate.

Finally, the events that you want to send should be picked out
from the menu of possible webhook events, affording the CI server
maximum flexibility.

