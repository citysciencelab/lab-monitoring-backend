# lab-monitoring-backend


### Installation

Requires
* python3
* flask

```pip install -r requirements.txt```

#### nginx configuration

in /etc/nginx/conf.d/your_conf_file.conf:
```
server {
    listen 80 443; # http https
    location = /monitorbackend { rewrite ^ /monitorbackend/; }
    location /monitorbackend { try_files $uri @monitorbackend; }
    location @monitorbackend {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/monitorbackend.sock;
    }
}

$ service nginx reload
```


### uwsgi serve

```
$ uwsgi -s /tmp/monitorbackend.sock --manage-script-name --mount /monitorbackend=api:app --plugin python3
$ sudo chown www-data.www-data /tmp/monitorbackend.sock
```

### Usage

```python api.py``` runs the flask backend-server on port 5000

### Description

### API specification

POST a username in field ```nm``` to ```/login``` to get the string user id from the database. If the user does not exist yet, it will be created.

POST your data in field ```data``` to ````/submit``` (TO DO: more detailed fields)

### Configuration
