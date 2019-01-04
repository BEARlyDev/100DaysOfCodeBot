# Download base image ubuntu 18.04
FROM python:3.6

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN apt-get update
RUN apt-get install -y libicu57 libicu-dev
RUN pip3 install pipenv

ADD . /app
RUN cd /app && pipenv install

# Configure Services and Port
CMD ["./run.sh"]
 
EXPOSE 80 443