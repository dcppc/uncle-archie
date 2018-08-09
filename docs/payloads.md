# How Payloads Are Processed

Uncle Archie runs a Flask server to receive webhooks.
Github sends webhooks in the form of JSON to the Flask
server when events occur on Github. The JSON file contains
lots of information about the event - the who/what/where/when/how.

The JSON webhook is converted to a Python dictionary and is
passed to the `process_payload()` function defined in 
`process_payload.py`.  The function takes three arguments:
the full payload, the meta-information (name of repo,
name of branch, type of event), and the config dictionary
coming from `config.json` (this contains the Github API
key we need).

## Hooks

Each incoming webhook payload is passed to a set of hook functions,
which are Python functions that live in the `hooks/` folder.
These are imported and called by `process_python.py`.

See [Hooks](hooks.md) for details about how the hooks work
and how to define new ones.

## Payload Museum

To see examples of payloads, visit the 
Payload Museum in the `museum/` directory
of the repository.

## Uncle Archie Configuration File

The configuration file `config.json` contains **both** Flask **and** 
backend (hook-specific) configuration details.

For example, the secret key for the Flask server is a key that must
be embedded in the webhook for the webhook to be processed.
This is a flask-specific configuration detail. But the Github
API key for the Github bot is also specified in the configuration
file, and that is information used by the hook functions.

API keys are sensitive information so this file 
should be kept secret (hence it is in `.gitignore`).

The config is loaded by the Flask application, since it contains
flask-specific configuration details. The configuration is then
handed off to the process payload function, which passes it on 
to each hook function.

It is avialable via the variable `conf`.

