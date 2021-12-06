FROM golang:1.17.4-alpine3.15 AS build

COPY src/ /src
WORKDIR /src
RUN go build && apk add g++ && cd /src/schema/bin && ./build.sh

FROM alpine
WORKDIR /app

COPY --from=build /src/resoccessor /app/
COPY --from=build /src/schema/bin/schema /app/schema/bin/
RUN apk add g++

CMD ["./resoccessor"]

