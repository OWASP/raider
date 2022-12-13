FROM        python:3.10
MAINTAINER  Daniel Neagaru <daniel@neagaru.com>

ADD . /opt/raider/
RUN pip3 install -e /opt/raider
RUN mkdir -p /root/.config/raider/projects

VOLUME ["/root/.config/raider"]
ENTRYPOINT ["raider"]
