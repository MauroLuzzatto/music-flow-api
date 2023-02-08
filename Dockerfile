# Use an official Python image as the base image
FROM public.ecr.aws/lambda/python:3.9


# Copy the required files to the image
COPY ./app.py ./app.py
COPY ./requirements.txt ./requirements.txt

# Install the required packages
RUN python3.9 -m pip install -r requirements.txt -t .


# Run the FastAPI application
CMD ["app.handler"]
