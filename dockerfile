FROM python:3.6-stretch

# create app user
RUN useradd -ms /bin/bash cbot

WORKDIR /home/cbot

# needed to install dependencies
ADD requirements.txt .

RUN pip install -r requirements.txt

USER cbot

# our app
COPY ctb ./ctb

ENTRYPOINT ["python", "-m", "ctb"]
