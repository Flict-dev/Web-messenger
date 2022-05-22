FROM node:16.0.0

WORKDIR /

EXPOSE 3000
COPY package.json ./
COPY package-lock.json ./

RUN npm install
COPY . ./

CMD ["npm", "start"]