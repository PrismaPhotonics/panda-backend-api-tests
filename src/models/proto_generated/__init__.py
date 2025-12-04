"""
Auto-generated Protocol Buffer modules for gRPC communication.

Generated from protos/*.proto files using grpc_tools.protoc.

Modules:
    - pandadatastream_pb2: Protocol buffer message classes (PRODUCTION)
    - pandadatastream_pb2_grpc: gRPC service stubs (PRODUCTION)
    - datastream_pb2: Legacy protocol buffer message classes
    - datastream_pb2_grpc: Legacy gRPC service stubs

Usage (Production - pandadatastream):
    from src.models.proto_generated import pandadatastream_pb2, pandadatastream_pb2_grpc
    
    # Create channel and stub
    channel = grpc.insecure_channel('host:port')
    stub = pandadatastream_pb2_grpc.DataStreamServiceStub(channel)
    
    # Stream data (use stream_id, not job_id!)
    request = pandadatastream_pb2.StreamDataRequest(stream_id=0)
    for response in stub.StreamData(request):
        print(f"Data shape: {response.data_shape_x}x{response.data_shape_y}")
        print(f"Amplitude: {response.global_minimum} to {response.global_maximum}")
"""
# Auto-generated imports - production (pandadatastream)
try:
    from . import pandadatastream_pb2
    from . import pandadatastream_pb2_grpc
except ImportError:
    pass

# Auto-generated imports - legacy (datastream)
try:
    from . import datastream_pb2
    from . import datastream_pb2_grpc
except ImportError:
    pass
