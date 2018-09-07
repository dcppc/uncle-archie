# Uncle Archie Tests

Test strategy:

Create a docker compose file with a container running uncle archie
and another container running curl commands to fake incoming webhooks.

May only be able to trigger events, but that's better than triggering
commit after commit.

