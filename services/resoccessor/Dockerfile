FROM golang:1.17.4-alpine3.15 AS build

COPY src/ /src
WORKDIR /src
RUN go build && apk add g++

FROM alpine
WORKDIR /app

COPY --from=build /src/resoccessor /app/
COPY --from=build /src/schema/bin/schema /app/schema/bin/
COPY --from=build /src/server/static /app/server/static/
COPY --from=build /src/server/templates /app/server/templates/
RUN apk add g++

CMD ["./resoccessor"]

