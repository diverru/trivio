FROM ubuntu:18.04

LABEL maintainer="Alexander Kiselyov"

USER root
ENV HOME /root
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONPATH /trivio_bot
WORKDIR /trivio_bot

RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections \
    && apt-get update -qq \
    && apt-get install -y -qq --no-install-recommends \
        python3 python3-pip python3-setuptools \
    && pip3 install wheel \
    && apt-get -qq clean \
    && apt-get -qq autoremove \
    && rm -rf /var/lib/apt/lists/* /var/tmp/*

COPY docker/trivio_bot/requirements.txt /
RUN pip3 install -r /requirements.txt \
    && rm -rf /root/.cache/pip/*

COPY trivio_bot /trivio_bot