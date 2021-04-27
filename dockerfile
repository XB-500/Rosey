FROM python:3-slim AS build-env
ADD . /app
WORKDIR /app

COPY src app
COPY requirements.txt /temp/
RUN pip install --target=/app -r /temp/requirements.txt
RUN useradd -u 8877 gvauser

FROM gcr.io/distroless/python3
COPY --from=build-env /app /app

EXPOSE 8080
ENV PORT 8080

#USER gvauser
WORKDIR /app
CMD ["main.py"]