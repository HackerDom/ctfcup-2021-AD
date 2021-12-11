FROM golang:1.17.5-stretch AS build

COPY src/ /src
WORKDIR /src
RUN go build && apt update && apt install g++ -y

FROM ubuntu
WORKDIR /app

COPY --from=build /src/resoccessor /app/
COPY --from=build /src/schema/bin/schema /app/schema/bin/
COPY --from=build /src/server/static /app/server/static/
COPY --from=build /src/server/templates /app/server/templates/
RUN apt update && apt install g++ -y

CMD ["./resoccessor"]

