# DCPPC Task Classes

## private www pull request builder

When a pull request is opened in the `private-www` repo,
run a build test.

## private www submodule integration builder

When a pull request is opened or synced in a repository that is
a submodule of `private-www`, run a build test on the 
`private-www` repo using that branch of the submodule.

## private www submodule update pull request opener

When a pull request is merged into master in a repository that is
a submodule of `private-www`, open a pull request in `private-www`
to update the submodule pointer.

## private www heroku deployer

When a pull request is merged into master in the `private-www`
repo, build the site and deploy it to Heroku.

## use case library pull request builder

When a pull request is opened or synced in the use case library
repository, run a build test on the repository.

## use case library gh-pages deployer

When a pull request is merged into master in the use case library
repo, build the site and deploy it to Github Pages.

## centillion continuous integration tester

Run continous integration tests on master and on pull requests.

## uncle-archie continuous integration tester

Run continous integration tests on master and on pull requests.

## private-www continuous integration tester

Run continous integration tests on master and on pull requests.

## use case library continuous integration tester

Run continous integration tests on master and on pull requests.

