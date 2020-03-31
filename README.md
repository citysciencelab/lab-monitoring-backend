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

POST only valid JSON with ```Content-Type: application/json```.

POST a username in field ```nm``` to ```/login``` to get the string user id from the database. If the user does not exist yet, it will be created.

POST your data in field ```data``` to ```/submit```

#### Analysis API

```/num_submissions``` ```day|day_start,day_end``` reports the number of total submissions for a given day or day range.

```/aggregate``` ```[day_start day_end] key... aggregate...``` Returns a JSON data series of the given key(s), aggregated according to the function specified wiht ```aggregate```. You can supply a single aggregate for all keys or the same number of aggregates as keys. If you don't supply day_start, it will get all data from March 1st on. If you don't supply day_end, it will collect entries until today.

```/aggregate_plot``` ```[day_start day_end] key... aggregate...``` same as /aggregate, put returns a pygal plot instead.

```/user_timeline``` ```[day_start day_end] key... id``` returns a JSON time series with the values of the given key(s) of a single user (not aggregated).

```/user_plot``` ```[day_start day_end] key... id``` same as /user_timeline, but as pygal plot.

#### Aggregate Functions

* average
* max
* min
* all [not implemented for plotting yet]

### Configuration
