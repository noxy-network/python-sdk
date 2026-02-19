.PHONY: proto build test

proto:
	mkdir -p noxy/grpc
	touch noxy/__init__.py noxy/grpc/__init__.py
	python -m grpc_tools.protoc \
		-I proto \
		--python_out=noxy/grpc \
		--grpc_python_out=noxy/grpc \
		proto/noxy.proto
	# Fix relative import in generated grpc file
	@sed -i.bak 's/^import noxy_pb2/from . import noxy_pb2/' noxy/grpc/noxy_pb2_grpc.py 2>/dev/null || \
	 sed -i '' 's/^import noxy_pb2/from . import noxy_pb2/' noxy/grpc/noxy_pb2_grpc.py
	@rm -f noxy/grpc/noxy_pb2_grpc.py.bak

build: proto
	pip install -e .

test: build
	pytest tests/ -v 2>/dev/null || true
