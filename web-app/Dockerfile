# python 3.11 as parent image
FROM python:3.11-slim

# set working directory
WORKDIR /app

# copy files from current directory to working directory
COPY . .

# install dependencies
RUN pip3 install -r requirements.txt

# expose port 8001
EXPOSE 8001

# Run the src
CMD ["python3", "-m", "src.app"]