# Nginx and Jenkins

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
any requests for , say, `https://jenkins.mydomain.com` can be reverse 
proxied to `http://localhost:8080/`, where an instance of Jenkins
is running.

The advantage of this is that Jenkins is not accessible via port
8080 to outside users. Every request must pass through nginx.

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

**Jenkins runs on port 8080 and is available at
`localhost:8080`.**

## Nginx Standard Configuration

The "standard configuration" for nginx is to use port 443 for
HTTPS, port 80 for HTTP, and to automatically redirect HTTP
requests on port 80 to the more secure port 443.

The nginx configuration file below sets up nginx as a 
reverse proxy in front of Jenkins, and makes it available 
via a subdomain like `jenkins.mysite.com`.

Here is the nginx configuration file and the location
on disk where it should be using an aptitude-installed
nginx:

**`/etc/nginx/sites-available/jenkins.conf`**

```plain
server {
    listen 80;
    listen [::]:80;
    server_name jenkins.mydomain.com;
    location / {
        return 301 https://jenkins.mydomain.com$request_uri;
    }
}

server {
    listen 443;
    listen [::]:443;
    server_name jenkins.mydomain.com;

    ssl on;
    ssl_certificate /etc/letsencrypt/live/jenkins.mydomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jenkins.mydomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
 
    location / {
        proxy_set_header        Host $host:$server_port;
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header        X-Forwarded-Proto $scheme;
        proxy_redirect http:// https://;
        proxy_pass              http://localhost:8080;
        # Required for new HTTP-based CLI
        proxy_http_version 1.1;
        proxy_request_buffering off;
        proxy_buffering off; # Required for HTTP-based CLI to work over SSL
        # workaround for https://issues.jenkins-ci.org/browse/JENKINS-45651
        add_header 'X-SSH-Endpoint' 'jenkins.domain.tld:50022' always;
    }
}
```

### Alternative Nginx Configuration

Alternatively, if you want your server to be publicly available on a non-standard 
port like 8081, but still use SSL, for example being available at

```
https://jenkins.mydomain.com:8081
```

then you can remove the port 80 redirect and change port 443 to 8081:

```
server {
    listen 8081;
    listen [::]:8081;
    server_name jenkins.mydomain.com;

    ssl on;
    ssl_certificate /etc/letsencrypt/live/jenkins.mydomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jenkins.mydomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
 
    location / {
        proxy_set_header        Host $host:$server_port;
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header        X-Forwarded-Proto $scheme;
        proxy_redirect http:// https://;
        proxy_pass              http://localhost:8080;
        # Required for new HTTP-based CLI
        proxy_http_version 1.1;
        proxy_request_buffering off;
        proxy_buffering off; # Required for HTTP-based CLI to work over SSL
        # workaround for https://issues.jenkins-ci.org/browse/JENKINS-45651
        add_header 'X-SSH-Endpoint' 'jenkins.domain.tld:50022' always;
    }
}
```

The configuration file (full contents given above) should be copied to
(requires sudo access):

```
/etc/nginx/sites-available/jenkins.conf
```

The site should then be enabled by linking this configuration
file to the `sites-enabled` folder:

```
sudo ln -fs /etc/nginx/sites-available/jenkins.conf /etc/nginx/sites-enabled/
```

Now nginx can be restarted:

```
sudo service nginx restart
```

