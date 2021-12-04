FROM gradle:7.1.0-jdk16 as build
COPY . /home/gradle/src
WORKDIR /home/gradle/src
RUN gradle build --no-daemon 

FROM openjdk:16-jdk-alpine
EXPOSE 8080
RUN mkdir /app
COPY --from=build /home/gradle/src/build/libs/*.jar /usr/app/ATM.jar
ENTRYPOINT ["java","-jar", "/usr/app/ATM.jar", "-Xmx1G"]