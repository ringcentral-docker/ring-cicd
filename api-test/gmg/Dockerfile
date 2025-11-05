# Build stage: Install dependencies and tools
ARG JACOCO_VERSION=0.8.13
ARG DOCKER_REGISTRY=ghcr.io
FROM ${DOCKER_REGISTRY}/ringcentral-docker/jdk/jdk:17.0.13 AS builder

# Install required tools (minimized)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        python3 \
        ca-certificates \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set working directory
WORKDIR /app

# Copy Gradle wrapper files (these rarely change)
COPY ./gradlew .
COPY ./gradlew.bat .
COPY ./gradle/ gradle/
COPY ./gradle.properties .

# Copy build configuration files (these rarely change)
COPY ./build.gradle .
COPY ./settings.gradle .

# Set Gradle cache directory
ENV GRADLE_USER_HOME=/app/.gradle

# Pre-download dependencies
RUN ./gradlew dependencies --no-daemon --stacktrace --info && \
    ./gradlew --no-daemon --stacktrace --info

# Download Jacoco agent and CLI using updated script
ENV JACOCO_VERSION=${JACOCO_VERSION:-0.8.13}
COPY ./jacoco/download-jacoco.sh /app/jacoco/download-jacoco.sh
RUN chmod +x /app/jacoco/download-jacoco.sh && \
    mkdir -p /app/tools/jacoco && \
    cd /app/jacoco && JACOCO_VERSION=${JACOCO_VERSION} ./download-jacoco.sh && \
    mv jacocoagent.jar /app/tools/jacoco/jacocoagent.jar && \
    mv jacococli.jar /app/tools/jacoco/jacococli.jar

# Copy Python script for Jacoco to Cobertura conversion (if exists)
# COPY .gitlab/jacoco_to_cobertura.py /app/tools/

# Set execution permissions
RUN chmod +x gradlew

# Create necessary directories
RUN mkdir -p reports container-classes swagger-coverage-output

# Set environment variables
ENV JAVA_OPTS="-Xmx2g -Xms1g"
ENV GRADLE_OPTS="-Dorg.gradle.daemon=false -Dorg.gradle.parallel=true -Dorg.gradle.caching=true"

# Runtime stage: Create minimal runtime image
FROM ${DOCKER_REGISTRY}/ringcentral-docker/jdk/jdk:17.0.13 AS runtime

# Install runtime tools only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        python3 \
        ca-certificates \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

# Copy necessary files from builder stage
COPY --from=builder /app/gradlew .
COPY --from=builder /app/gradle/ gradle/
COPY --from=builder /app/gradle.properties .
COPY --from=builder /app/build.gradle .
COPY --from=builder /app/settings.gradle .
COPY --from=builder /app/.gradle .gradle
COPY --from=builder /app/tools/ tools/
COPY --from=builder /app/jacoco/ jacoco/

# Set execution permissions
RUN chmod +x gradlew

# Create necessary directories
RUN mkdir -p reports container-classes swagger-coverage-output

# Set environment variables
ENV JAVA_OPTS="-Xmx2g -Xms1g"
ENV GRADLE_OPTS="-Dorg.gradle.daemon=false -Dorg.gradle.parallel=true -Dorg.gradle.caching=true"

