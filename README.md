# Test Trading System

This repository contains a minimal example of a trading system. The project can be containerised using Docker.

## Environment configuration

Default environment variables are provided in `.env.sample`. Copy this file to `.env` and adjust any values as needed. The `docker-compose` command automatically loads variables from `.env`, letting you override the defaults in `docker-compose.yml`.

```
cp .env.sample .env
# edit .env if required
```

## Building containers

```
docker-compose build
```

## Running services

```
docker-compose up
```

This will start the strategy service along with Redis, Prometheus, Grafana and Loki.
