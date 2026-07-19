# Stage 1: Build the binary from local source
FROM golang:1.24-alpine AS builder
RUN apk add --no-cache git

# Copy local source code into the container
COPY source/ /go/src/snowflake
WORKDIR /go/src/snowflake/proxy

# Build the binary
RUN go build -o /snowflake-proxy .

# Stage 2: Create the minimal runtime image
FROM alpine:3.19
RUN apk add --no-cache ca-certificates

# Copy the binary from the builder
COPY --from=builder /snowflake-proxy /usr/bin/snowflake-proxy
COPY docker_entrypoint.sh /docker_entrypoint.sh
RUN chmod +x /docker_entrypoint.sh

ENTRYPOINT ["/docker_entrypoint.sh"]
