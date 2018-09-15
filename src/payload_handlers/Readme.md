# Uncle Archie: Payload Handlers

The Payload Handler class is a high-level class
that adds tasks to a task list at an abstract level.
Payload handlers do not run any commands and only 
know what tasks to create and run.

You can think of a Payload Handler as a suite of
related tasks and tests.

## Using a Payload Handler

To use a payload handler, set it using the `app` object
in the `webapp` submodule of Uncle Archie:

```
import archie

app = archie.webapp.app
app.set_payload_handler('default')
app.run(port=5005)
```

This uses the default payload handler, which dumps
the payload to a file on disk. To pass parameters
to the payload handler, set parameters using the
Flask app's config variable:

```
import archie

app = archie.webapp.app
config = archie.webapp.app.config
config['payload_handler'] = {
    'param_1' : 'value_1',
    'param_2' : 'value_2'
}
app.set_payload_handler('default')
app.run(port=5005)
```

The respective Payload Handler class should look
for `param_1` and `param_2` in the Flask config
variable that is passed to it when the 
`process_payload()` method is called on it.

## Defining a Payload Handler

To define a Payload Handler class, extend the
`BasePayloadHandler` class, and override the
virtual `process_payload()` method.

Thie `process_payload()` method defined by the
Payload Handler should create and run high-level
Task objects.

The extra level of abstraction lets you define
a high-level payload handler that loads a whole
suite of tasks and tests, without fussing with
any low-level details.

## Classes

### `PayloadHandlerFactory` class

See [`factory.py`](factory.py)

Uncle Archie uses a factory pattern to create
Payload Handlers of different types. Each payload
handler has a predefined set of tasks.

The Payload Handler factory is created/used by the 
Flask app in the `/webhook` route. It calls the 
factory to create a new Payload Handler object each
time a webhook payload arrives.

If users wish to define new payload handlers
they can define a new class extending the 
`BasePayloadHandler` class, and redefine the
`process_payload()` method to run whatever
tasks they wish.

Payload Handlers can accept parameters set in the 
Flask config object, which is passed to the 
`process_payload()` method.

### `BasePayloadHandler` class

See [`handlers.py`](handlers.py)

The `BasePayloadHandler` class defines one virtual method,
`process_payload()`, which is the method that accepts the
payload and Flask configuration and creates and runs 
high-level Task objects.

### `DumpPayloadHandler` class

The `DumpPayloadHandler` does just what it says - it dumps
the payloads it receives (this is like a hello world program
for webhook servers). It does this by creating a high-level
Task object. Options like directory are passed in via the
Flask configuration.

### `DCPPCPayloadHandler` class

The `DCPPCPayloadHandler` runs a set of tasks for the 
DCPPC organization.

Telling Uncle Archie to use this handler will run
a DCPPC instance of Uncle Archie.

Note: this is not for general usage, and requires a 
Github API key for an account with appropriate access
to DCPPC repos.

