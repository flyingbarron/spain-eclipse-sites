#!/usr/bin/env python3
"""
Test script to demonstrate the clean server shutdown functionality.
This script starts the server, waits a moment, then triggers shutdown via API.
"""

import subprocess
import time
import urllib.request
import sys

def test_shutdown():
    print("Starting server...")
    # Start server in background
    process = subprocess.Popen(
        [sys.executable, "serve_viewer.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(2)
    
    print("\nServer should be running. Testing shutdown endpoint...")
    
    try:
        # Trigger shutdown via API
        response = urllib.request.urlopen("http://localhost:8000/api/shutdown", timeout=5)
        data = response.read().decode('utf-8')
        print(f"Shutdown response: {data}")
        
        # Wait for server to shut down
        time.sleep(2)
        
        # Check if process has terminated
        if process.poll() is not None:
            print("\n✓ Server shut down cleanly!")
            print(f"Exit code: {process.returncode}")
        else:
            print("\n✗ Server still running, forcing termination...")
            process.terminate()
            process.wait(timeout=5)
            
    except Exception as e:
        print(f"\nError during test: {e}")
        process.terminate()
        process.wait(timeout=5)
    
    # Print any output
    stdout, stderr = process.communicate(timeout=1)
    if stdout:
        print("\nServer output:")
        print(stdout)
    if stderr:
        print("\nServer errors:")
        print(stderr)

if __name__ == "__main__":
    test_shutdown()

# Made with Bob
