# Hatagawa I Flag Monitoring System

This is an enhanced version of the BlackHat MEA CTF 2025 Qualifiers "Hatagawa I" challenge that includes a comprehensive flag monitoring system.

## Features

### Original Interactive Mode
- Classic river monitoring experience with Japanese aesthetics (旗 = flag, 川 = river)
- Interactive menu system to watch flags float by
- LCG-based encryption for flag obfuscation

### New Monitoring System
- **Continuous Monitoring**: Automated detection of flags appearing in the environment
- **Pattern Recognition**: Smart detection of flag-like patterns in encrypted data
- **Accurate Decryption**: Verification system to prevent false positives
- **Comprehensive Logging**: Detailed logs with timestamps and metadata
- **Targeted Search**: Ability to monitor for specific flag patterns
- **Configurable Duration**: Set monitoring time limits or run indefinitely

## Usage

### Interactive Mode (Original)
```bash
python3 hatagawa.py
```

### Monitoring Mode
```bash
# Basic monitoring (unlimited duration)
python3 hatagawa.py --monitor

# Monitor for 30 seconds
python3 hatagawa.py --monitor --duration 30

# Monitor for specific pattern
python3 hatagawa.py --monitor --pattern "D3BUGG1NG"

# Custom log file
python3 hatagawa.py --monitor --log-file custom_monitor.log

# All options combined
python3 hatagawa.py --monitor --pattern "CTF" --duration 60 --log-file search.log
```

### Custom Flag Environment
```bash
# Set custom flag
DYN_FLAG="CTF{your_custom_flag}" python3 hatagawa.py --monitor
```

## Command Line Options

- `--monitor`: Enable continuous monitoring mode
- `--pattern PATTERN`: Specific flag pattern to search for (stops when found)
- `--duration DURATION`: Monitoring duration in seconds (default: unlimited)
- `--log-file LOG_FILE`: Custom log file path (default: hatagawa_monitor.log)

## Output

### Successful Capture Log Entry
```
2025-09-07 10:48:33,262 - INFO - SUCCESSFUL CAPTURE #1
2025-09-07 10:48:33,262 - INFO - Timestamp: 2025-09-07 10:48:33.261886
2025-09-07 10:48:33,262 - INFO - Source: Hatagawa I River Environment
2025-09-07 10:48:33,262 - INFO - Captured Data: 51e731b2eb3ac06be2f7f342db90d6a1ef3876732a83b634c5
2025-09-07 10:48:33,262 - INFO - Decrypted Flag: BHFlagY{D3BUGG1NG_1S_FUN}
2025-09-07 10:48:33,262 - INFO - Verification: SUCCESS
```

### Session Summary
```
2025-09-07 10:48:41,266 - INFO - Monitoring session complete:
2025-09-07 10:48:41,266 - INFO - Duration: 8.00 seconds
2025-09-07 10:48:41,266 - INFO - Total attempts: 5
2025-09-07 10:48:41,266 - INFO - Successful captures: 5
2025-09-07 10:48:41,266 - INFO - False positives prevented: 0
2025-09-07 10:48:41,266 - INFO - Accuracy: 100.0%
```

## Technical Details

### Cryptography
- Uses Linear Congruential Generator (LCG) for keystream generation
- One-time pad encryption (XOR cipher)
- Real-time decryption verification for accuracy

### Pattern Detection
- Length-based heuristics for flag identification
- Structure validation to prevent false positives
- Support for various flag formats (BHFlagY{...}, CTF{...}, etc.)

### Monitoring Features
- Sporatic flag appearance simulation (every 2 seconds)
- Comprehensive error handling and logging
- Keyboard interrupt support (Ctrl+C)
- Configurable monitoring parameters

## Testing

Run the included test suite:
```bash
python3 test_hatagawa_monitor.py
```

## Files

- `hatagawa.py`: Main application with both interactive and monitoring modes
- `test_hatagawa_monitor.py`: Comprehensive test suite
- `hatagawa_monitor.log`: Default log file (generated at runtime)
- `.gitignore`: Excludes log files and temporary artifacts

## Requirements

- Python 3.6+
- No external dependencies required
- Works on Linux, macOS, and Windows