# grpcoin-python-client

# Development

First, you must generate proto files.

```sh

python3 -m grpc_tools.protoc -I ./protos --python_out=. --grpc_python_out=. ./protos/grpcoin.proto
```
