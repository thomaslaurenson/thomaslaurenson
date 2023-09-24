# thomaslaurenson > data

Collection of Python programs to dump data from GitHub and make custom charts for this repo

## Quickstart

Make a personal access token (under Settings > Developer Settings > Personal access tokens) with the following permissions:

- `repo`: all
- `admin:org` `read:org`

```
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
python3 top_languages.py -p html tex lua -c 5 -l -r thomaslaurenson/arduino-lmic -v
```
