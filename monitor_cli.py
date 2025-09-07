#!/usr/bin/env python3
"""
Hatagawa I Flag Monitor - Usage Examples and Utilities
"""

import argparse
import json
import sys
from flag_monitor import HatagawaMonitor

def run_continuous_monitor(host, port):
    """Run continuous monitoring"""
    print(f"Starting continuous monitoring of {host}:{port}")
    print("Press Ctrl+C to stop monitoring")
    
    monitor = HatagawaMonitor(host=host, port=port)
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        monitor.stop_monitoring()
    
    # Show final statistics
    stats = monitor.get_statistics()
    print("\nFinal Statistics:")
    print(json.dumps(stats, indent=2))

def run_single_capture(host, port):
    """Run a single flag capture"""
    print(f"Attempting single flag capture from {host}:{port}")
    
    monitor = HatagawaMonitor(host=host, port=port)
    
    import socket
    sock = monitor.connect_to_service()
    if sock:
        flags = monitor.capture_flag(sock)
        sock.close()
        
        if flags:
            print(f"Successfully captured {len(flags)} flags:")
            for flag in flags:
                print(f"  - {flag}")
        else:
            print("No flags captured")
    else:
        print("Failed to connect to service")

def analyze_captured_flags():
    """Analyze previously captured flags"""
    try:
        with open('captured_flags.json', 'r') as f:
            flags_data = []
            for line in f:
                line = line.strip()
                if line:
                    flags_data.append(json.loads(line))
        
        print(f"Found {len(flags_data)} captured flags:")
        print("="*60)
        
        for i, flag_data in enumerate(flags_data, 1):
            print(f"Flag #{i}:")
            print(f"  Hex: {flag_data['flag']}")
            print(f"  Timestamp: {flag_data['analysis']['timestamp']}")
            print(f"  Length: {flag_data['analysis']['length']} chars ({flag_data['analysis']['byte_length']} bytes)")
            
            # Show potential decryptions if any
            analysis = flag_data['analysis']
            for key, value in analysis.items():
                if key.startswith('potential_decryption_'):
                    prefix = key.replace('potential_decryption_', '')
                    print(f"  Potential decryption ({prefix}): {value}")
            
            print("-" * 40)
        
    except FileNotFoundError:
        print("No captured flags file found. Run the monitor first to capture flags.")
    except Exception as e:
        print(f"Error analyzing flags: {e}")

def main():
    parser = argparse.ArgumentParser(description="Hatagawa I Flag Monitoring System")
    parser.add_argument('--host', default='34.252.33.37', help='Target host (default: 34.252.33.37)')
    parser.add_argument('--port', type=int, default=30653, help='Target port (default: 30653)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Continuous monitoring
    continuous_parser = subparsers.add_parser('monitor', help='Start continuous monitoring')
    
    # Single capture
    single_parser = subparsers.add_parser('capture', help='Perform single flag capture')
    
    # Analyze
    analyze_parser = subparsers.add_parser('analyze', help='Analyze captured flags')
    
    # Test with local server
    test_parser = subparsers.add_parser('test', help='Test with local server')
    
    args = parser.parse_args()
    
    if args.command == 'monitor':
        run_continuous_monitor(args.host, args.port)
    elif args.command == 'capture':
        run_single_capture(args.host, args.port)
    elif args.command == 'analyze':
        analyze_captured_flags()
    elif args.command == 'test':
        print("Starting test server on localhost:9999...")
        import subprocess
        import time
        import threading
        
        # Start test server
        def start_test_server():
            subprocess.run([sys.executable, 'test_server.py'])
        
        server_thread = threading.Thread(target=start_test_server)
        server_thread.daemon = True
        server_thread.start()
        
        time.sleep(2)  # Give server time to start
        
        # Run test capture
        run_single_capture('localhost', 9999)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()