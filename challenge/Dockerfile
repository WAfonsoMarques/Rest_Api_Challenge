FROM python:3.7

## FOR DEBUG
# RUN apt install -yqq curl

# Flask listens by default on port 5000
EXPOSE 5000

WORKDIR /challenge

COPY requirements.txt /challenge
RUN pip3 install -r requirements.txt

COPY ./app/ /challenge

CMD python3 __init__.py