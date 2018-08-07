# Installing Jenkins

These instructions assume you are running Ubuntu 16.04.

* See the [jenkins installation page](https://jenkins.io/doc/book/installing/)
  on jenkins.io for coverage of other platforms.

* See [jenkins download page](https://jenkins.io/download/) on jenkins.io
  to download jenkins for your platform.

## installing jenkins with aptitude

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


## installing nginx proxy

If you are running Jenkins behind an nginx server (optional), 
this is the proper time to set up the nginx server to reverse 
proxy Jenkins.

See [nginx and jenkins](nginx.md)


