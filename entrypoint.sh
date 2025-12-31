#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

# Run migrations and collectstatic for production
if [ "$DJANGO_SETTINGS_MODULE" = "MyPortfolio.settings.production" ]; then    
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

# Execute the passed command
exec "$@"
