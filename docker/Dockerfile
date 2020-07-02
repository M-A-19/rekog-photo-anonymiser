FROM amazonlinux:2018.03

# Need to set "ulimit -n" to a small value to stop yum from hanging:
# https://bugzilla.redhat.com/show_bug.cgi?id=1715254#c1
RUN ulimit -n 1024 && yum -y update && yum -y install \
    git \
    gcc \
    python36 \
    python36-pip \
    python36-devel \
    zip \
    && yum clean all

COPY aws-requirements.txt lambda/aws-requirements.txt
COPY package-requirements.txt lambda/package-requirements.txt
COPY credentials lambda/credentials
COPY packager.sh lambda/packager.sh


RUN python3 -m pip install pip==18.1

# Requirements copied from lambda Python 3.6, but not in base image
# (Plus Cython which is a build-time requirement for numpy)
RUN python3 -m pip install -r lambda/aws-requirements.txt

ENV AWS_DEFAULT_REGION=eu-west-2
ENV AWS_SHARED_CREDENTIALS_FILE=/lambda/credentials

# Make it possible to build numpy:
# https://github.com/numpy/numpy/issues/14147
ENV CFLAGS=-std=c99
