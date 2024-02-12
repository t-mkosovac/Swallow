FROM python:3.8

# Install dependencies for pyodbc and pymssql
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    tdsodbc \
    freetds-dev \
    freetds-bin \
    && apt-get clean

# Install ODBC Driver 17 and 18 for SQL Server

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 msodbcsql18

# Install pyodbc and pymssql
RUN pip install pyodbc pymssql

# Copy your Python code to the container
COPY sql-test.py /py/sql-test.py

# Set the working directory
WORKDIR /py

# Run your Python code
CMD ["python", "sql-test.py"]
