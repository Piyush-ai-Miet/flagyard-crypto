#!/usr/bin/env python3
"""
Test script for Hatagawa I Flag Monitoring System
"""

import subprocess
import time
import sys
import os

def run_command(cmd, timeout=10):
    """Run a command and return its output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        # Combine stdout and stderr for analysis
        output = result.stdout + result.stderr
        return result.returncode, output, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"

def test_monitoring_basic():
    """Test basic monitoring functionality."""
    print("Testing basic monitoring (5 seconds)...")
    
    cmd = "python3 hatagawa.py --monitor --duration 5"
    returncode, stdout, stderr = run_command(cmd, timeout=8)
    
    if returncode != 0:
        print(f"❌ Basic monitoring failed: {stderr}")
        return False
    
    # Check for expected output patterns
    expected_patterns = [
        "Hatagawa I Monitoring System Activated",
        "Starting continuous monitoring",
        "Monitoring session complete",
        "SUCCESSFUL CAPTURE"
    ]
    
    for pattern in expected_patterns:
        if pattern not in stdout:
            print(f"❌ Missing expected pattern: {pattern}")
            return False
    
    print("✅ Basic monitoring test passed")
    return True

def test_monitoring_with_pattern():
    """Test monitoring with specific pattern."""
    print("Testing pattern-specific monitoring...")
    
    cmd = "python3 hatagawa.py --monitor --pattern 'D3BUGG1NG' --duration 3"
    returncode, stdout, stderr = run_command(cmd, timeout=6)
    
    if returncode != 0:
        print(f"❌ Pattern monitoring failed: {stderr}")
        return False
    
    if "Target pattern 'D3BUGG1NG' found!" not in stdout:
        print("❌ Target pattern not found")
        return False
    
    print("✅ Pattern monitoring test passed")
    return True

def test_custom_flag():
    """Test monitoring with custom flag."""
    print("Testing with custom flag...")
    
    cmd = "DYN_FLAG='FLAG{custom_test}' python3 hatagawa.py --monitor --duration 3"
    returncode, stdout, stderr = run_command(cmd, timeout=6)
    
    if returncode != 0:
        print(f"❌ Custom flag test failed: {stderr}")
        return False
    
    if "FLAG{custom_test}" not in stdout:
        print("❌ Custom flag not captured correctly")
        return False
    
    print("✅ Custom flag test passed")
    return True

def test_help_output():
    """Test help functionality."""
    print("Testing help output...")
    
    cmd = "python3 hatagawa.py --help"
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode != 0:
        print(f"❌ Help command failed: {stderr}")
        return False
    
    if "Hatagawa I Flag Monitoring System" not in stdout:
        print("❌ Help output missing expected content")
        return False
    
    print("✅ Help output test passed")
    return True

def test_log_file_creation():
    """Test that log files are created."""
    print("Testing log file creation...")
    
    log_file = "/tmp/test_monitor.log"
    cmd = f"python3 hatagawa.py --monitor --duration 2 --log-file {log_file}"
    returncode, stdout, stderr = run_command(cmd, timeout=5)
    
    if returncode != 0:
        print(f"❌ Log file test failed: {stderr}")
        return False
    
    if not os.path.exists(log_file):
        print(f"❌ Log file not created: {log_file}")
        return False
    
    print("✅ Log file creation test passed")
    return True

def main():
    """Run all tests."""
    print("🚀 Starting Hatagawa I Flag Monitoring System Tests")
    print("=" * 60)
    
    tests = [
        test_help_output,
        test_monitoring_basic,
        test_monitoring_with_pattern,
        test_custom_flag,
        test_log_file_creation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            time.sleep(0.5)  # Brief pause between tests
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Hatagawa monitoring system is working correctly.")
        return 0
    else:
        print("🚨 Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())