#!/bin/bash
set -e

# Ensure OPcache directory exists
mkdir -p /tmp/opcache && chmod 777 /tmp/opcache

# Ensure .env exists
if [ ! -f .env ]; then
    cp .env.example .env
fi

# Ensure SQLite database exists
if [ ! -f database/database.sqlite ]; then
    touch database/database.sqlite
fi

# Ensure composer dependencies in native volume
if [ ! -f vendor/autoload.php ]; then
    echo "Installing Composer dependencies in native Linux volume..."
    composer install --no-interaction --prefer-dist
fi

# Ensure APP_KEY
if ! grep -q "APP_KEY=base64:" .env; then
    php artisan key:generate --force
fi

# Ensure migrations
php artisan migrate --force

# Ensure npm dependencies in native volume
if [ ! -f "node_modules/@tailwindcss/oxide-linux-x64-gnu/package.json" ]; then
    echo "Installing NPM dependencies in native Linux volume..."
    npm install
fi

# Generate Wayfinder types
php artisan wayfinder:generate --with-form || true

exec "$@"
