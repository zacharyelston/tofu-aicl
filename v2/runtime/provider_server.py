"""
Provider Server Runtime

Shared gRPC server setup for AICL providers.
Eliminates 50+ lines of boilerplate per provider.
"""

import grpc
import os
import signal
import sys
from concurrent import futures
from typing import Optional
import proto.provider_pb2_grpc as provider_pb2_grpc


class ProviderServer:
    """
    Standardized gRPC server for AICL providers
    
    Usage:
        from v2.runtime import ProviderServer
        
        class MyProvider(provider_pb2_grpc.ProviderServicer):
            # ... implement provider logic ...
            pass
        
        if __name__ == '__main__':
            server = ProviderServer()
            server.register_service(MyProvider())
            server.serve()
    """
    
    def __init__(
        self,
        port: Optional[int] = None,
        max_workers: int = 10,
        graceful_shutdown_timeout: int = 5
    ):
        """
        Initialize provider server
        
        Args:
            port: Port to listen on (defaults to PORT env var or 50051)
            max_workers: Max gRPC worker threads
            graceful_shutdown_timeout: Seconds to wait for graceful shutdown
        """
        # Get port from env or parameter
        self.port = port or int(os.getenv('PORT', '50051'))
        self.max_workers = max_workers
        self.graceful_shutdown_timeout = graceful_shutdown_timeout
        
        # Create gRPC server
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
        self._services_registered = False
    
    def register_service(self, servicer: provider_pb2_grpc.ProviderServicer):
        """
        Register a provider service
        
        Args:
            servicer: Provider implementation (subclass of ProviderServicer)
        """
        provider_pb2_grpc.add_ProviderServicer_to_server(servicer, self.server)
        self._services_registered = True
    
    def serve(self, blocking: bool = True):
        """
        Start the server
        
        Args:
            blocking: If True, blocks until interrupted. If False, returns immediately.
        """
        if not self._services_registered:
            raise RuntimeError("No services registered. Call register_service() first.")
        
        # Bind to port
        self.server.add_insecure_port(f'[::]:{self.port}')
        
        # Start server
        self.server.start()
        print(f"Provider server started on port {self.port}")
        
        if blocking:
            # Setup signal handlers for graceful shutdown (only in main thread)
            import threading
            if threading.current_thread() is threading.main_thread():
                def handle_shutdown(signum, frame):
                    print("\nShutting down gracefully...")
                    self.server.stop(self.graceful_shutdown_timeout)
                    sys.exit(0)
                
                signal.signal(signal.SIGINT, handle_shutdown)
                signal.signal(signal.SIGTERM, handle_shutdown)
            
            # Wait for termination
            self.server.wait_for_termination()
    
    def stop(self, grace: Optional[int] = None):
        """
        Stop the server
        
        Args:
            grace: Grace period in seconds (defaults to graceful_shutdown_timeout)
        """
        grace = grace or self.graceful_shutdown_timeout
        self.server.stop(grace)


def create_provider_server(
    servicer: provider_pb2_grpc.ProviderServicer,
    port: Optional[int] = None,
    **kwargs
) -> ProviderServer:
    """
    Create and start a provider server (convenience function)
    
    Args:
        servicer: Provider implementation
        port: Port to listen on
        **kwargs: Additional ProviderServer arguments
        
    Returns:
        ProviderServer instance
        
    Usage:
        from v2.runtime import create_provider_server
        
        if __name__ == '__main__':
            create_provider_server(MyProvider())
    """
    server = ProviderServer(port=port, **kwargs)
    server.register_service(servicer)
    server.serve(blocking=True)
    return server
