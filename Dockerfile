# Download base image ubuntu 18.04
FROM ubuntu:18.04

RUN apt-get install -y python3 python3-pip python3-icu && \
    rm -rf /var/lib/apt/lists/*

ADD . /app
RUN cd /app && pipenv install

# Configure Services and Port
CMD ["./run.sh"]
 
EXPOSE 80 443