# Nginx Web Server

## Background

### What Is Nginx?

nginx is a web server that can allow for a lot more flexibility
in routing domain names and web traffic from the frontend to
various backend servers.

One of the more useful functionalities in nginx is the ability to
set up a reverse proxy.

### What Is A Reverse Proxy?

A proxy is defined as _the authority to represent someone else_.
Typically a proxy is set up to "surround" and "wrap" actions that
the user takes, and relay them to the "outside world" (i.e., the 
world beyond the proxy).

A reverse proxy means that instead of "surrounding" and "wrapping"
the client, a reverse proxy wraps the end server. That means that
any requests for , say, `https://archie.mydomain.com` can be reverse 
proxied to the Uncle Archie Flask server at `http://localhost:50005/`.

The advantage of this is that Uncle Archie Flask is not accessible
via port 50005 to outside users. Every request must pass through nginx.

## First Steps: Installing Nginx

Using your operating system's package manager is recommended:

```
apt-get install nginx
```

On Ubuntu, this will install configuration files to:

```
/etc/nginx/
```

and will make nginx a service that can be started/stopped with:

```
sudo service nginx start
sudo service nginx stop
```

**Uncle Archie runs on port 50005 and is available at
`localhost:50005`.**

## Nginx Standard Configuration

The "standard configuration" for nginx is to use port 443 for
HTTPS, port 80 for HTTP, and to automatically redirect HTTP
requests on port 80 to the more secure port 443.

The nginx configuration file below sets up nginx as a 
reverse proxy in front of Uncle Archie, and makes it available 
via a subdomain like `archie.mysite.com`.

Here is the nginx configuration file and the location
on disk where it should be using an aptitude-installed
nginx:

**`/etc/nginx/sites-available/archie.conf`**

```plain
server {
    listen 80;
    listen [::]:80;
    server_name archie.mydomain.com;
    location / {
        return 301 https://archie.mydomain.com$request_uri;
    }
}

server {
    listen 443;
    listen [::]:443;
    server_name archie.mydomain.com;

    ssl on;
    ssl_certificate /etc/letsencrypt/live/archie.mydomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/archie.mydomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;

    client_max_body_size 100m;
 
    gzip              on;
    gzip_http_version 1.0;
    gzip_proxied      any;
    gzip_min_length   500;
    gzip_disable      "MSIE [1-6]\.";
    gzip_types        text/plain text/xml text/css
                      text/comma-separated-values
                      text/javascript
                      application/x-javascript
                      application/atom+xml;

    location /webhook {
        # /webhook* anything takes user to port 5005, api
        proxy_set_header   X-Real-IP  $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   Host $host;
        proxy_pass http://127.0.0.1:5005/webhook;
    }

    ### location / {
    ###     # Here, you can optionally redirect the user to 
    ###     # a landing page explaining the webhook server.
    ###     #
    ###     # ......or not.
    ### }
}
```

The configuration file (full contents given above) should be copied to
(requires sudo access):

```
/etc/nginx/sites-available/archie.conf
```

The site should then be enabled by linking this configuration
file to the `sites-enabled` folder:

```
sudo ln -fs /etc/nginx/sites-available/archie.conf /etc/nginx/sites-enabled/
```

Now nginx can be restarted:

```
sudo service nginx restart
```

