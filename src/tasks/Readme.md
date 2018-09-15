# Uncle Archie: Tasks and Tests

Uncle Archie Task classes are low-level 
classes that run commands and take actions
on the system.

All Task classes define a `run()`
method that is called by the Payload Handler's
`process_payload()` method.

The Test subclass extends the Task class.
All Test classes define a `run()` method,
as well as a `test()` method that actually
runs the test (everything else in the `run()`
method is setup or cleanup for the test).

The `test()` method can do things like mark
a Github commit as pass/fail.

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

Parameters for the Tasks are set using the config variable,
which contains the Uncle Archie Flask configuration.

## Defining a Task

Each Task object must define a `run()` method.
There is nothing else required for Task objects.

## Task Classes

For a list of DCPPC task classes, see [DCPPC_Tasks.md](DCPPC_Tasks.md)

### `UncleArchieTask` base class

This is the base `Task` class.

This class tries to stay as general as possible.
It only defines one virtual method, `run()`.












