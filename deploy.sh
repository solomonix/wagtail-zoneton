#!/bin/bash

# (Re)build the container image
podman build --tag pod-zoneton:latest -f Containerfile .

# Call auto-update to restart the container using the new image
podman auto-update

# Run static file collection
podman exec pod-zoneton python manage.py migrate
