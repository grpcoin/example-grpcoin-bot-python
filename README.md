# Example Grpcoin Python Bot

An example grpcoin bot written in Python for demonstration purposes. 

## How to run

### Setting access token
Before running the bot, make sure you have a GitHub account.

Then, [create a GitHub personal access token](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token#creating-a-token) 
that does not have any permissions!

Set your GitHub token to `TOKEN` environment variable.

```sh
export TOKEN=...
```

### Installing dependencies

Note that it is strongly recommended to create a `virtualenv` before installing
requirements not to affect global Python modules. You can refer 
[here](https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv)
to set a virtual environment. 

Execute the following pip command on a shell to install dependencies: 

```sh
pip install -r requirements.txt
```

Generate Python codes for proto files:

```sh
python -m grpc_tools.protoc -I ./protos --python_out=. --grpc_python_out=. ./protos/grpcoin.proto
```

### Running bot

Run the following command to start the bot: 

```sh
python main.py
```
