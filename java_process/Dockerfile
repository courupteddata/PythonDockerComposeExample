FROM amazoncorretto:11-alpine-full as builder

WORKDIR /app

COPY java_process/.mvn/ .mvn
COPY java_process/mvnw java_process/pom.xml ./
RUN ./mvnw dependency:resolve

COPY java_process/src ./src
RUN ./mvnw clean compile assembly:single

FROM amazoncorretto:11-alpine-full
WORKDIR /app
COPY --from=builder /app/target/rabbitmq-producer-consumer-1.0-SNAPSHOT.jar /app/

CMD [ "java", "-jar", "/app/rabbitmq-producer-consumer-1.0-SNAPSHOT.jar" ]



