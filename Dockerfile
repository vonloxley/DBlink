
FROM python:3.9 AS builder

RUN pip install --upgrade pip

RUN adduser --disabled-password --gecos "" worker
USER worker
WORKDIR /home/worker

COPY --chown=worker:worker requirements.txt requirements.txt
RUN pip install --user -r requirements.txt

# second unnamed stage
FROM python:3.9-slim
RUN adduser --disabled-password --gecos "" worker
USER worker
WORKDIR /home/worker

# copy only the dependencies installation from the 1st stage image
COPY --from=builder /home/worker/.local .local
COPY --chown=worker:worker ./dblink.py .

CMD [ "python", "./dblink.py" ]
