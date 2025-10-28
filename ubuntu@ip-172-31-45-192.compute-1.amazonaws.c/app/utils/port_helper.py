import socket
import random
from typing import List, Optional
from app.config import settings


class PortAllocator:
    """Utility class for managing port allocation for browser sessions."""
    
    def __init__(self):
        self.used_ports: set = set()
        self.port_range = range(settings.port_start, settings.port_end + 1)
    
    def is_port_available(self, port: int) -> bool:
        """Check if a port is available for use."""
        if port in self.used_ports:
            return False
        
        # Test if port is actually available on the system
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return True
            except OSError:
                return False
    
    def get_available_port(self) -> Optional[int]:
        """Get an available port from the configured range."""
        # Create a shuffled list of ports to randomize allocation
        available_ports = [p for p in self.port_range if self.is_port_available(p)]
        
        if not available_ports:
            return None
        
        # Return a random available port
        port = random.choice(available_ports)
        self.used_ports.add(port)
        return port
    
    def release_port(self, port: int) -> bool:
        """Release a port back to the pool."""
        if port in self.used_ports:
            self.used_ports.remove(port)
            return True
        return False
    
    def get_available_count(self) -> int:
        """Get the count of available ports."""
        return len([p for p in self.port_range if self.is_port_available(p)])
    
    def get_used_ports(self) -> List[int]:
        """Get list of currently used ports."""
        return list(self.used_ports)


# Global port allocator instance
port_allocator = PortAllocator()

