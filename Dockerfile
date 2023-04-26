FROM python:3.10
EXPOSE $PORT
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD streamlit run app.py --server.port $PORT