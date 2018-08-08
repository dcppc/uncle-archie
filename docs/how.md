# How It Works

Uncle Archie is a home-brewed continuous integration (CI) server.

On the front end, Uncle Archie receives webhooks from Github
via a Flask server. This webhook endpoint is installed in
any repository that would potentially like to trigger CI 
builds with Uncle Archie.

On the back end, Uncle Archie passes each webhook to a set
of user-defined Python functions that decide what to do.
They implement all of the logic - finding pull requests
against master, identifying the head commit in a branch,
updating the status of a commit, etc etc.

Uncle Archie's flask server is simply a messenger - when
events happen in repositories, webhooks are sent to the
flask server, which passes it along to each CI script.

