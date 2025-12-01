"""
Demo: Complete Live Job Flow - Real gRPC Connection
===================================================

This script demonstrates the FULL Live Job flow:
1. Create job via POST /configure
2. Wait for Pod to be ready (with retries!)
3. Connect to gRPC server
4. Receive REAL spectrogram frames
5. Disconnect

Run:
    python scripts/demo_live_job_flow.py --env staging

Author: QA Automation Architect
Date: 2025-11-30
"""

import sys
import time
import logging
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config_manager import ConfigManager
from src.apis.focus_server_api import FocusServerAPI
from src.apis.grpc_client import GrpcStreamClient
from src.models.focus_server_models import ConfigureRequest, DisplayInfo, Channels, FrequencyRange

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_step(step: int, text: str):
    """Print a step marker."""
    print(f"\n{'─' * 60}")
    print(f"  STEP {step}: {text}")
    print(f"{'─' * 60}")


def run_live_job_demo(env: str = "staging"):
    """
    Run a complete Live Job demonstration.
    
    This shows the REAL flow that PandaApp uses:
    1. Create job
    2. Get stream URL/port
    3. Connect to gRPC (with retries!)
    4. Receive frames
    5. Disconnect
    """
    print_header("LIVE JOB DEMO - Real gRPC Connection")
    
    # =================================================================
    # SETUP: Load configuration
    # =================================================================
    print_step(0, "SETUP - Loading Configuration")
    
    config = ConfigManager(env=env)
    
    api_config = config.get_section("focus_server")
    print(f"  Environment: {env}")
    print(f"  Backend URL: {api_config.get('base_url')}")
    
    # =================================================================
    # STEP 1: Create Job via POST /configure
    # =================================================================
    print_step(1, "CREATE JOB - POST /configure")
    
    # Prepare configuration
    config_payload = ConfigureRequest(
        displayTimeAxisDuration=10,
        nfftSelection=1024,
        displayInfo=DisplayInfo(height=600),
        channels=Channels(min=1, max=50),  # 50 channels - light load
        frequencyRange=FrequencyRange(min=0, max=500),
        view_type="0"  # MULTICHANNEL
    )
    
    print(f"  Channels: 1-50 (50 channels)")
    print(f"  Frequency: 0-500 Hz")
    print(f"  NFFT: 1024")
    print(f"  View Type: MultiChannel")
    
    # Create API client
    api = FocusServerAPI(config)
    
    # Send configure request
    start_time = time.time()
    response = api.configure_streaming_job(config_payload)
    configure_time = (time.time() - start_time) * 1000
    
    print(f"\n  ✅ Job created in {configure_time:.0f}ms")
    print(f"  Job ID: {response.job_id}")
    print(f"  Stream URL: {response.stream_url}")
    print(f"  Stream Port: {response.stream_port}")
    print(f"  Frequencies: {response.frequencies_amount}")
    print(f"  Channels: {response.channel_amount}")
    
    job_id = response.job_id
    stream_url = response.stream_url
    stream_port = int(response.stream_port)
    
    # =================================================================
    # STEP 2: Wait for Pod to be Ready (with RETRIES!)
    # This is the KEY insight from Yonatan!
    # =================================================================
    print_step(2, "WAIT FOR READY - Pod needs time to start")
    
    print("  ⏳ The Pod is starting up...")
    print("  ⏳ gRPC server is initializing...")
    print("  ⏳ This may take a few seconds...")
    print()
    
    # =================================================================
    # STEP 3: Connect to gRPC (with RETRIES!)
    # =================================================================
    print_step(3, "CONNECT TO gRPC - With Retries")
    
    grpc_client = GrpcStreamClient(
        config_manager=config,
        connection_timeout=30,
        stream_timeout=60
    )
    
    max_retries = 5
    retry_delay = 2.0  # seconds
    connected = False
    
    for attempt in range(max_retries):
        print(f"  Attempt {attempt + 1}/{max_retries}...")
        
        try:
            start_time = time.time()
            grpc_client.connect(
                stream_url=stream_url,
                stream_port=stream_port,
                use_tls=False
            )
            connect_time = (time.time() - start_time) * 1000
            
            connected = True
            print(f"  ✅ Connected in {connect_time:.0f}ms!")
            break
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            
            if attempt < max_retries - 1:
                print(f"  ⏳ Waiting {retry_delay}s before retry...")
                time.sleep(retry_delay)
    
    if not connected:
        print(f"\n  ❌ FAILED to connect after {max_retries} attempts")
        print("  Possible reasons:")
        print("    - Pod is not ready yet")
        print("    - Network issues")
        print("    - gRPC server crashed")
        return
    
    # =================================================================
    # STEP 4: Receive REAL Spectrogram Frames
    # =================================================================
    print_step(4, "STREAM DATA - Receiving Real Frames")
    
    frames_to_receive = 5
    print(f"  Requesting {frames_to_receive} frames...")
    print()
    
    frame_count = 0
    total_data_points = 0
    
    try:
        for frame in grpc_client.stream_data(
            stream_id=0,
            max_frames=frames_to_receive,
            timeout=30
        ):
            frame_count += 1
            data_points = frame.data_shape_x * frame.data_shape_y
            total_data_points += data_points
            
            print(f"  📦 Frame {frame_count}:")
            print(f"      Shape: {frame.data_shape_x} x {frame.data_shape_y}")
            print(f"      Channels: {frame.start_channel} - {frame.end_channel}")
            print(f"      Amplitude: [{frame.global_minimum:.2f}, {frame.global_maximum:.2f}]")
            print(f"      Data points: {data_points:,}")
            
            # Show timestamps if available
            if frame.timestamp_in_milis:
                timestamps = list(frame.timestamp_in_milis)
                if timestamps:
                    print(f"      Time range: {timestamps[0]} - {timestamps[-1]} ms")
            print()
            
    except Exception as e:
        print(f"  ⚠️ Stream ended: {e}")
    
    print(f"  ✅ Received {frame_count} frames")
    print(f"  ✅ Total data points: {total_data_points:,}")
    
    # =================================================================
    # STEP 5: Disconnect and Cleanup
    # =================================================================
    print_step(5, "DISCONNECT - Cleanup")
    
    grpc_client.disconnect()
    print("  ✅ Disconnected from gRPC server")
    print("  ✅ Resources released")
    
    # Note: The cleanup-job in Kubernetes will automatically delete
    # the Pod after ~50 seconds of inactivity
    print("\n  ℹ️  The Pod will be automatically cleaned up by Kubernetes")
    print("      after ~50 seconds of inactivity (cleanup-job monitors CPU)")
    
    # =================================================================
    # SUMMARY
    # =================================================================
    print_header("SUMMARY")
    print(f"  Job ID: {job_id}")
    print(f"  Configure time: {configure_time:.0f}ms")
    print(f"  Frames received: {frame_count}")
    print(f"  Total data points: {total_data_points:,}")
    print()
    print("  This is EXACTLY what PandaApp does when you open a Live view!")
    print()


def main():
    parser = argparse.ArgumentParser(description="Live Job Demo")
    parser.add_argument(
        "--env", 
        default="staging",
        help="Environment to use (staging/production)"
    )
    args = parser.parse_args()
    
    try:
        run_live_job_demo(env=args.env)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

