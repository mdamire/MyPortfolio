FROM python:3.8-slim
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN apt update && apt install -y build-essential default-libmysqlclient-dev
RUN pip install -r requirements.txt
COPY . /code/
CMD python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000
