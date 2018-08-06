# installing jenkins

These instructions assume you are running Ubuntu 16.04.

* See the [jenkins installation page](https://jenkins.io/doc/book/installing/)
  for coverage of other platforms.

* See [jenkins download page](https://jenkins.io/download/) to get jenkins 
  for your platform.

## installing with aptitude

To install jenkins, we use aptitude, which installs
jenkins as a system service:

```
wget -q -O - https://pkg.jenkins.io/debian/jenkins-ci.org.key | sudo apt-key add -
echo deb https://pkg.jenkins.io/debian-stable binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list
sudo apt-get update
sudo apt-get install jenkins
```

Now start jenkins running on port 8080:

```
sudo systemctl start jenkins
```

## starting/stopping the jenkins service

Jenkins will be installed as a system service, so it can be 
started and stopped using systemctl:

```
sudo systemctl start jenkins
sudo systemctl stop jenkins
sudo systemctl restart jenkins
```

## unlocking jenkins

Verify your installation went okay by visiting
`http://<server-ip>:8080` in your browser. You should
be asked for an admin password, available in the file
`/var/lib/jenkins/secrets/initialAdminPassword`:

```
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

You can set a new user/password, or you can use
the admin username with the alphanumeric string in
the above file as the password.

Once you set up an admin user, you should now see
the following login page when you visit your jenkins
instance:

<img src="/images/jenkins-login-pre.png" width="500px" />


## installing jenkins plugins

The last installation step is to install the right
Jenkins plugin to interact with Github.

Once you are logged in you should see a view like this:

<img src="/images/jenkins-login-post.png" width="500px" />

After clicking "Manage Jenkins" on the left, you should see a list of menu items:

<img src="/images/jenkins-manage.png" width="500px" />

Scroll down to the item "Manage Plugins" (gren puzzle piece):

<img src="/images/jenkins-manage-2.png" width="500px" />

This takes you to the plugin manager view:

<img src="/images/jenkins-pm.png" width="500px" />

Click the Available tab to see a list of plugins that are available on the
server and can be installed into your Jenkins instance:

<img src="/images/jenkins-pm-avail.png" width="500px" />

## installing github pull request builder plugin

To enable Jenkins to build Pull Requests and act as a PR check, we need
to install the "Github Pull Request Builder" plugin into Jenkins.

Use Control + F to search for "Github Pull Request Builder" and check
the box next to it. Then click the button at the bottom that says
"Install without restart."

Now click the Installed tab on the plugin manager page to see a list
of plugins that are installed on the server: 

<img src="/images/jenkins-pm-inst.png" width="500px" />

Control + F search for "Github Pull Request Builder" and you should
see it come up:

<img src="/images/jenkins-pm-inst-2.png" width="500px" />

Don't bother clicking the link, since it will take you to
the Jenkins wiki page for the plugin. We will configure it
in the next step. See [set up jenkins](setup.md).

