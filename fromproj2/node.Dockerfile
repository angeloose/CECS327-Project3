FROM python:3.9

WORKDIR /app

COPY node.py .

RUN pip install flask requests

EXPOSE 5000

CMD ["python", "node.py"]