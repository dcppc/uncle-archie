# Activating Hooks in Github

Once you have written a new Uncle Archie hook, it is being called 
from `process_payload.py`, and the Uncle Archie flask server has 
been restarted, you must activate webhooks in the repository.


## Installing Uncle Archie Webhooks in a Github Repo

See [Flask](flask.md) (section, "Installing Uncle Archie
Webhooks in a Github Repo").


## Dealing With SSH, Github Credentials, Private Repos

Before testing whether Uncle Archie can access private
repositories, make sure Uncle Archie is using the
credentials that you expect.

See the [Startup Service](service.md) page for more info
on how to set up an isolated user account for Uncle Archie
that has its own SSH keys and Github user credentials.

Once the user account has been created, the Uncle Archie
startup service can be modified to run as the dedicated
user.

Last, if you clone private repositories, you must use a
URL scheme like `git@github.com:owner/repo` instead of 
`https://github.com/owner/repo`.

