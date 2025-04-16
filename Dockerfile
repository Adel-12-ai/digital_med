FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PORT=8800

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install "gunicorn==23.0.0" \
    && pip install -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 8000

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "digital_med.wsgi:application"]
