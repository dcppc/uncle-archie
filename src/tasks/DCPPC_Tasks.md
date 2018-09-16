# DCPPC Task Classes

The base Task class handles processing of parameters
common to all tasks:

- htdocs dir
- status url
- log dir

Each DCPPC test must look in the config dictionary for
any of the following (and define default values for them):

- name
- label
- temp dir
- repo whitelist

Some DCPPC tests take additional parameters:

- base branch
- submodule remap

## DCPPC Task Class Parameters

The general pattern for setting parameters
is as follows:

```
import archie

app = archie.webapp.app
config = app.config

config['htdocs_dir'] = '/path/to/htdocs'
config['base_url'] = 'https://archie.example.com'

config['name_of_task'] = {
    'param_1' : 'value_1',
    'param_2' : 'value_2',
    'param_3' : 'value_3',
}

app.run()
```

Full example:

```
import archie

app = archie.webapp.app
config = app.config

config['htdocs_dir'] = '/www/archie.example.com/htdocs/output'
config['base_url'] = 'https://archie.example.com/output'

config['private_www_PR_builder'] = {
    'repo_whitelist' : ['dcppc/private-www'],
    'base_branch' : 'master'
}

config['private_www_submodule_integration_PR_builder'] = {
    'repo_whitelist' : [
            'dcppc/internal',
            'dcppc/organize',
            'dcppc/nih-demo-meetings',
            'dcppc/dcppc-workshops',
    ],
    'base_branch' : 'master',
    'submodule_map' : {
            'dcppc/dcppc-workshops' : 'workshops',
    }
}

app.run()
```


### DCPPC Task Classes

## private www PR builder

When a pull request is opened in the `private-www` repo,
run a build test.

## private www submodule integration PR builder

When a pull request is opened or synced in a repository that is
a submodule of `private-www`, run a build test on the 
`private-www` repo using that branch of the submodule.

## private www submodule update PR opener

When a pull request is merged into master in a repository that is
a submodule of `private-www`, open a pull request in `private-www`
to update the submodule pointer.

## private www (heroku) deployer

When a pull request is merged into master in the `private-www`
repo, build the site and deploy it to Heroku.

## use case library PR builder

When a pull request is opened or synced in the use case library
repository, run a build test on the repository.

## use case library (gh-pages) deployer

When a pull request is merged into master in the use case library
repo, build the site and deploy it to Github Pages.

## centillion CI tester

Run continous integration tests on master and on pull requests.

## uncle-archie CI tester

Run continous integration tests on master and on pull requests.

## private-www CI tester

Run continous integration tests on master and on pull requests.

## use case library CI tester

Run continous integration tests on master and on pull requests.

