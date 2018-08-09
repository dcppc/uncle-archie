# Flask Webhook Server

The first component of Uncle Archie is the flask webhook server.
This is a server with one endpoint whose sole function is to 
receive and process webhooks from any number of repositories.

## Routes

The Uncle Archie Flask server has one endpoint, `/webhook`. That is
where all webhooks should be sent. If your Uncle Archie server is
running at `archie.mydomain.com`, you should install webhooks with an endpoint
of `https://archie.mydomain.com/webhook` (more on domain configuration
and HTTPS on the [Nginx](nginx.md) page).

The `/webhook` route is sent a JSON payload from Github. 

The Flask server extracts meta-info (name of repo, type of event,
name of branch) about the webhook event from the payload,
then passes all of this information to `process_payload()`
in the `process_payload.py` file, which passes it on to 
user-defined functions.

There are also [webhook examples](https://developer.github.com/webhooks/)
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

