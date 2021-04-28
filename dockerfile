FROM python:3.8-slim

RUN mkdir /app
WORKDIR /app
ADD . /app/
RUN pip install -r requirements.txt

EXPOSE 8080
ENV PORT 8080

WORKDIR /app/src
ENV PYTHONPATH /app/src
CMD ["python", "/app/src/main.py"]