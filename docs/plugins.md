# Installing Jenkins Plugins

The last step for getting our uncle-jenkins server prepared
is to install the right jenkins plugins to perform the tasks
we want.

## plugins

* [**Github Pull Request Builder (GHPRB)**](plugins_ghprb.md) - the GHPRB
  plugin allows Jenkins to create builds on pull requests, which allows Jenkins
  to be integrated as a PR build check step in a repository. See the
  [GHPRB plugin](plugins_ghprb.md) page.

## how to install plugins

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

From here, you can install any of the plugins listed.

