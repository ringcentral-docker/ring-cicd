# base image
FROM public.ecr.aws/docker/library/eclipse-temurin:21-jdk-noble

RUN apt-get update -y \
    && apt-get install -y ca-certificates gnupg \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32 871920D1991BC93C \
    && apt-get install -y openssh-clients git \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*