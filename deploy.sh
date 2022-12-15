#!/bin/bash

# (Re)build the container image
podman build --tag wagtail-zoneton:latest -f Containerfile .

# Stop the service
systemctl --user stop pod-zoneton.service
systemctl --user disable pod-zoneton.service

# Re-deploy the pod-zoneton.service unit file in case it updated
sed -E 's|__HOMEDIR__|'$PWD'|g' pod-zoneton.service > ~/.config/systemd/user/pod-zoneton.service
systemctl --user daemon-reload

# Enable the container (in case it wasn't already) and restart it
systemctl --user enable pod-zoneton.service
systemctl --user start pod-zoneton.service

# Call auto-update to restart the container using the new image
#podman auto-update

# Run migrations
podman exec pod-zoneton python manage.py migrate

# Deploy static files
podman exec pod-zoneton python manage.py collectstatic --noinput

