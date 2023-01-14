FROM python:3.11.1-alpine3.17
LABEL maintainers="asdoon00@gmail.com"

ENV PYTHONUNBUFFERED 1
WORKDIR /app

COPY requirements.txt /app
RUN  apk add --no-cache postgresql-libs && \
     apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
     pip install -r requirements.txt --no-cache-dir && \
     apk --purge del .build-deps
RUN rm requirements.txt

COPY src/ /app
COPY certificates/ /app/certificates

RUN ./manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "leads_management.wsgi:application"]