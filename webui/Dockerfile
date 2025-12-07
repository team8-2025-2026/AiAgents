FROM node:18-alpine

WORKDIR /webui

COPY package.json .

RUN npm install

COPY . .

CMD [ "npm", "run", "dev" ]
