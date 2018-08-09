# Startup Service

See [`scripts/archie.service`](https://github.com/charlesreid1/uncle-archie/blob/master/scripts/archie.service)

Now install the service to `/etc/systemd/system/archie.servce`,
and activate it:

```
sudo systemctl enable archie.service
```

Now you can start/stop the service with:

```
sudo systemctl (start|stop) archie.service
```

