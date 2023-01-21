#Builder
FROM python:3.11.1-alpine3.17 as builder
WORKDIR /app
COPY requirements.txt /app
RUN apk --no-cache add postgresql-dev gcc python3-dev musl-dev openssl && \
    pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Generate Certificates
RUN mkdir certificates && \
    openssl req -newkey rsa:2048 -nodes -keyout certificates/key.pem -x509 -days 365 -out certificates/certificate.pem \
    -subj "/C=IN/ST=Karnataka/L=Bengaluru/O=NA(Individual)/OU=Aakarshit Sharma/CN=gaming.freaks.utubechannel@gmail.com"


# Main Dockerfile
FROM python:3.11.1-alpine3.17
LABEL maintainers="asdoon00@gmail.com"

ENV PYTHONUNBUFFERED 1
WORKDIR /app

COPY requirements.txt .
COPY --from=builder /app/wheels /wheels
RUN apk add --no-cache libpq && \
     pip install --no-cache /wheels/*
RUN rm requirements.txt

COPY src/ .
COPY --from=builder /app/certificates/ ./certificates

RUN ./manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "leads_management.wsgi:application"]