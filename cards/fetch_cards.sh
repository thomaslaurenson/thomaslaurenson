#!/bin/bash


# Set username
USERNAME="thomaslaurenson"

# Move to script folder
DIRECTORY=$(dirname "$0")
cd $DIRECTORY

## STATS

# Start github-readme-stats Docker container
echo "[*] Building github-readme-stats Docker environment..."
PROJECT="github-readme-stats"
cd "$PROJECT"
source .env
docker image build -t "$PROJECT" --build-arg PAT_1=$PAT_1 .
docker run --name "$PROJECT" --env-file .env -p 9000:9000 -d "$PROJECT"

echo "[*] Waiting for API to be available..."
sleep 10

# Query local API for GitHub stats cards
echo "[*] Fetching github_stats_card..."
curl "http://localhost:9000/?username=$USERNAME&count_private=true&hide_border=true&bg_color=00000000&title_color=FFFFFF&text_color=FFFFFF&show_icons=true&icon_color=FF8300&ring_color=FF8300" -o ../github_stats_card_dark.svg

curl "http://localhost:9000/?username=$USERNAME&count_private=true&hide_border=true&bg_color=FFFFFFFF&title_color=000000&text_color=000000&show_icons=true&icon_color=FF8300&ring_color=FF8300" -o ../github_stats_card_light.svg

# Query local API for GitHub top languages cards
echo "[*] Fetching languages_card..."
curl "http://localhost:9000/top-langs?username=$USERNAME&count_private=true&hide=tex,html&layout=donut&hide_border=true&bg_color=00000000&title_color=FFFFFF&text_color=FFFFFF" -o ../github_languages_card_dark.svg

curl "http://localhost:9000/top-langs?username=$USERNAME&count_private=true&hide=tex,html&layout=donut&hide_border=true&bg_color=FFFFFF&title_color=000000&text_color=000000" -o ../github_languages_card_light.svg

# Stop github-readme-stats Docker container and delete everything
echo "[*] Destroying github-readme-stats Docker environment..."
docker container stop github-readme-stats
docker container rm github-readme-stats
docker image rm github-readme-stats
cd ..

## STREAKS

# Start github-readme-streak-stats Docker container
echo "[*] Building github-readme-streak-stats Docker environment..."
PROJECT="github-readme-streak-stats"
cd "$PROJECT"
docker image build -t "$PROJECT" .
docker run --name "$PROJECT" -p 8080:80 -d "$PROJECT"

echo "[*] Waiting for API to be available..."
sleep 10

# Query streak API
echo "[*] Fetching streak_card..."
curl -L "http://localhost:8080/github-readme-streak-stats/src?user=$USERNAME&theme=dark&hide_border=true&date_format=M%20j%5B%2C%20Y%5D&exclude_days=Sun%2CSat&background=00000000" -o ../github_streak_card_dark.svg

curl -L "http://localhost:8080/github-readme-streak-stats/src?user=$USERNAME&theme=default&hide_border=true&date_format=M%20j%5B%2C%20Y%5D&exclude_days=Sun%2CSat&background=00000000" -o ../github_streak_card_light.svg

# Stop github-readme-streak-stats Docker container and delete everything
echo "[*] Destroying github-readme-streak-stats Docker environment..."
docker container stop github-readme-streak-stats
docker container rm github-readme-streak-stats
docker image rm github-readme-streak-stats
cd ..
