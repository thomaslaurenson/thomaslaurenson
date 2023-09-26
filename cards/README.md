# thomaslaurenson > cards

Instead of using an API service, all GitHub cards are static and updated periodically.

If you want to use my setup:

- Change the `username` or `user` parameter in the `fetch_cards.sh` script
- Download and start the `github-readme-stats` API
- Run the script using `./fetch_cards.sh`

## Quickstart

The stats and top languages cards are made using the [github-readme-stats](https://github.com/anuraghazra/github-readme-stats) project. Using a local copy, so I can use my own GitHub access token and, therefore, get data from my private repos.

- Create token in GitHub
    - Settings > Developer Settings > Personal access tokens
    - Set the following permissions
    - `repo`: all
    - `user`: all
- Download and start API

```
git clone https://github.com/anuraghazra/github-readme-stats.git
cd github-readme-stats
npm install express
npm install
PAT_1=TOKEN node express.js
```

The streak card is made using the [github-readme-streak-stats](https://github.com/DenverCoder1/github-readme-streak-stats). I use their API directly.

To refresh all cards:

```
./fetch_cards.sh
```
