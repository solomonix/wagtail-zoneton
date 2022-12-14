QUICK NOTES - FORMAT THIS LATER

Building the container
Use something close to this:

$ docker build --tag wagtail-zoneton:latest -f Containerfile .


Django Settings Environment Variable
This needs to be set to "zoneton_lodge.settings.production" for production settings to take over
(it defaults to "zoneton_lodge.settings.dev" in wsgi.py)


Database Migrations
For right now, spin up a container and access the command line, run migrations
i.e. podman run -itd -v $PWD/src:/usr/src/app wagtail-zoneton:latest /bin/bash
$ python manage.py makemigrations
$ python manage.py migrate


Updating dependencies
Same story, do this with a container image:
podman run -itd -v $PWD/src:/usr/src/app -v $PWD/requirements.txt:/tmp/requirements.txt wagtail-zoneton:latest /bin/bash
$ pip freeze > /tmp/requirements.txt


Quick Start Development Environment
Since I'm still on Windows, I set up docker-compose to spin up an environment to hack on. 
Just run "docker-compose up" and you're off to the races. Start a super user and migrations with:

$ docker-compose exec web python manage.py migrate
$ docker-compose exec web python manage.py createsuperuser
