# Use an official Python image as the base image
FROM public.ecr.aws/lambda/python:3.9

COPY ./requirements.txt ./requirements.txt

# Install the required packages
RUN python3.9 -m pip install -r requirements.txt -t .

# Copy the required files to the image
COPY ./music_flow/ ./music_flow/
COPY ./.env ./.env
COPY ./app ./app
COPY ./main.py ./main.py
# COPY ./results/ ./results/

RUN mkdir -v -p ./results/
RUN chmod -R o+rX .

# Run the FastAPI application
CMD ["main.handler"]
