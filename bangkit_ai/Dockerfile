FROM python:3.11


WORKDIR /app

COPY . /app

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=8080
EXPOSE 8080

CMD ["python","main.py"]