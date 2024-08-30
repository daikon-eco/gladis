# backend/Dockerfile
FROM rust:1.70 as builder

WORKDIR /app

RUN apt-get update && apt-get install -y libssl-dev pkg-config

COPY Cargo.toml Cargo.lock ./

# Copy the source code
COPY src ./src
COPY Rocket.toml ./

RUN cargo build --release

# Stage 2: Prepare the final container image
FROM debian:buster-slim

# Create a non-root user and switch to it
RUN useradd -ms /bin/bash appuser
USER appuser

WORKDIR /app

# Copy the build artifacts from the builder stage
COPY --from=builder /app/target/release/backend .

EXPOSE 8000

CMD ["./backend"]