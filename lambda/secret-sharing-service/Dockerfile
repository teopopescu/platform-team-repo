# Single stage build for better compatibility
FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

# Install uv using pip
RUN pip install --no-cache-dir uv==0.8.11

# Copy Python dependency descriptor
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --no-cache-dir --target . .

# Copy Lambda function code
COPY *.py .

# Set Lambda handler
CMD ["handler.handler"]
