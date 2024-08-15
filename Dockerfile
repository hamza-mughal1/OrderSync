FROM python:3.12
WORKDIR /app

COPY ./requirement.txt /requirement.txt

RUN pip install -r /requirement.txt

# EXPOSE 3000

COPY ./images /images
COPY ./app.py /app.py
COPY ./handler /handler
COPY ./model /model

CMD ["python3", "/app.py"]