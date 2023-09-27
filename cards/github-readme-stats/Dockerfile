FROM node:18-alpine

RUN apk add --no-cache git

WORKDIR /app
RUN git clone https://github.com/anuraghazra/github-readme-stats.git
WORKDIR /app/github-readme-stats
RUN npm install
RUN npm install express

EXPOSE 9000

CMD PAT_1="$PAT_1" node express.js
