# python 3.11 as parent image
FROM python:3.11-slim

# set working directory
WORKDIR /app

# copy files from current directory to working directory
COPY src/ .

# install dependencies
RUN pip3 install -r requirements.txt

# expose port 8001
EXPOSE 8001

# run command. src.app as a module 
CMD ["python3", "app.py"]