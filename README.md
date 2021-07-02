# example-grpcoin-bot-python

An example grpcoin bot written in Python. 

# Dependencies

I advise you to create a virtualenv not to mess with your global python environment.
Then, install the requirements. 

```sh

pip install -r requirements.txt
```

# Development

First, you must generate proto files.

```sh

python3 -m grpc_tools.protoc -I ./protos --python_out=. --grpc_python_out=. ./protos/grpcoin.proto
```

To run, 

```py

python3 main.py
```