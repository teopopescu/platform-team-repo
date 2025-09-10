# Stage 1: Lambda base image - using the same base for both stages ensures architecture compatibility
FROM public.ecr.aws/lambda/python:3.12 as base

# Stage 2: Install uv in a builder stage
FROM base as builder
RUN pip install --no-cache-dir uv==0.8.11

# Stage 3: Final image
FROM base

WORKDIR ${LAMBDA_TASK_ROOT}

# Copy uv from builder stage
COPY --from=builder /var/lang/bin/uv /bin/uv

# Copy Python dependency descriptors
COPY pyproject.toml uv.lock ./

# Install dependencies into Lambda folder
RUN uv pip install --no-cache-dir --target . .

# Copy Lambda function code
COPY *.py .

# Set Lambda handler
CMD ["handler.handler"]
