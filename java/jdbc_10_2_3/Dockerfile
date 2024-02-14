# Stage 1: Compile the Java code
FROM openjdk:22-jdk AS compile
WORKDIR /java10
COPY . .
RUN javac -cp json-simple-1.1.jar ./src/jdbc_10_2_3/JDBC_10_2_3.java

# Stage 2: Create a minimal runtime image
FROM openjdk:22-jdk-slim
WORKDIR /java10
COPY json-simple-1.1.jar /java10/
COPY mssql-jdbc-10.2.3.jre17.jar /java10/
COPY --from=compile /java10/bin/jdbc_10_2_3/ /java10/bin/jdbc_10_2_3/
CMD ["java", "-cp", "/java10/bin:json-simple-1.1.jar:mssql-jdbc-10.2.3.jre17.jar", "jdbc_10_2_3.JDBC_10_2_3"]
