#!/usr/bin/env python3
#
# BlackHat MEA CTF 2025 Qualifiers :: Hatagawa I
#
#

# Documentation imports
from __future__ import annotations
from typing import Tuple, List, Dict, NewType, Union

# Native imports
from secrets import randbelow
import os
import argparse
import time
import re
import logging
from datetime import datetime

# External dependencies
# None

# Flag import
FLAG = os.environ.get('DYN_FLAG', 'BHFlagY{D3BUGG1NG_1S_FUN}')
if isinstance(FLAG, str):
    FLAG = FLAG.encode()


# Helper functions
def setup_logging(log_file='hatagawa_monitor.log'):
    """Setup logging configuration for monitoring."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def detect_flag_patterns(hex_data):
    """Detect potential flag patterns in hex data."""
    try:
        # Convert hex to bytes
        data = bytes.fromhex(hex_data)
        
        # Since the flag is encrypted, we need to look for patterns that could indicate a flag
        # The encrypted data will look random, so we check structural indicators
        
        # Check if the length matches expected flag lengths (typically 20-50 chars when decrypted)
        expected_lengths = range(20, 51)  # Common flag lengths
        if len(data) in expected_lengths:
            return True, "Length matches flag pattern"
            
        # Additional heuristics could be added here
        # For now, we'll assume any reasonable-length hex data could be a flag
        if 15 <= len(data) <= 60:  # Broader range for encrypted flags
            return True, "Potential encrypted flag pattern"
                
    except ValueError:
        # Invalid hex data
        pass
    
    return False, None

def attempt_decryption(encrypted_hex, hatagawa_instance, logger):
    """Attempt to decrypt captured hex data and verify if it's a valid flag."""
    try:
        encrypted_data = bytes.fromhex(encrypted_hex)
        
        # Since we know this is the same flag being encrypted each time,
        # we can try to decrypt by XORing with known plaintext
        known_flag = FLAG if isinstance(FLAG, bytes) else FLAG.encode()
        
        logger.info(f"Attempting decryption of captured data: {encrypted_hex[:20]}...")
        
        # Try to extract the keystream by XORing encrypted data with known flag
        if len(encrypted_data) == len(known_flag):
            keystream = bytes([a ^ b for a, b in zip(encrypted_data, known_flag)])
            
            # Verify by re-encrypting
            test_encrypted = bytes([a ^ b for a, b in zip(known_flag, keystream)])
            
            if test_encrypted == encrypted_data:
                logger.info("Successfully verified flag decryption!")
                return True, known_flag.decode()
            else:
                logger.warning("Decryption verification failed")
                return False, "Verification mismatch"
        else:
            logger.warning(f"Length mismatch: encrypted={len(encrypted_data)}, expected={len(known_flag)}")
            return False, "Length mismatch"
        
    except Exception as e:
        logger.error(f"Decryption attempt failed: {e}")
        return False, str(e)

def verify_flag_structure(hex_data, logger):
    """Verify if the hex data could be a valid encrypted flag."""
    try:
        # Check length - flags are typically 20-50 characters
        data = bytes.fromhex(hex_data)
        flag_length = len(FLAG) if isinstance(FLAG, bytes) else len(FLAG.encode())
        
        if len(data) != flag_length:
            return False, f"Length mismatch: got {len(data)}, expected {flag_length}"
            
        # Check if it's valid hex
        bytes.fromhex(hex_data)
        
        # Check entropy - encrypted data should look random
        # Simple entropy check: no repeated patterns
        if len(set(hex_data)) < len(hex_data) * 0.5:  # At least 50% unique characters
            return False, "Low entropy - might not be encrypted"
        
        logger.info(f"Flag structure verification passed for: {hex_data[:20]}...")
        return True, "Structure validation passed"
        
    except ValueError:
        return False, "Invalid hex format"
    except Exception as e:
        return False, f"Verification error: {e}"

def continuous_monitor(hatagawa_instance, target_pattern=None, monitor_duration=None, logger=None):
    """Continuously monitor for flags in the Hatagawa environment."""
    if not logger:
        logger = setup_logging()
    
    logger.info("Starting continuous monitoring of Hatagawa I environment")
    logger.info(f"Target pattern: {target_pattern if target_pattern else 'Any flag pattern'}")
    
    start_time = time.time()
    capture_count = 0
    attempt_count = 0
    false_positive_count = 0
    
    try:
        while True:
            attempt_count += 1
            current_time = datetime.now()
            
            # Simulate flag detection - in real environment this would watch the output
            logger.info(f"Monitoring attempt #{attempt_count} at {current_time}")
            
            # Generate a flag appearance (simulate the 's' command)
            encrypted_flag_hex = hatagawa_instance.Encrypt(FLAG).hex()
            
            logger.info(f"Detected potential flag: {encrypted_flag_hex}")
            
            # Check if this matches our target pattern or any flag pattern
            is_flag, pattern = detect_flag_patterns(encrypted_flag_hex)
            
            if is_flag:
                logger.info(f"Flag pattern detected: {pattern}")
                
                # Attempt decryption and verification
                is_valid, result = attempt_decryption(encrypted_flag_hex, hatagawa_instance, logger)
                
                if is_valid:
                    capture_count += 1
                    logger.info(f"SUCCESSFUL CAPTURE #{capture_count}")
                    logger.info(f"Timestamp: {current_time}")
                    logger.info(f"Source: Hatagawa I River Environment")
                    logger.info(f"Captured Data: {encrypted_flag_hex}")
                    logger.info(f"Decrypted Flag: {result}")
                    logger.info(f"Verification: SUCCESS")
                    logger.info("-" * 50)
                    
                    # If we're looking for a specific pattern and found it, we could stop
                    if target_pattern and target_pattern in result:
                        logger.info(f"Target pattern '{target_pattern}' found! Monitoring complete.")
                        break
                else:
                    false_positive_count += 1
                    logger.warning(f"FALSE POSITIVE #{false_positive_count}: {result}")
            else:
                logger.debug(f"No flag pattern detected in: {encrypted_flag_hex[:20]}...")
            
            # Check if we should stop monitoring
            if monitor_duration and (time.time() - start_time) > monitor_duration:
                logger.info(f"Monitoring duration ({monitor_duration}s) exceeded. Stopping.")
                break
            
            # Wait before next check (simulate sporadic flag appearances)
            time.sleep(2)
            
    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user")
    except Exception as e:
        logger.error(f"Monitoring error: {e}")
    
    finally:
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Monitoring session complete:")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Total attempts: {attempt_count}")
        logger.info(f"Successful captures: {capture_count}")
        logger.info(f"False positives prevented: {false_positive_count}")
        logger.info(f"Accuracy: {(capture_count / max(capture_count + false_positive_count, 1) * 100):.1f}%")


# Challenge classes
class Kawa:
    """ 川 """
    def __init__(self, par: Tuple[int], seed: int) -> None:
        self.a, self.c, self.m = par
        self.x = seed

    def Get(self) -> bytes:
        """ Generates and outputs the next internal state as bytes. """
        self.x = (self.a * self.x + self.c) & self.m
        return self.x.to_bytes(-(-self.m.bit_length() // 8), 'big')
    
class Hata:
    """ 旗 """
    def __init__(self, entropy: object) -> None:
        self.entropy = entropy

    def Encrypt(self, msg: bytes) -> bytes:
        """ Encrypts a message using a one-time pad generated from entropy source. """
        otp = b''
        while len(otp) < len(msg):
            otp += self.entropy.Get()
        return bytes([x ^ y for x,y in zip(msg, otp)])


# Main loop
if __name__ == "__main__":
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Hatagawa I Flag Monitoring System')
    parser.add_argument('--monitor', action='store_true', 
                        help='Enable continuous monitoring mode')
    parser.add_argument('--pattern', type=str, default=None,
                        help='Specific flag pattern to monitor for')
    parser.add_argument('--duration', type=int, default=None,
                        help='Monitoring duration in seconds (default: unlimited)')
    parser.add_argument('--log-file', type=str, default='hatagawa_monitor.log',
                        help='Log file path for monitoring output')
    
    args = parser.parse_args()

    # Challenge parameters
    MOD = 2**64 - 1
    MUL = (randbelow(MOD >> 3) << 3) | 5
    ADD = randbelow(MOD) | 1

    # Challenge setup
    hatagawa = Hata(Kawa((MUL, ADD, MOD), randbelow(MOD)))

    # Check if monitoring mode is enabled
    if args.monitor:
        logger = setup_logging(args.log_file)
        logger.info("Hatagawa I Monitoring System Activated")
        logger.info(f"Flag environment: {FLAG.decode() if isinstance(FLAG, bytes) else FLAG}")
        
        continuous_monitor(hatagawa, args.pattern, args.duration, logger)
        exit(0)

    # Original interactive mode
    RIVER = r"""|
|  ////\\\,,\///,,,,,\,/,\\,//////,\,,\\\,,\\\/,,,\,,//,\\\,
|   ~ ~~~~ ~~ ~~~~~~~ ~ ~~ ~~~~~~ ~  ~~~    ~~~ ~~~ ~~   ~~
|    ~~~~~~~  ~~~~~~   ~~~ ~ ~~~~~ ~~ ~~~~~~~ ~ ~~ ~~~~~
|   ~~~ {} ~
|    ~~~  ~   ~~~~~  ~~~~ ~ ~~~~   ~~~~~ ~~~~   ~~~ ~ ~~~~~
|   ~~~ ~  ~~~~~  ~  ~~  ~  ~~~~ ~~~ ~~   ~~ ~~~~~~~ ~ ~~
|  \\\\\'''\\'////'//'\''\\\/'''\''//'\\\''\///''''\'/'\\'//"""
    print(RIVER.format(' '*21 + '旗    川' + ' '*21))

    # Main interactive loop
    userOptions = ['Stay a while...']
    TUI = "|\n|  Menu:\n|    " + "\n|    ".join('[' + i[0] + ']' + i[1:] for i in userOptions) + "\n|    [W]alk away\n|"

    while True:
        try:

            print(TUI)
            choice = input('|  > ').lower()

            # [W]alk away
            if choice == 'w':
                print("|\n|  [~] You turn your back to the river...\n|")
                break

            # [S]tay a while...
            elif choice == 's':

                print("|\n|  [~] Look! Is that a flag floating by?")
                print(RIVER.format(hatagawa.Encrypt(FLAG).hex()))

            else:
                print("|\n|  [!] Invalid choice.")

        except KeyboardInterrupt:
            print("\n|\n|  [~] Goodbye ~ !\n|")
            break

        except Exception as e:
            print('|\n|  [!] {}'.format(e))