FROM node:lts

# Install dependencies for pyodbc and pymssql
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    unixodbc \
    unixodbc-dev \
    tdsodbc \
    freetds-dev \
    freetds-bin \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install ODBC Driver 17 and 18 for SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /js

# Install app dependencies
COPY package*.json ./
RUN npm install

# Bundle app source
COPY . .

# Install required packages
RUN npm install mssql odbc

# Run the app
CMD [ "node", "sql-test.js" ]
