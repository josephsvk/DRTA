FROM python:3.11-slim
WORKDIR /app
COPY form.py /app/form.py
RUN apt-get update && apt-get install -y openssh-client && pip install npyscreen
CMD ["python", "form.py"]
