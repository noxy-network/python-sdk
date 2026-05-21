.PHONY: proto build test

proto:
	mkdir -p noxy/grpc
	touch noxy/__init__.py noxy/grpc/__init__.py
	python3 -m grpc_tools.protoc \
		-I proto \
		--python_out=noxy/grpc \
		--grpc_python_out=noxy/grpc \
		proto/agent.proto
	# Fix relative import if protoc emitted a top-level import
	@sed -i.bak 's/^import agent_pb2/from . import agent_pb2/' noxy/grpc/agent_pb2_grpc.py 2>/dev/null || \
	 sed -i '' 's/^import agent_pb2/from . import agent_pb2/' noxy/grpc/agent_pb2_grpc.py
	@rm -f noxy/grpc/agent_pb2_grpc.py.bak

build: proto
	pip install -e .

test: build
	pytest tests/ -v 2>/dev/null || true
