# Use the AWS Python 3.12 base image
FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

# Install system dependencies
RUN yum install -y gcc python3-devel

# Copy requirements first to leverage Docker cache
COPY pyproject.toml ./

# Install dependencies directly using pip
RUN pip install --no-cache-dir \
    boto3>=1.40.11 \
    cryptography>=45.0.6 \
    pgpy>=0.6.0

# Copy Lambda function code
COPY *.py .

# Set the CMD to your handler (must be a string, not a list)
CMD handler.handler
