FROM python:3.10

WORKDIR /app

RUN useradd -u 1000 app && \
    mkdir -p /var/www/app && \
    chown -R app:app /var/www/app

COPY Pipfile* /app/

RUN pip install --no-cache-dir pipenv && \
    pipenv requirements > requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

COPY . /app/

ENV PYTHONPATH=/app

USER app

CMD ["uwsgi", "--http", ":5000", "--master", "--enable-threads", "-s", "/var/www/app/app.sock", "--manage-script-name", "--mount", "/=app:app"]
