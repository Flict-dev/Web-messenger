FROM node:latest

WORKDIR /

EXPOSE 3000
COPY package.json ./
COPY package-lock.json ./

RUN npm install
COPY . ./

CMD ["npm", "start"]