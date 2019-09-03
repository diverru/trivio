FROM ubuntu:18.04

LABEL maintainer="Alexander Kiselyov"

USER root
ENV HOME /root
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONPATH /trivio_backend
WORKDIR /trivio_backend

RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections \
    && apt-get update -qq \
    && apt-get install -y -qq --no-install-recommends \
        python3 python3-pip locales python3-setuptools python3-dev sqlite3 \
    && pip3 install wheel \
    && apt-get -qq clean \
    && dpkg-reconfigure locales && locale-gen en_US.UTF-8 && locale-gen ru_RU.UTF-8 \
    && apt-get -qq autoremove \
    && rm -rf /var/lib/apt/lists/* /var/tmp/*

COPY docker/trivio_backend/requirements.txt /
RUN pip3 install -r /requirements.txt \
    && rm -rf /root/.cache/pip/*

COPY docker/trivio_backend/gunicorn.conf.py /
#TODO: COPY trivio_backend /trivio_backend

CMD ["/usr/local/bin/gunicorn", "backend.wsgi:application", "-c", "/gunicorn.conf.py"]

