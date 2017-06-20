FROM python:alpine

RUN pip install requests schedule

COPY ./ /

CMD ["python", "/rancher-cleanup.py"]
