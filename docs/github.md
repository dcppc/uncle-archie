# Activating Hooks in Github

Once you have written a new Uncle Archie hook, it is being called 
from `process_payload.py`, and the Uncle Archie flask server has 
been restarted, you must activate webhooks in the repository.

Go to the repository of interest and click "Settings", 
then click "Webhooks" on the left side, then click the
"Add webhook" button.


## Dealing With SSH And Private Repos

With Uncle Archie, private repositories can get tricky.

For the user running Uncle Archie, you need to set up 
an SSH key, add it to the Github account you want Uncle
Archie to use (the same account you're using to generate
the API access token).

Then, you need to set your Github username and email for 
the \*nix user you are using to run Uncle Archie by adding
the following to your `~/.bash_profile`:

```
GIT_AUTHOR_NAME="<uncle-archie-bot-name>"
GIT_COMMITTER_NAME="${GIT_AUTHOR_NAME}"
git config --global user.name "${GIT_AUTHOR_NAME}"

GIT_AUTHOR_EMAIL="<uncle-archie-bot-email>"
GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
git config --global user.email "${GIT_AUTHOR_EMAIL}"
```

Now, when you log in as that \*nix user and run Uncle Archie,
the Github user will be set via environment variables, and
the SSH key for that user will allow you to clone repos
over SSH.

Last, if you clone repositories, use a URL scheme like 
`git@github.com:owner/repo` instead of 
`https://github.com/owner/repo`.

