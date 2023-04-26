FROM python:3.10

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py"]
