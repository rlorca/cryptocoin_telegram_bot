FROM python:3.6-stretch

# create app user
RUN useradd -ms /bin/bash cbot

WORKDIR /home/cbot

# needed to install dependencies
COPY requirements.txt .

RUN pip install -r requirements.txt

# our app
COPY ctb ./ctb

USER cbot

ENTRYPOINT ["python", "-m", "ctb"]
