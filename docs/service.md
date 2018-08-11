# Startup Service

File: [`scripts/archie.service`](https://github.com/charlesreid1/uncle-archie/blob/master/scripts/archie.service)

### Quick Version

Start by creating a separate user account on your \*nix box that will
be used to run Uncle Archie with separate SSH and Github user credentials
than your regular account.

**Create** a new user:

```
adduser florence
```

**Log in** as the new user and (i) generate a new SSH key, and (ii) add lines to
your `~/.bash_profile` that will set your Github username/email credentials.

```
sudo -H -u florence /bin/bash

# now you are the user florence

# generate ssh key
ssh-keygen -t rsa -N '' -b 4096 -f $HOME/.ssh/id_rsa -C "<email-of-github-bot-account>"
chmod 700 $HOME/.ssh
touch $HOME/.ssh/authorized_keys
chmod 600 $HOME/.ssh/authorized_keys

# add this to ~/bash_profile
GIT_AUTHOR_NAME="<uncle-archie-bot-name>"
GIT_AUTHOR_EMAIL="<uncle-archie-bot-email>"

GIT_COMMITTER_NAME="${GIT_AUTHOR_NAME}"
GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"

git config --global user.name "${GIT_AUTHOR_NAME}"
git config --global user.email "${GIT_AUTHOR_EMAIL}"
```

**Update** `archie.service` to run Uncle Archie as the new user
you just created, by setting the username in the two lines

```
ExecStart=/user/bin/sudo -H -u <username> ...
ExecStop=/user/bin/sudo -H -u <username> ...
```

**Install** the startup service by copying to 
`/etc/systemd/system/archie.servce`. Then activate it:

```
sudo cp scripts/archie.service /etc/systemd/system/archie.service
sudo systemctl enable archie.service
```

Now you can start/stop the service with:

```
sudo systemctl (start|stop) archie.service
```


### Start/Stop Archie Scripts

You may be wondering why we require a script to start and stop Uncle Archie.

There are several challenges running Uncle Archie as a startup service,
and multiple setup steps involved. These include:

* Startup services run as the root user, but we want Uncle Archie
  to run as a normal user

* We want to use a virtual python environment with packages installed
  from requirements.txt, not the system python or a user python
  that may have outdated or missing packages.

* We need the SSH and Github user credentials that Uncle Archie will
  use to match those of the Github bot account we're using to run
  Uncle Archie, and not the personal credentials of the developer
  whose machine Uncle Archie is running on.

That's what the `start_archie.sh` script does.

