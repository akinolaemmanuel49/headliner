# Base image
FROM python:3.12-slim

# Install cron and supervisor
RUN apt-get update && apt-get install -y cron supervisor

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN python -m venv .venv
RUN .venv/bin/pip install -r requirements.txt

# Copy the cronjob script
COPY headliner.sh /app/headliner.sh
RUN chmod +x /app/headliner.sh

# Add cron job
# RUN echo "*/30 * * * * /bin/bash /app/headliner.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/headliner
RUN echo "* * * * * /bin/bash /app/headliner.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/headliner
RUN chmod 0644 /etc/cron.d/headliner && crontab /etc/cron.d/headliner

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose the Django server port
EXPOSE 8000

# Start supervisor
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
