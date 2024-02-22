FROM node:lts

# Create app directory
WORKDIR /js

# Install app dependencies
COPY package*.json ./
RUN npm install

# Bundle app source
COPY sql-test.js ./
# COPY . .

# Run the app
CMD [ "node", "sql-test.js" ]
