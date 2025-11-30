#!/usr/bin/env python3
"""
Generate Python gRPC stubs from proto files.

This script generates Python code from .proto files for gRPC communication.

Usage:
    python scripts/generate_proto.py

Output:
    - src/models/proto_generated/datastream_pb2.py (messages)
    - src/models/proto_generated/datastream_pb2_grpc.py (service stubs)

Author: QA Automation Architect
Date: 2025-11-29
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Generate Python stubs from proto files."""
    # Get project root
    project_root = Path(__file__).parent.parent
    protos_dir = project_root / "protos"
    output_dir = project_root / "src" / "models" / "proto_generated"
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create/update __init__.py
    init_file = output_dir / "__init__.py"
    init_file.write_text('''"""
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
''')
    print(f"✅ Created/updated {init_file}")
    
    # Find proto files
    proto_files = list(protos_dir.glob("*.proto"))
    if not proto_files:
        print("❌ No .proto files found in protos/ directory")
        sys.exit(1)
    
    print(f"📁 Proto files found: {[p.name for p in proto_files]}")
    print(f"📁 Output directory: {output_dir}")
    
    # Generate stubs for each proto file
    for proto_file in proto_files:
        print(f"\n🔧 Generating stubs for {proto_file.name}...")
        
        cmd = [
            sys.executable, "-m", "grpc_tools.protoc",
            f"-I{protos_dir}",
            f"--python_out={output_dir}",
            f"--grpc_python_out={output_dir}",
            str(proto_file)
        ]
        
        print(f"   Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Error generating stubs:")
                print(f"   stdout: {result.stdout}")
                print(f"   stderr: {result.stderr}")
                sys.exit(1)
            
            print(f"   ✅ Generated successfully")
            
        except FileNotFoundError:
            print("❌ grpc_tools.protoc not found. Install with: pip install grpcio-tools")
            sys.exit(1)
    
    # Fix imports in generated files (relative imports)
    print("\n🔧 Fixing imports in generated files...")
    
    # Fix imports for all generated grpc files
    for grpc_file in output_dir.glob("*_pb2_grpc.py"):
        content = grpc_file.read_text()
        # Get the base name (e.g., "datastream" from "datastream_pb2_grpc.py")
        base_name = grpc_file.stem.replace("_pb2_grpc", "")
        
        # Fix import to use relative import
        old_import = f"import {base_name}_pb2 as {base_name.replace('-', '_')}__pb2"
        new_import = f"from . import {base_name}_pb2 as {base_name.replace('-', '_')}__pb2"
        
        if old_import in content:
            fixed_content = content.replace(old_import, new_import)
            grpc_file.write_text(fixed_content)
            print(f"   ✅ Fixed imports in {grpc_file.name}")
    
    # List generated files
    print("\n📄 Generated files:")
    for f in output_dir.glob("*.py"):
        size = f.stat().st_size
        print(f"   - {f.name} ({size} bytes)")
    
    print("\n✅ Proto generation complete!")
    print("\nUsage in code:")
    print("   from src.models.proto_generated import datastream_pb2, datastream_pb2_grpc")


if __name__ == "__main__":
    main()

