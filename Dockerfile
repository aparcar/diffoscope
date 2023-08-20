FROM debian:sid-slim

ARG DEBIAN_FRONTEND=noninteractive

ADD [".", "/srv/diffoscope"]
RUN mkdir -p /usr/share/man/man1/ \
&& apt-get update && apt-get install --yes --no-install-recommends \
    build-essential devscripts equivs \
&& mk-build-deps --install --tool 'apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends --yes' /srv/diffoscope/debian/control \
&& apt-get remove --purge --yes \
    build-essential devscripts equivs \
&& rm -rf /srv/diffoscope/debian \
&& rm -rf /var/lib/apt/lists/* \
&& useradd -ms /bin/bash user

USER user
WORKDIR /home/user

ENV PATH="/srv/diffoscope/bin:${PATH}"

ENTRYPOINT ["/srv/diffoscope/bin/diffoscope"]
