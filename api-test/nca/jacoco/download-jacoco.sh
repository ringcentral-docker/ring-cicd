#!/bin/bash

# Download Jacoco agent and CLI
# Use JACOCO_VERSION from environment variable or default to 0.8.10
JACOCO_VERSION="${JACOCO_VERSION:-0.8.13}"
JACOCO_AGENT_URL="https://repo1.maven.org/maven2/org/jacoco/org.jacoco.agent/${JACOCO_VERSION}/org.jacoco.agent-${JACOCO_VERSION}-runtime.jar"
JACOCO_CLI_URL="https://repo1.maven.org/maven2/org/jacoco/org.jacoco.cli/${JACOCO_VERSION}/org.jacoco.cli-${JACOCO_VERSION}-nodeps.jar"

echo "Downloading Jacoco agent and CLI version ${JACOCO_VERSION}..."
echo "Agent URL: ${JACOCO_AGENT_URL}"
echo "CLI URL: ${JACOCO_CLI_URL}"

# Download agent with retry mechanism
max_attempts=3
attempt=1
while [ $attempt -le $max_attempts ]; do
    echo "Attempt $attempt: Downloading JaCoCo agent..."
    if curl -L --connect-timeout 30 --max-time 300 -o jacocoagent.jar ${JACOCO_AGENT_URL}; then
        echo "JaCoCo agent downloaded successfully!"
        break
    else
        echo "Attempt $attempt failed, retrying..."
        sleep 5
        attempt=$((attempt + 1))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ Failed to download JaCoCo agent after $max_attempts attempts"
    exit 1
fi

# Download CLI with retry mechanism
attempt=1
while [ $attempt -le $max_attempts ]; do
    echo "Attempt $attempt: Downloading JaCoCo CLI..."
    if curl -L --connect-timeout 30 --max-time 300 -o jacococli.jar ${JACOCO_CLI_URL}; then
        echo "JaCoCo CLI downloaded successfully!"
        break
    else
        echo "Attempt $attempt failed, retrying..."
        sleep 5
        attempt=$((attempt + 1))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ Failed to download JaCoCo CLI after $max_attempts attempts"
    exit 1
fi

echo "✅ Both JaCoCo agent and CLI downloaded successfully!"

