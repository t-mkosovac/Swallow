# Stage 1: Compile the Java code
FROM openjdk:22-jdk AS compile
WORKDIR /java11
COPY . .
RUN javac -cp json-simple-1.1.jar ./src/jdbc_11_2_3/JDBC_11_2_3.java

# Stage 2: Create a minimal runtime image
FROM openjdk:22-jdk-slim
WORKDIR /java11
COPY json-simple-1.1.jar /java11/
COPY mssql-jdbc-11.2.3.jre18.jar /java11/
COPY --from=compile /java11/bin/jdbc_11_2_3/ /java11/bin/jdbc_11_2_3/
CMD ["java", "-cp", "/java11/bin:json-simple-1.1.jar:mssql-jdbc-11.2.3.jre18.jar", "jdbc_11_2_3.JDBC_11_2_3"]
