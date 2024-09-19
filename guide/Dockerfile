# Use the official Python 3.11 image as the base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Set environment variables with default values
ENV DEBIAN_FRONTEND=noninteractive
ENV GECKODRIVER_VER=v0.34.0
ENV FIREFOX_VER=119.0

# Update and install necessary packages
RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y \
        firefox-esr \
        libx11-xcb1 \
        libdbus-glib-1-2 \
        curl \
        tar \
        bzip2 \
    && rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Add the latest Firefox
RUN curl -sSLO "https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VER}/linux-x86_64/en-US/firefox-${FIREFOX_VER}.tar.bz2" \
    && tar -jxf firefox-*.tar.bz2 \
    && mv firefox /opt/ \
    && chmod 755 /opt/firefox \
    && chmod 755 /opt/firefox/firefox

# Add geckodriver
RUN curl -sSLO "https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VER}/geckodriver-${GECKODRIVER_VER}-linux64.tar.gz" \
    && tar zxf geckodriver-*.tar.gz \
    && mv geckodriver /usr/bin/

# Copy the application code into the container
COPY . /app

# Define the default command to run when the container starts
CMD ["python", "main.py"]
