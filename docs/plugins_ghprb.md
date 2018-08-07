# Github Pull Request Builder (GHPRB) Jenkins Plugin

Also see the [plugins](plugins.md) page.

## installing jenkins GHPRB plugin 

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
the Jenkins wiki page for the plugin. 

## getting to the jenkins configuration page

To configure the GHPRB plugin, start from the home view:

<img src="/images/jenkins-login-post.png" width="500px" />

After clicking "Manage Jenkins" on the left, you should see a list of menu items:

<img src="/images/jenkins-manage.png" width="500px" />

After clicking the first item, "Configure System", you should see a page with
many sections:

<img src="/images/jenkins-configure.png" width="500px" />

Let's go through how to set up the pull request build plugin
to properly authenticate with Github.

## configuring jenkins GHPRB plugin

Note: these steps are based largely on the README in the
[Github Pull Request Builder plugin
repo](https://github.com/jenkinsci/ghprb-plugin/blob/master/README.md)
(on Github, of course).

Once at the configuration page, scroll down to the section titled
"Github Pull Request Builder" (or Control + F it).

<img src="/images/jenkins-ghprb-1.png" width="500px" />

This has a couple of key fields:

* Github server API URL: this is for Github Enterprise users; leave as is if
  using Github.com

* Credentials: this is where we will add our Github credentials (log in under
  the bot account we want Jenkins to use).

* Connect to API: we will use this to test our credentials.

* Advanced: this button will open up a whole host of options. These are covered
  below.

### basic configuration: authenticating with Github API

Click the "Add" button next to credentials and select Jenkins as your 
credentials provider. Create a credential of Kind "Secret Text".
For the Secret, you will enter a Github Personal Access Token,
which we'll cover next.

Here is what the jenkins credentials provider looks like:

<img src="/images/jenkins-ghprb-2.png" width="500px" />

To create a Github Authentication Token, log in to Github using the account
jenkins will review PRs as. Go to the Settings page and click Developer Settings,
then Personal acess tokens, or just visit <https://github.com/settings/tokens>
once you are logged in.

Now click "Generate New Token". You will see some options like those shown
below. Configure the check boxes to match those shown in the image below:

<img src="/images/jenkins-ghprb-3.png" width="500px" />

Now create a token. The token will only be shown once, and cannot be viewed
again, so store it somewhere safe like a password manager.

Back at the jenkins credentials provider window, enter the
API key you generated into the "Secret" field. Leave the
other fields blank. Click Add.

Here's what the Github Pull Request Builder section of the jenkins configuration 
page will look like once you've authenticated with Github: 

<img src="/images/jenkins-ghprb-3.png" width="500px" />

Now test the authentication mechanism by clicking Test Credentials.

### testing authentication with Github

There are several tests to run to ensure Github authentication is
working okay.

Starting from the Github Pull Request Builder section of the configuration
page, click the Test Credentials button:

<img src="/images/jenkins-ghprb-4.png" width="500px" />

This opens several checkboxes with options. To run the given test,
you check the box. (Weird, I know.)

<img src="/images/jenkins-ghprb-5-test-1.png" width="500px" />

When you check the "Test basic connection to Github" box, you'll see
the results of checking that you can connect to Github:

<img src="/images/jenkins-ghprb-5-test-2.png" width="500px" />

Enter a repository that your Jenkins user should have access to, 
and then check the next checkbox, "Test Permissions to a Repository":

<img src="/images/jenkins-ghprb-5-test-3.png" width="500px" />

For the next test, you should create a pull request in the repository
that you entered in the text box. You can do this easily by opening
the README file in your repository, clicking the pencil "Edit" button
in Github, and adding an empty line at the top of the file.

When you click the green submit button, make sure you select the option
to create a new branch and start a pull request. Once you have submitted
the change as a pull request, click the "Pull Requests" tab of the repository
and find the pull request's number. In the example below, the pull request
is #1:

<img src="/images/jenkins-ghprb-5-test-4.png" width="500px" />

When you click "Comment to Issue", Jenkins will use the Github credentials
to attempt to leave the comment specified in the text box in the pull
request thread.

Here's what it should look like if everything goes according to plan:

<img src="/images/jenkins-ghprb-5-test-5.png" width="500px" />



