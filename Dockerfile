FROM php:7.4-apache

LABEL org.opencontainers.image.title="ghas-ado-logic-app PHP container scanning demo"
LABEL org.opencontainers.image.description="Legacy PHP 7.4 Apache image with intentionally outdated Composer packages so GHAS container scanning shows realistic findings."

WORKDIR /var/www/html

RUN apt-get update \
    && apt-get install -y --no-install-recommends git unzip libzip-dev \
    && docker-php-ext-install zip \
    && rm -rf /var/lib/apt/lists/*

COPY --from=composer:2.2 /usr/bin/composer /usr/local/bin/composer
ENV COMPOSER_ALLOW_SUPERUSER=1

WORKDIR /var/www/demo
COPY container-demo/composer.json ./composer.json
RUN composer install --no-dev --prefer-dist --no-interaction

WORKDIR /var/www/html
COPY container-demo/index.php ./index.php
COPY container-demo/config-example.php ./config-example.php
RUN cp -R /var/www/demo/vendor ./vendor \
    && cp /var/www/demo/composer.json ./composer.json \
    && cp /var/www/demo/composer.lock ./composer.lock

EXPOSE 80
