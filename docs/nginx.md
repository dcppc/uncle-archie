# nginx and jenkins

## some background

### what is nginx?

nginx is a web server that can allow for a lot more flexibility
in routing domain names and web traffic from the frontend to
various backend servers.

One of the more useful functionalities in nginx is the ability to
set up a reverse proxy.

### what is a reverse proxy?

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

## installing nginx

recommend using your operating system's package manager.

```
apt-get install nginx
```

On ubuntu, this will install configuration files to

```
/etc/nginx/
```

and will make nginx a service that can be started/stopped with:

```
sudo service nginx start
sudo service nginx stop
```

## nginx configuration

What follows is an nginx configuration file for
using Jenkins behind an nginx reverse proxy, and
making it available via a subdomain like `jenkins.mysite.com`.

Here is the nginx configuration file and the location
on disk where it should be using an aptitude-installed
nginx:

**`/etc/nginx/sites-available/jenkins.conf`**

```plain
# jenkins service is available at localhost:8080

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


