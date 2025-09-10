# Stage 1: Use Python image for building uv
FROM python:3.12-slim as builder
RUN pip install --no-cache-dir uv==0.8.11

# Stage 2: Final Lambda image
FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

# Copy uv from builder stage
COPY --from=builder /usr/local/bin/uv /bin/uv

# Copy Python dependency descriptors
COPY pyproject.toml uv.lock ./

# Install dependencies into Lambda folder
RUN uv pip install --no-cache-dir --target . .

# Copy Lambda function code
COPY *.py .

# Set Lambda handler
CMD ["handler.handler"]
