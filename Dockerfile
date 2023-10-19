FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "10000", "main:app"]
