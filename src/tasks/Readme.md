# Uncle Archie: Tasks and Tests

Uncle Archie Task classes are low-level 
classes that run commands and take actions
on the system.

All Task classes define a `process_payload()`
method that is called by the Payload Handler's
`process_payload()` method.

Uncle Archie Test classes are components of
Task classes (a Task may run multiple Tests).

All Test classes define a `run()` command,
which actually runs the test and performs
an action with the result (e.g., marking a
Github commit as pass or fail).

## Using a Task

Tasks are used by Payload Handlers when
the Payload Handler defines its
`process_payload()` method. To use them,
the user first defines a Task class
in the Uncle Archie package:

```
class BuildTask1(UncleArchieTest):
    def process_payload(self, payload, meta, config):
        # This is where commands are actually run
        subprocess.call(['touch','/tmp/hello_world_1'])

class BuildTask2(UncleArchieTest):
    def process_payload(self, payload, meta, config):
        subprocess.call(['touch','/tmp/hello_world_2'])
```

Then, this Task is created by a Payload Handler,
which calls its `process_payload()` method:

```
class MyPayloadHandler(BasePayloadHandler):
    def process_payload(self, payload, meta, config):

        task1 = BuildTask1()
        task1.process_payload(payload,meta,config)

        task2 = BuildTask2()
        task2.process_payload(payload,meta,config)
```

