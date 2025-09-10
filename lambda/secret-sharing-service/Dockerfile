# Stage 1: Use Python image for building uv
FROM python:3.12-slim as builder
RUN pip install --no-cache-dir uv==0.8.11

# Stage 2: Final Lambda image
FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

# Copy uv from builder stage
COPY --from=builder /usr/local/bin/uv /bin/uv

# Copy Python dependency descriptor
COPY pyproject.toml ./

# Generate lock file and install dependencies
RUN uv pip install --no-cache-dir --target . .

# Copy Lambda function code
COPY *.py .

# Set Lambda handler
CMD ["handler.handler"]
