# syntax=docker/dockerfile:1
#
# Static public site. It makes no API calls, so there is no ARG or ENV for an API
# URL here: the image builds and runs with no backend and no credentials.

FROM node:18-alpine

ENV NODE_ENV=production

WORKDIR /app

COPY package*.json ./
RUN npm ci

# .dockerignore keeps node_modules and the archived _inactive/ tree out of the
# build context, so this is only the site source.
COPY . .
RUN npm run build

RUN chown -R node:node /app/.next
USER node

EXPOSE 3000

CMD ["npm", "start"]
