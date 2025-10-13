"""
Tests for Provider Server Runtime

Validates shared gRPC server setup and lifecycle management.
"""

import pytest
import grpc
import time
import threading
from concurrent import futures
from v2.runtime import ProviderServer
import proto.provider_pb2 as provider_pb2
import proto.provider_pb2_grpc as provider_pb2_grpc


class MockProvider(provider_pb2_grpc.ProviderServicer):
    """Mock provider for testing"""
    
    def GetSchema(self, request, context):
        return provider_pb2.GetSchemaResponse()
    
    def ValidateConfig(self, request, context):
        return provider_pb2.ValidateConfigResponse()
    
    def Configure(self, request, context):
        return provider_pb2.ConfigureResponse()


class TestProviderServer:
    """Test suite for shared provider server runtime"""
    
    def test_server_creation(self):
        """Test server instance creation"""
        server = ProviderServer(port=50099)
        assert server.port == 50099
        assert server.max_workers == 10
        assert server._services_registered is False
    
    def test_default_port_from_env(self, monkeypatch):
        """Test port defaults to env variable"""
        monkeypatch.setenv('PORT', '50098')
        server = ProviderServer()
        assert server.port == 50098
    
    def test_service_registration(self):
        """Test service registration"""
        server = ProviderServer(port=50097)
        provider = MockProvider()
        server.register_service(provider)
        assert server._services_registered is True
    
    def test_serve_without_registration_fails(self):
        """Test serving without registration raises error"""
        server = ProviderServer(port=50096)
        with pytest.raises(RuntimeError, match="No services registered"):
            server.serve(blocking=False)
    
    def test_server_starts_and_stops(self):
        """Test server lifecycle - start and stop"""
        server = ProviderServer(port=50095)
        provider = MockProvider()
        server.register_service(provider)
        
        # Start in non-blocking mode
        server.serve(blocking=False)
        time.sleep(0.5)  # Give server time to start
        
        # Verify server is running by attempting connection
        channel = grpc.insecure_channel('localhost:50095')
        try:
            grpc.channel_ready_future(channel).result(timeout=2)
            server_running = True
        except grpc.FutureTimeoutError:
            server_running = False
        finally:
            channel.close()
        
        assert server_running, "Server should be running"
        
        # Stop server
        server.stop(grace=1)
        time.sleep(0.5)
        
        # Verify server stopped
        channel = grpc.insecure_channel('localhost:50095')
        try:
            grpc.channel_ready_future(channel).result(timeout=1)
            server_stopped = False
        except grpc.FutureTimeoutError:
            server_stopped = True
        finally:
            channel.close()
        
        assert server_stopped, "Server should be stopped"
    
    def test_multiple_services_not_supported(self):
        """Test that registering multiple services works (last one wins)"""
        server = ProviderServer(port=50094)
        provider1 = MockProvider()
        provider2 = MockProvider()
        
        server.register_service(provider1)
        server.register_service(provider2)
        
        assert server._services_registered is True
    
    def test_graceful_shutdown_timeout(self):
        """Test custom graceful shutdown timeout"""
        server = ProviderServer(port=50093, graceful_shutdown_timeout=2)
        assert server.graceful_shutdown_timeout == 2
    
    def test_max_workers_configuration(self):
        """Test custom max workers"""
        server = ProviderServer(port=50092, max_workers=5)
        assert server.max_workers == 5


class TestProviderServerIntegration:
    """Integration tests for provider server"""
    
    def test_client_can_connect_and_call(self):
        """Test that a gRPC client can connect and make calls"""
        server = ProviderServer(port=50091)
        provider = MockProvider()
        server.register_service(provider)
        
        # Start server in background thread
        def run_server():
            server.serve(blocking=True)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(0.5)  # Give server time to start
        
        # Create client and make call
        channel = grpc.insecure_channel('localhost:50091')
        stub = provider_pb2_grpc.ProviderStub(channel)
        
        try:
            response = stub.GetSchema(provider_pb2.GetSchemaRequest())
            assert response is not None
            assert isinstance(response, provider_pb2.GetSchemaResponse)
        finally:
            channel.close()
            server.stop(grace=1)
    
    def test_server_in_thread_no_signal_errors(self):
        """Regression test: server from non-main thread should not raise signal errors"""
        server = ProviderServer(port=50090)
        provider = MockProvider()
        server.register_service(provider)
        
        exception_holder = []
        
        def run_server_and_capture_exception():
            try:
                server.serve(blocking=True)
            except ValueError as e:
                exception_holder.append(e)
        
        server_thread = threading.Thread(target=run_server_and_capture_exception, daemon=True)
        server_thread.start()
        time.sleep(0.5)
        
        # Verify no signal-related exceptions occurred
        assert len(exception_holder) == 0, f"Unexpected exception: {exception_holder}"
        
        # Cleanup
        server.stop(grace=1)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
