# Zoneton Lodge Public Website
This repository houses the source code for the public website of Zoneton Lodge No. 964. The 
Technology Committee has made this public for educational purposes in case it may be of interest
to other Lodges or organizations interested in using Python, Django, or wagtail for their own web
presence. Pull requests may be accepted as well.

## Licensing
All of the code used is open-sourced under the BSD license (Django, wagtail, etc.) **except for the 
HTML theme**. We have used the `NativeChurch` theme which is requires a purchased license to use.
The theme may be purchased at https://themeforest.net/item/nativechurch-responsive-html5-template/7010838

## Development
While our website was designed to be run on a RedHat based Linux server using the `podman` 
container system and `systemd` for orchestration, development is mostly Windows & Docker friendly.
Included in the base is a `docker-compose.yaml` file for this purpose.

### Development vs. Production Settings files
Wagtail uses the `DJANGO_SETTINGS_MODULE` to determine whether Django should use dev.py or 
production.py. The `Dockerfile` is built for production by default, but is overridden in the 
`docker-compose.yaml` for development. 

To set this by hand, use: `DJANGO_SETTINGS_MODULE: 'zoneton_lodge.settings.dev'`

### Setting up a development environment on Windows
- Ensure Windows Subsystem for Linux (WSL) is installed
- Install and enable Docker for Windows
- Clone this repository
- Run `docker-compose up`
- Set up a super user for development: 
```bash 
$ docker-compose exec web python manage.py migrate
```
- Run database migrations:
```bash
$ docker-compose exec web python manage.py createsuperuser
```

### Database migrations
Generating migration files and running them has to be done inside the container.
```bash
$ docker-compose exec web python manage.py makemigrations
$ docker-compose exec web python manage.py migrate
```

### Updating dependencies
Dependencies are installed from `requirements.txt` when the container is built. To update the file:
```bash
$ pip freeze > /tmp/requirements.txt
```

## Deployment
Our deployment does require a RedHat based Linux server with `podman`, postgreSQL, and a 
reverse-proxy provider (i.e. nginx) webserver already in place.

### Required Secrets
In order to run in production, credentials for the database, email server, etc. must be deployed
into the `secrets` subsystem for `podman`. These can be added as follows:

```bash
$ printf <secret> | podman secret create secret_name - 
```

This will cause the secret to be mounted inside the container as `/run/secrets/secret_name` when 
the `--secret source=secret_name,uid=1000,gid=1000,mode=600` flag is used.

| Secret Name | Purpose                              | Required |
| :---        |            :---:                     |   :---:  |
| zoneton_db_user | The postgresql username to use | Yes |
| zoneton_db_pass | The postgresql password to use | Yes |
| zoneton_db_name | Name of the postgresql production database | Yes |
| zoneton_db_host | The hostname of the database server | Yes |
| zoneton_db_port | TCP port for the database (default `5432`) | No |
| zoneton_storage_id | AWS compatible key_id for file storage | Yes |
| zoneton_storage_key | AWS compatible key for file storage | Yes |
| zoneton_storage_bucket | AWS compatible name for the storage bucket | Yes |
| zoneton_secret_key | Django secret key | Yes |

### Initial setup
- Create a database user and database for the website
- Add the necessary reverse-proxy definitions to the web server
- Clone this repository to an unprivileged user's project directory
- Run the initial deployment script to build the container (and for static files, etc.)
```bash
$ ./deploy.sh
```
- Create the super user account
```bash
$ podman exec -it pod-zoneton /bin/bash
$(container) python manage.py createsuperuser
$(container) exit
```

### Deploying Updates
The systemd unit file is already configured to use `auto-update` facilities in `podman`. When the 
local image is updated (when the `deploy.sh` script runs `podman build`), auto-update will restart
the service using the new image.
- Pull the latest changes from this repository
- Run `./deploy.sh`

# Other Notes
## Building the Container by hand
Use something close to this:
```bash
$ podman build --tag wagtail-zoneton:latest -f Containerfile .
```
