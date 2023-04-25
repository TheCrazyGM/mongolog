# How to run as a systemd service using a unix socket

```ini
[Unit]
Description=Mongolog Viewer
After=network.target

[Service]
User=<username>
WorkingDirectory=/path/to/app
ExecStart=/path/to/venv/bin/gunicorn --workers 3 --bind unix:/tmp/mongolog.sock app:app

[Install]
WantedBy=multi-user.target
```

## To change the port of the Flask app service for systemd, you need to modify the ExecStart command in the

[Service] section of the unit file. Here's an example of how to change the port to 8080:

```ini
[Service]
User=<username>
WorkingDirectory=/path/to/app
ExecStart=/path/to/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8080 app:app
```

Note that we changed the --bind option to 0.0.0.0:8080, which means the app will listen on all available
network interfaces on port 8080. You can replace 8080 with any other port number you prefer. After making the
changes, save the file and reload the systemd daemon with the command:

`sudo systemctl daemon-reload`

Then restart the service with:

`sudo systemctl restart <service-name>`

Replace <service-name> with the actual name of your service.

## how would i do the reverse proxy with the /tmp/mongolog.sock using nginx

To set up a reverse proxy with Nginx for your Flask app using the /tmp/mongolog.sock socket, you can follow  
these steps:

1 Install Nginx on your server if it's not already installed:

```sh
    sudo apt-get update
    sudo apt-get install nginx
```

2 Create a new Nginx server block configuration file for your Flask app:

```sh
    sudo nano /etc/nginx/sites-available/myapp
```

Replace myapp with a name of your choice.  
 3 Add the following configuration to the file:

```nginx
server {
listen 80;
server_name example.com; # Replace with your domain name

       location / {
           proxy_pass http://unix:/tmp/mongolog.sock;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }

```

This configuration tells Nginx to listen on port 80 for requests to your domain name, and to proxy those
requests to the Unix socket at /tmp/mongolog.sock. The proxy_set_header directives are used to pass along
the original client IP address and other headers to your Flask app.

4 Save and close the file.

5 Create a symbolic link to enable the new server block:

```sh
   sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
```

6 Test the Nginx configuration:

```sh
    sudo nginx -t
```

If there are no errors, reload Nginx to apply the changes:

```sh
    sudo systemctl reload nginx
```

That's it! Your Flask app should now be accessible through Nginx at your domain name.
