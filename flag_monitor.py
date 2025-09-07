#!/usr/bin/env python3
"""
Hatagawa I Flag Monitoring System
Continuously monitors the Hatagawa I environment for flags and captures them accurately.
"""

import socket
import time
import re
import logging
from typing import List, Optional, Dict, Set
from datetime import datetime
import threading
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hatagawa_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HatagawaMonitor:
    """Monitor for Hatagawa I flags"""
    
    def __init__(self, host: str = "34.252.33.37", port: int = 30653):
        self.host = host
        self.port = port
        self.captured_flags: Set[str] = set()
        self.flag_pattern = re.compile(r'[0-9a-fA-F]{32,}')  # Pattern for hex encoded flags
        self.monitoring = False
        self.connection_retries = 0
        self.max_retries = 50  # Increased for better persistence
        self.retry_delay = 10  # seconds, increased delay
        
        # Statistics
        self.total_connections = 0
        self.total_captures = 0
        self.start_time = None
        
    def connect_to_service(self) -> Optional[socket.socket]:
        """Establish connection to the Hatagawa I service"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            logger.info(f"Attempting to connect to {self.host}:{self.port}")
            sock.connect((self.host, self.port))
            logger.info("Successfully connected to Hatagawa I service")
            return sock
        except Exception as e:
            logger.error(f"Failed to connect to service: {e}")
            return None
    
    def send_command(self, sock: socket.socket, command: str) -> bool:
        """Send command to the service"""
        try:
            sock.send(f"{command}\n".encode())
            return True
        except Exception as e:
            logger.error(f"Failed to send command '{command}': {e}")
            return False
    
    def receive_data(self, sock: socket.socket, timeout: int = 10) -> str:
        """Receive data from the service"""
        try:
            sock.settimeout(timeout)
            data = b""
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                    
                    # Check if we have a complete response
                    decoded_data = data.decode('utf-8', errors='ignore')
                    if '[W]alk away' in decoded_data and '> ' in decoded_data:
                        break
                        
                except socket.timeout:
                    break
                except Exception as e:
                    logger.debug(f"Receive error: {e}")
                    break
            
            result = data.decode('utf-8', errors='ignore')
            logger.debug(f"Received {len(result)} characters: {result[:200]}...")
            return result
        except Exception as e:
            logger.error(f"Failed to receive data: {e}")
            return ""
    
    def detect_flags(self, data: str) -> List[str]:
        """Detect potential flags in the received data"""
        flags = []
        
        # Look for hex patterns that could be encrypted flags
        hex_matches = self.flag_pattern.findall(data)
        
        for match in hex_matches:
            # Filter out patterns that are clearly not flags
            if len(match) >= 32 and match not in self.captured_flags:
                flags.append(match)
                logger.info(f"New flag candidate detected: {match}")
        
        return flags
    
    def analyze_flag(self, flag_hex: str) -> Dict:
        """Analyze a captured flag for patterns and metadata"""
        analysis = {
            'hex': flag_hex,
            'length': len(flag_hex),
            'timestamp': datetime.now().isoformat(),
            'byte_length': len(flag_hex) // 2 if len(flag_hex) % 2 == 0 else (len(flag_hex) + 1) // 2,
            'source': 'Hatagawa I'
        }
        
        # Check if it could be an encrypted CTF flag
        if analysis['byte_length'] >= 16:  # Reasonable minimum for encrypted flag
            analysis['likely_encrypted_flag'] = True
        else:
            analysis['likely_encrypted_flag'] = False
        
        # Try to decode as bytes and look for patterns
        try:
            if len(flag_hex) % 2 == 0:
                flag_bytes = bytes.fromhex(flag_hex)
                analysis['bytes'] = list(flag_bytes)
                
                # Check for common CTF flag patterns
                # Many CTF flags start with known prefixes like "BHFlagY{", "flag{", etc.
                # when XORed, these might show patterns
                potential_prefixes = [b'BHFlagY{', b'flag{', b'FLAG{', b'CTF{']
                
                for prefix in potential_prefixes:
                    if len(flag_bytes) >= len(prefix):
                        # Try XOR with this prefix to see if we get readable text
                        key_candidate = bytes([a ^ b for a, b in zip(flag_bytes[:len(prefix)], prefix)])
                        analysis[f'potential_key_for_{prefix.decode()}'] = key_candidate.hex()
                        
                        # Try to decrypt the whole message with this key pattern
                        if len(key_candidate) > 0:
                            decrypted = self.attempt_xor_decrypt(flag_bytes, key_candidate)
                            if decrypted:
                                analysis[f'potential_decryption_{prefix.decode()}'] = decrypted
                
        except Exception as e:
            analysis['decode_error'] = str(e)
            
        return analysis
    
    def attempt_xor_decrypt(self, ciphertext: bytes, key_pattern: bytes) -> str:
        """Attempt to decrypt using XOR with a repeating key pattern"""
        try:
            if not key_pattern:
                return ""
                
            decrypted = []
            for i, byte in enumerate(ciphertext):
                key_byte = key_pattern[i % len(key_pattern)]
                decrypted.append(byte ^ key_byte)
            
            result = bytes(decrypted)
            # Check if result looks like readable text (contains printable characters)
            if all(32 <= b <= 126 for b in result):
                return result.decode('ascii')
            else:
                return ""
        except:
            return ""
    
    def capture_flag(self, sock: socket.socket) -> List[str]:
        """Attempt to capture a flag by triggering the service"""
        captured_flags = []
        
        try:
            # Send 'stay a while' command to trigger flag display
            logger.info("Triggering flag display...")
            if self.send_command(sock, 's'):
                # Receive the response
                response = self.receive_data(sock)
                logger.debug(f"Received response: {response[:200]}...")
                
                # Detect flags in the response
                flags = self.detect_flags(response)
                
                for flag in flags:
                    if flag not in self.captured_flags:
                        self.captured_flags.add(flag)
                        captured_flags.append(flag)
                        
                        # Analyze the flag
                        analysis = self.analyze_flag(flag)
                        
                        # Log the capture
                        logger.info(f"FLAG CAPTURED: {flag}")
                        logger.info(f"Analysis: {json.dumps(analysis, indent=2)}")
                        
                        # Save to file
                        self.save_flag_to_file(flag, analysis)
            
        except Exception as e:
            logger.error(f"Error during flag capture: {e}")
        
        return captured_flags
    
    def save_flag_to_file(self, flag: str, analysis: Dict):
        """Save captured flag to file"""
        try:
            with open('captured_flags.json', 'a') as f:
                flag_data = {
                    'flag': flag,
                    'analysis': analysis
                }
                f.write(json.dumps(flag_data) + '\n')
        except Exception as e:
            logger.error(f"Failed to save flag to file: {e}")
    
    def monitor_session(self, sock: socket.socket):
        """Monitor a single session"""
        try:
            # Receive initial greeting
            greeting = self.receive_data(sock)
            logger.info("Connected to Hatagawa I service")
            logger.debug(f"Initial greeting: {greeting[:100]}...")
            
            capture_count = 0
            max_captures_per_session = 10
            
            while self.monitoring and capture_count < max_captures_per_session:
                # Capture flags
                new_flags = self.capture_flag(sock)
                
                if new_flags:
                    capture_count += len(new_flags)
                    logger.info(f"Captured {len(new_flags)} new flags in this session")
                
                # Wait before next capture attempt
                time.sleep(2)
            
            # Send walk away command to close gracefully
            self.send_command(sock, 'w')
            
        except Exception as e:
            logger.error(f"Error in monitoring session: {e}")
        finally:
            try:
                sock.close()
            except:
                pass
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        logger.info("Starting Hatagawa I flag monitoring...")
        logger.info(f"Target: {self.host}:{self.port}")
        self.monitoring = True
        self.start_time = datetime.now()
        
        while self.monitoring:
            try:
                # Attempt to connect
                sock = self.connect_to_service()
                
                if sock:
                    # Reset retry counter on successful connection
                    self.connection_retries = 0
                    self.total_connections += 1
                    
                    # Monitor this session
                    self.monitor_session(sock)
                    
                else:
                    # Connection failed, increment retry counter
                    self.connection_retries += 1
                    
                    if self.connection_retries >= self.max_retries:
                        logger.error(f"Max retries ({self.max_retries}) reached. Stopping monitoring.")
                        break
                    
                    logger.warning(f"Connection failed. Retry {self.connection_retries}/{self.max_retries} in {self.retry_delay} seconds...")
                    
                    # Exponential backoff with jitter
                    delay = min(self.retry_delay * (1.5 ** min(self.connection_retries, 10)), 300)  # Max 5 min
                    time.sleep(delay)
                
                # Brief pause between sessions
                if self.monitoring:
                    time.sleep(5)
                    
                # Log periodic status
                if self.total_connections > 0 and self.total_connections % 10 == 0:
                    self.log_status()
                    
            except KeyboardInterrupt:
                logger.info("Monitoring interrupted by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in monitoring loop: {e}")
                time.sleep(self.retry_delay)
        
        self.monitoring = False
        logger.info("Flag monitoring stopped")
        self.log_final_report()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        logger.info("Stopping flag monitoring...")
        self.monitoring = False
    
    def log_status(self):
        """Log current monitoring status"""
        if self.start_time:
            uptime = datetime.now() - self.start_time
            logger.info(f"Monitoring Status - Uptime: {uptime}, Connections: {self.total_connections}, Flags: {len(self.captured_flags)}")
    
    def log_final_report(self):
        """Log final monitoring report"""
        if self.start_time:
            total_time = datetime.now() - self.start_time
            logger.info("="*50)
            logger.info("FINAL MONITORING REPORT")
            logger.info("="*50)
            logger.info(f"Total monitoring time: {total_time}")
            logger.info(f"Total connections made: {self.total_connections}")
            logger.info(f"Total flags captured: {len(self.captured_flags)}")
            logger.info(f"Flags captured: {list(self.captured_flags)}")
            logger.info("="*50)
    
    def get_statistics(self) -> Dict:
        """Get monitoring statistics"""
        uptime = None
        if self.start_time:
            uptime = str(datetime.now() - self.start_time)
            
        return {
            'total_flags_captured': len(self.captured_flags),
            'captured_flags': list(self.captured_flags),
            'monitoring_active': self.monitoring,
            'total_connections': self.total_connections,
            'uptime': uptime,
            'target_host': self.host,
            'target_port': self.port
        }

def main():
    """Main function"""
    monitor = HatagawaMonitor()
    
    try:
        # Start monitoring in a separate thread so we can handle interrupts
        monitor_thread = threading.Thread(target=monitor.start_monitoring)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Keep main thread alive and handle interrupts
        while monitor.monitoring:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        monitor.stop_monitoring()
        
    # Print final statistics
    stats = monitor.get_statistics()
    logger.info(f"Final statistics: {json.dumps(stats, indent=2)}")

if __name__ == "__main__":
    main()