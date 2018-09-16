# Uncle Archie: Tasks and Tests

Uncle Archie Task classes are low-level 
classes that run commands and take actions
on the system.

All Task classes define a `run()`
method that is called by the Payload Handler's
`process_payload()` method.

All Task classes also define `setup()`
and `teardown()` methods that are called
before and after the task is run.

## Using a Task

Tasks are used by Payload Handlers when
the Payload Handler defines its
`process_payload()` method. To use them,
the user first defines a Task class
in the Uncle Archie package:

```
class Task1(UncleArchieTask):
    def run(self, payload, meta, config):
        # This is where commands are actually run
        subprocess.call(['touch','/tmp/hello_world_1'])

class Task2(UncleArchieTask):
    def run(self, payload, meta, config):
        subprocess.call(['touch','/tmp/hello_world_2'])
```

The Tasks are created by a Payload Handler,
which calls the `run()` method on each Task:

```
class MyPayloadHandler(BasePayloadHandler):
    def process_payload(self, payload, meta, config):

        task1 = Task1()
        task1.run(payload,meta,config)

        task2 = Task2()
        task2.run(payload,meta,config)
```

## Passing Parameters to Tasks

Parameters for the Tasks are set using the config variable,
which contains the Uncle Archie Flask configuration.

For example, a task can utilize a parameter from
the Flask config to decide how to run a task:

```
class Task1(UncleArchieTask):
    def run(self, payload, meta, config):

        # Set the value of the sad flag
        sad = False
        if 'Task1' in config.keys():
            if 'sad' in config['Task1'].keys():
                sad = config['Task1']['sad']

        if sad:
            subprocess.call(['touch','/tmp/goodbye_world'])
        else:
            subprocess.call(['touch','/tmp/hello_world'])
```

The `sad` flag can then be set by the Uncle Archie user
when they create the Uncle Archie Flask app:

```
import archie

app = archie.webapp.app
config = app.config
config['Task1'] = {
    'sad' : True
}

...set payload handler using Task1...

app.run()
```

Now, when the webhook is received by the Flask app, 
it calls the Payload Handler, which calls Task1,
which checks the Flask config for a `sad` key and
controls the beahvior of the task.

## Defining a Task

Each Task object must define a `run()` method.
There is nothing else required for Task objects.

## Task Classes

For a list of DCPPC task classes, see [DCPPC_Tasks.md](DCPPC_Tasks.md)

### `UncleArchieTask` base class

See [`base.py`](base.py)

This is the base Task class.

The base Task class checks for any required input parameters
in the config variable:

- `htdocs_dir`
- `base_url`
- `log_dir`

Default values for these are set in the base Task class.

It does not process a name or label for the Task,
or any config variables that are task-specific.

This is because Tasks know their own name and label.
All Task config variables can be set in config,
but Tasks must know their own name to know where
to look! So, leave task-specific parameter handling
to the Task itself.

This class tries to stay as general as possible.
It only defines one virtual method, `run()`.

### `GithubTask` base class

See [`base.py`](base.py)

The Github Task base class defines convenience methods
for tasks that are performing actions on Github. This
base class can perform actions with the payload like 
checking if the payload is opening or syncing a pull 
request, getting the head commit of a pull request, or
setting the status of a commit.

### `PyGithubTask` base class

See [`base.py`](base.py)

The PyGithub Task base class extends the Github Task
class. It adds a setup and tear down step to the constructor
and destructor, respectively. These setup and tear down
methods manage a virtual Python environment, in which all 
Python commands for this Task will be run.

