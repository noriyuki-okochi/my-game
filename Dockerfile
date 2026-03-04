FROM python:3.9.5
USER root

RUN apt-get update && apt-get upgrade -y
RUN apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
RUN apt-get install -y \
    x11-apps \
    && rm -rf /var/lib/apt/list/*
RUN apt-get install -y libgl1-mesa-dev
RUN apt-get install -y vim less
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL js_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

RUN mkdir -p /root/python
RUN mkdir -p /root/python/panda3d/src
COPY requirements.txt /root/python
COPY dat/ /root/python/dat/
COPY db/ /root/python/db/
COPY fonts/ /root/python/fonts/
COPY models/ /root/python/models/
COPY reg/ /root/python/reg/
WORKDIR /root/python
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

