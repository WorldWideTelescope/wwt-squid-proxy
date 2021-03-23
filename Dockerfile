# Copyright 2020-2021 the .NET Foundation
# Licensed under the MIT License
#
# To check what version of Squid is currently out for 20.10, see:
# https://packages.ubuntu.com/groovy/squid

FROM ubuntu:20.10

ENV SQUID_VERSION=4.13 \
    SQUID_CACHE_DIR=/var/spool/squid \
    SQUID_LOG_DIR=/var/log/squid \
    SQUID_USER=proxy

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y \
      python3-tornado \
      squid=${SQUID_VERSION}* \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /sbin/entrypoint.sh
RUN chmod 755 /sbin/entrypoint.sh

ADD squid.conf /etc/squid/squid.conf

ADD fetcher.py /fetcher.py
RUN chmod +x /fetcher.py

EXPOSE 80/tcp
ENTRYPOINT ["/sbin/entrypoint.sh"]
