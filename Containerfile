# start with a common base stage for dependencies
FROM python:3-slim AS base
LABEL org.zonetonlodge.image.authors="harlen@harlencompton.com"

# turn off .pyc files and stdout buffering, PORT is used by gunicorn
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# create the builder image for later and add build-deps
FROM base AS builder
RUN apt-get update --yes --quiet && \
    apt-get install --yes --quiet --no-install-recommends \
        build-essential \
        libpq-dev \
        python3-dev \
        libpq-dev \
        libjpeg62-turbo-dev \
        zlib1g-dev \
        libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# We need the application server too
RUN pip install --upgrade pip
COPY ./requirements.txt /tmp/requirements.txt
RUN pip install --no-warn-script-location --prefix=/install -r /tmp/requirements.txt
RUN pip install --no-warn-script-location --prefix=/install gunicorn

# Move on to our deployable image stage
# Setup our app workdir, permissions, etc.
FROM base
COPY --from=builder /install /usr/local
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN useradd zoneton
RUN chown -R zoneton:zoneton /usr/src/app

# Now move the app code.
COPY --chown=zoneton:zoneton ./src /usr/src/app

# Switch to the "zoneton" user for some isolation
USER zoneton

# Set the mode to use PROD
ENV DJANGO_SETTINGS_MODULE="zoneton_lodge.settings.production"

# Finally, run the app
EXPOSE 8000
CMD ["gunicorn", "--workers 3", "zoneton_lodge.wsgi:application"]
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

