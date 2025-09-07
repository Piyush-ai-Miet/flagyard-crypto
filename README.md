# Hatagawa I Flag Monitoring System

This system continuously monitors the Hatagawa I environment by Flagyard to detect and capture flags accurately, avoiding false positives.

## Overview

The monitoring system consists of several components:

1. **flag_monitor.py** - Core monitoring system with cryptanalysis capabilities
2. **monitor_cli.py** - Command-line interface for easy usage
3. **test_server.py** - Local test server for development and testing
4. **hatagawa.py** - Original CTF challenge implementation

## Features

- **Continuous Monitoring**: Automatically connects to the Hatagawa I service and monitors for flags
- **Flag Detection**: Identifies hex-encoded flags using pattern matching
- **Cryptanalysis**: Attempts to analyze captured flags and detect encryption patterns
- **Deduplication**: Avoids capturing the same flag multiple times
- **Robust Connection Handling**: Automatic retry with exponential backoff
- **Detailed Logging**: Comprehensive logging to file and console
- **JSON Export**: Saves captured flags with analysis data in JSON format

## Usage

### Basic Usage

#### Continuous Monitoring (Recommended)
```bash
python3 monitor_cli.py monitor
```

This starts continuous monitoring of the default target (34.252.33.37:30653). The monitor will:
- Attempt to connect to the service
- Automatically trigger flag displays
- Capture and analyze any flags found
- Save results to `captured_flags.json`
- Log activity to `hatagawa_monitor.log`

#### Single Flag Capture
```bash
python3 monitor_cli.py capture
```

Performs a single flag capture attempt and exits.

#### Analyze Captured Flags
```bash
python3 monitor_cli.py analyze
```

Analyzes previously captured flags from `captured_flags.json`.

### Advanced Usage

#### Custom Target
```bash
python3 monitor_cli.py monitor --host 192.168.1.100 --port 8080
```

#### Test with Local Server
```bash
python3 monitor_cli.py test
```

Starts a local test server and performs a test capture.

## Direct Usage of flag_monitor.py

```python
from flag_monitor import HatagawaMonitor

# Create monitor instance
monitor = HatagawaMonitor(host="34.252.33.37", port=30653)

# Start continuous monitoring
monitor.start_monitoring()

# Or perform single capture
import socket
sock = monitor.connect_to_service()
if sock:
    flags = monitor.capture_flag(sock)
    print(f"Captured: {flags}")
    sock.close()
```

## Output Files

### captured_flags.json
Contains captured flags with detailed analysis:
```json
{
  "flag": "320af2e7ceeea34cfeae586183f96deecb6f999ce53ce37bec",
  "analysis": {
    "hex": "320af2e7ceeea34cfeae586183f96deecb6f999ce53ce37bec",
    "length": 50,
    "timestamp": "2025-09-07T10:52:40.577366",
    "byte_length": 25,
    "source": "Hatagawa I",
    "likely_encrypted_flag": true,
    "bytes": [50, 10, 242, 231, ...],
    "potential_key_for_BHFlagY{": "7042b48baf89fa37",
    "potential_key_for_flag{": "54669380b5"
  }
}
```

### hatagawa_monitor.log
Detailed logging of all monitoring activities, including connection attempts, flag captures, and errors.

## Flag Analysis

The system performs automatic cryptanalysis on captured flags:

1. **Pattern Recognition**: Identifies hex-encoded data that could be encrypted flags
2. **Known Prefix Analysis**: Attempts to decrypt using common CTF flag prefixes:
   - `BHFlagY{` (BlackHat specific)
   - `flag{`
   - `FLAG{`
   - `CTF{`
3. **Key Extraction**: If a prefix matches, extracts the potential encryption key
4. **Full Decryption**: Attempts to decrypt the entire flag using the extracted key

## Understanding the Hatagawa Challenge

The original `hatagawa.py` implements:
- Linear Congruential Generator (LCG) for pseudo-random number generation
- One-time pad encryption using the LCG output
- Interactive interface for flag retrieval

The monitor exploits this by:
- Automatically triggering flag displays
- Capturing multiple encrypted versions
- Analyzing patterns in the encryption

## Security Considerations

- The system only monitors the specified Hatagawa I environment
- No data is transmitted to external services
- All captured data is stored locally
- Focused on legitimate CTF flag capture, avoiding false positives

## Troubleshooting

### Connection Issues
- Verify the target host and port are correct
- Check network connectivity
- Review logs in `hatagawa_monitor.log`

### No Flags Detected
- Ensure the service is responding correctly
- Check if the flag format has changed
- Review the regex pattern in `flag_pattern`

### Analysis Issues
- Verify captured flags are properly hex-encoded
- Check if new flag prefixes need to be added
- Review the cryptanalysis logic for improvements

## Dependencies

- Python 3.6+
- Standard library only (no external dependencies)

## Files Description

- **flag_monitor.py**: Core monitoring system
- **monitor_cli.py**: Command-line interface
- **test_server.py**: Local test server
- **hatagawa.py**: Original challenge (reference only)
- **captured_flags.json**: Output file with captured flags
- **hatagawa_monitor.log**: Monitoring activity log