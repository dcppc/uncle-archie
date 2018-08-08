# Architecture

Uncle Archie is a home-brewed continuous integration server.
It is implemented in Python and uses PyGithub to run checks
and set the status of code in Github repos.

Uncle Archie runs a single Flask webhook server with a single
endpoint that listens for incoming webhooks. These webhooks
are installed in various Github repositories so that Uncle
Archie can be notified of events in those repositories.

The Flask server will load a pile of user-defined functions
and pass the webhook to each one. To change the behavior of 
Uncle Archie, simply change the scripts.

**Ideal:** user defines a function, drops it in a folder, webhook
automatically loads all functions in that folder and passes
the webhook to each one. (Then, in the function, you say,
if this is a pull request event... do X... if this is a
push event... do Y...)

[List of Github webhooks](https://developer.github.com/webhooks/)

