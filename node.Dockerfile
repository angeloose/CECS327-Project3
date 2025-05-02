FROM python:3.9

WORKDIR /app

COPY node.py .

RUN pip install flask requests

RUN mkdir -p storage

EXPOSE 5000

CMD ["python", "node.py"]