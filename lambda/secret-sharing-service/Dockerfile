# Use the AWS Python 3.12 base image
FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

# Install uv using pip
RUN pip install uv==0.8.11

# Copy requirements first to leverage Docker cache
COPY pyproject.toml ./

# Install dependencies directly using pip
RUN uv pip install --no-cache-dir --target . .

# Copy Lambda function code
COPY *.py .

# Set the CMD to your handler (must be a string, not a list)
CMD handler.handler
