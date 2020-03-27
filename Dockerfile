# Copyright 2020 the .NET Foundation
# Licensed under the MIT License

FROM ubuntu:19.10

ENV SQUID_VERSION=4.8-1ubuntu2.1 \
    SQUID_CACHE_DIR=/var/spool/squid \
    SQUID_LOG_DIR=/var/log/squid \
    SQUID_USER=proxy

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y \
      liburi-perl \
      squid=${SQUID_VERSION}* \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /sbin/entrypoint.sh
RUN chmod 755 /sbin/entrypoint.sh

ADD squid.conf /etc/squid/squid.conf

ADD rewriter.pl /rewriter.pl
RUN chmod +x /rewriter.pl

EXPOSE 80/tcp
ENTRYPOINT ["/sbin/entrypoint.sh"]
