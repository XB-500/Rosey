FROM python:3.8-slim-buster

RUN mkdir /app
WORKDIR /app
ADD . /app/
RUN pip install -r requirements.txt

RUN apt-get -y update
RUN apt-get -y install git

RUN useradd --create-home chucknorris
USER chucknorris

ENV PYTHONUNBUFFERED=1
ENV LOG_SINK=WASURE


WORKDIR /app/src
ENV PYTHONPATH /app/src
CMD ["python", "/app/src/main.py"]