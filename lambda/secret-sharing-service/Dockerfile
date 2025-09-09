# Stage 0: Pull UV binary
FROM ghcr.io/astral-sh/uv:0.8.11 AS uv

# Stage 1: Lambda base image
FROM public.ecr.aws/lambda/python:3.12

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy uv binary and make it executable
COPY --from=uv /uv /bin/uv
RUN chmod +x /bin/uv

# Copy Python dependencies descriptors
COPY pyproject.toml uv.lock ./

# Install dependencies via uv
RUN /bin/uv pip install --no-cache-dir --target . .

# Copy Lambda function code
COPY *.py .

# Set Lambda handler
CMD ["handler.handler"]
