generate-protos:
	poetry run \
		python -m grpc_tools.protoc \
		-I ./protos \
		--python_out=./grpcoin/generated/ \
		--mypy_out=./grpcoin/generated/ \
		--grpc_python_out=./grpcoin/generated/ \
		--mypy_grpc_out=./grpcoin/generated/ \
		./protos/grpcoin.proto

path_fix:
	@sed -i -E 's/^import.*_pb2/from . \0/' ./grpcoin/generated/*.py

run_grpcoin:
	poetry run python -m grpcoin
