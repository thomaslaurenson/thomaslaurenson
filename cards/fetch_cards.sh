#!/bin/bash


# Move to script folder
DIRECTORY=$(dirname "$0")
cd $DIRECTORY

# Query local API for GitHub stats cards
curl "http://localhost:9000/?username=thomaslaurenson&count_private=true&hide_border=true&bg_color=00000000&title_color=FFFFFF&text_color=FFFFFF&show_icons=true&icon_color=FF8300&ring_color=FF8300" -o github_stats_card_dark.svg

curl "http://localhost:9000/?username=thomaslaurenson&count_private=true&hide_border=true&bg_color=FFFFFFFF&title_color=000000&text_color=000000&show_icons=true&icon_color=FF8300&ring_color=FF8300" -o github_stats_card_light.svg

# Query local API for GitHub top languages cards
curl "http://localhost:9000/top-langs?username=thomaslaurenson&count_private=true&hide=tex,html&layout=donut&hide_border=true&bg_color=00000000&title_color=FFFFFF&text_color=FFFFFF" -o github_languages_card_dark.svg

curl "http://localhost:9000/top-langs?username=thomaslaurenson&count_private=true&hide=tex,html&layout=donut&hide_border=true&bg_color=FFFFFF&title_color=000000&text_color=000000" -o github_languages_card_light.svg

# Query streak API
curl "https://streak-stats.demolab.com?user=thomaslaurenson&theme=dark&hide_border=true&date_format=M%20j%5B%2C%20Y%5D&exclude_days=Sun%2CSat&background=00000000" -o github_streak_card_dark.svg

curl "https://streak-stats.demolab.com?user=thomaslaurenson&theme=default&hide_border=true&date_format=M%20j%5B%2C%20Y%5D&exclude_days=Sun%2CSat&background=00000000" -o github_streak_card_light.svg
