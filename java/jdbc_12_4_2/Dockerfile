# Stage 1: Compile the Java code
FROM openjdk:22-jdk AS compile
WORKDIR /java12
COPY . .
RUN javac -cp json-simple-1.1.jar ./src/jdbc_12_4_2/JDBC_12_4_2.java

# Stage 2: Create a minimal runtime image
FROM openjdk:22-jdk-slim
WORKDIR /java12
COPY json-simple-1.1.jar /java12/
COPY mssql-jdbc-12.4.2.jre11.jar /java12/
COPY --from=compile /java12/bin/jdbc_12_4_2/ /java12/bin/jdbc_12_4_2/
CMD ["java", "-cp", "/java12/bin:json-simple-1.1.jar:mssql-jdbc-12.4.2.jre11.jar", "jdbc_12_4_2.JDBC_12_4_2"]
