FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

RUN apt update && apt install -y curl

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--timeout", "3600"]
