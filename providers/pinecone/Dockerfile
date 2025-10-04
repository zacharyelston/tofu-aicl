FROM python:3.11-slim

WORKDIR /app
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy proto files and generate code
COPY ./proto/ ./proto/
RUN python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    proto/provider.proto

# Copy provider code
COPY server.py .

EXPOSE 50051

CMD ["python", "server.py"]
