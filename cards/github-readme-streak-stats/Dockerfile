FROM php:8-apache-bookworm

RUN apt-get update && apt-get install -y \
    git \
    inkscape \
    bash \
    curl \
    libicu-dev \
    libzip-dev

WORKDIR /var/www/html

RUN curl -s https://getcomposer.org/installer | php

# Install PHPs intl extension
RUN docker-php-ext-configure intl
RUN docker-php-ext-install intl

# Install zip extension
RUN docker-php-ext-install zip

WORKDIR /var/www/html

RUN git clone https://github.com/DenverCoder1/github-readme-streak-stats.git

WORKDIR /var/www/html/github-readme-streak-stats
RUN php ../composer.phar install

COPY .env .env

EXPOSE 80
