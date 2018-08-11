# How It Works

Uncle Archie is a home-brewed continuous integration (CI) server.

**Front End:**

Uncle Archie runs a frontend webhook server that receives 
webhooks from Github. This runs a [Flask](#) 
server using [Jinja](#) templates.

This webhook server endpoint is installed into any Github
repository that would potentially like to trigger CI builds
with Uncle Archie.

**Back End:**

On the back end, the Flask server passes each webhook to a
set of Python hook functions. Those functions then decide
what to do with the payload.

**Example:**

An example of using Uncle Archie for CI testing is to run
documentation tests with mkdocs on pull requests on a repository.

To do this, we would define a hook function that takes a Github
webhook payload (JSON/Python dictionary) as input, and looks for
payloads that are updating or opening pull requests in specified
repositories. It then clones a local copy of the head commit
of that pull request, attempts to build mkdocs in the root of
the repository, and marks the commit as "success" or "failed"
depending on the outcome.

The Uncle Archie repository contains a hook function in
`hooks/mkdocs_test.py` that implements this test.


