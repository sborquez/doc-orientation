# Use an official Python runtime as a parent image
FROM python:3

# Install Tesseract-ocr
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-spa

#COPY /usr/share/tesseract-ocr/4.00/tessdata/spa.traineddata /data/spa.traineddata

# Copy the current directory contents into the container at /app
COPY /app /app

# Set the working directory to /app
WORKDIR /app

# Set port
ENV PORT 8000
EXPOSE 8000

# Install requeriments.txt
RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Run app.py when the container launches
CMD ["python", "-u", "app.py"]
