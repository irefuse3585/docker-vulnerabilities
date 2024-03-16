FROM python:3.10.13-alpine3.18

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD ["python3", "app.py"]