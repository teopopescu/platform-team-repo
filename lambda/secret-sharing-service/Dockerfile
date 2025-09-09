# Stage 0: Use uv for dependency installation (force x86_64)
FROM ghcr.io/astral-sh/uv:0.8.11 AS uv

# Stage 1: Lambda base image
FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

# Copy uv binary from stage 0
COPY --from=uv /uv /bin/uv

# Copy Python dependency descriptors
COPY pyproject.toml uv.lock ./

# Install dependencies into Lambda folder
RUN uv pip install --no-cache-dir --target . .

# Copy Lambda function code
COPY *.py .

# Set Lambda handler
CMD ["handler.handler"]
