#!/usr/bin/env python3
"""
Hatagawa I Flag Monitoring System - Demonstration
"""

import time
import threading
import subprocess
import sys
from monitor_cli import run_single_capture

def demo():
    """Demonstrate the flag monitoring system"""
    print("="*60)
    print("HATAGAWA I FLAG MONITORING SYSTEM DEMONSTRATION")
    print("="*60)
    print()
    
    print("1. Starting local test server...")
    
    # Start test server in background
    def start_server():
        subprocess.run([sys.executable, 'test_server.py'])
    
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    time.sleep(3)
    
    print("2. Testing flag capture...")
    print()
    
    # Perform test capture
    run_single_capture('localhost', 9999)
    
    print()
    print("3. Analyzing captured flags...")
    print()
    
    # Import and run analysis
    from monitor_cli import analyze_captured_flags
    analyze_captured_flags()
    
    print()
    print("="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    print()
    print("The system is ready to monitor the real Hatagawa I service at:")
    print("34.252.33.37:30653")
    print()
    print("To start monitoring, run:")
    print("  python3 monitor_cli.py monitor")
    print()
    print("For help:")
    print("  python3 monitor_cli.py --help")

if __name__ == "__main__":
    demo()