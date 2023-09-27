# thomaslaurenson > cards

Instead of using an API service, all GitHub cards are static SVG files and updated periodically.

## Overview

The stats and top languages cards are made using the [github-readme-stats](https://github.com/anuraghazra/github-readme-stats) project. This project is run locally using a Docker container - as this allows the use of my own GitHub access token, and access to stats from my private repos.

The streak card is made using the [github-readme-streak-stats](https://github.com/DenverCoder1/github-readme-streak-stats).

## Prerequisites

- Bash, or similar shell
- Docker
- Curl

## Quickstart

- Create token in GitHub
    - Settings > Developer Settings > Personal access tokens
    - Set the following permissions
    - `repo`: all
    - `user`: all
- Clone repo
    - `git clone https://github.com/thomaslaurenson/thomaslaurenson.git`
    - `cd thomaslaurenson/cards`
- Put token in: `github-readme-syats/.env` file
- Change the `USERNAME` variable in the `fetch_cards.sh` script
- Run the script using `./fetch_cards.sh`
