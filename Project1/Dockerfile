FROM python:3.8.10
#Set the working directory to /app
WORKDIR /app
#Copy local contents into the container
ADD . /app
#Install all required requirements
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "main.py"]
