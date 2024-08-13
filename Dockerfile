FROM python:3.12
WORKDIR /app

COPY ./requirement.txt /requirement.txt

RUN pip install -r /requirement.txt

COPY ./app.py /app.py
COPY ./handler /handler
COPY ./model /model
COPY ./images /images

EXPOSE 3000

RUN python3 /app.py