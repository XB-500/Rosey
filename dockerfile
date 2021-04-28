FROM python:3-slim
ADD . /app
WORKDIR /app

COPY src /app
COPY requirements.txt .
RUN pip install -r ./requirements.txt
RUN useradd -u 8877 gvauser

EXPOSE 8080
ENV PORT 8080

USER gvauser
WORKDIR /app
ENV PYTHONPATH /app
CMD ["/app/main.py"]