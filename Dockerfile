# BUILD

FROM python:3.6-alpine as builder

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN apk add bash
RUN apk add \
	python3 python3-dev \
	openssl openssl-dev ca-certificates \
    build-base libffi libffi-dev \
    icu-dev
RUN pip3 install pipenv

ADD . /build
WORKDIR /build

ENV PIPENV_VENV_IN_PROJECT 1

RUN pipenv install --deploy --system

RUN \
    apk del build-base libffi-dev openssl-dev python3-dev && \
    rm -rf /var/cache/apk/* && \
    rm -rf ~/.cache/ && \
    adduser -D -u 1001 noroot

USER noroot

# Configure Services and Port
CMD ["./run.sh"]
 
EXPOSE 80 443