# base image
FROM public.ecr.aws/docker/library/amazoncorretto:17-al2023-jdk

RUN dnf update -y \
    && dnf install -y openssh-clients git \
    && dnf autoremove -y \
    && rm -rf /var/lib/dnf/lists/*