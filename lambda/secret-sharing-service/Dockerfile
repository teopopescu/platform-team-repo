# Stage with uv
FROM --platform=linux/amd64 ghcr.io/astral-sh/uv:0.8.11 AS uv

# Lambda base
FROM public.ecr.aws/lambda/python:3.12
WORKDIR ${LAMBDA_TASK_ROOT}

COPY --from=uv /uv /bin/uv
COPY pyproject.toml uv.lock ./
RUN /bin/uv pip install --no-cache-dir --target . .

COPY *.py .
CMD ["handler.handler"]