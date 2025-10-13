import grpc
import os
import subprocess
from concurrent import futures
from google.protobuf.struct_pb2 import Struct

import proto.provider_pb2 as provider_pb2
import proto.provider_pb2_grpc as provider_pb2_grpc

class CommandAssertionProvider(provider_pb2_grpc.ProviderServicer):

    def _create_diagnostic(self, severity, summary, detail=""):
        return provider_pb2.Diagnostic(severity=severity, summary=summary, detail=detail)

    def GetSchema(self, request, context):
        # This provider has no persistent resources, only a validation action.
        return provider_pb2.GetSchemaResponse()

    def Validate(self, request, context):
        command = request.input.get('command')
        input_data = request.input.get('input', '')

        if not command:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "'command' is a required input for validation.")
            return provider_pb2.ValidateResponse(success=False, diagnostics=[diag])

        try:
            process = subprocess.run(
                command,
                input=input_data,
                text=True,
                capture_output=True,
                shell=True # Use with caution
            )

            output_struct = Struct()
            output_struct.update({
                "stdout": process.stdout,
                "stderr": process.stderr,
                "exit_code": process.returncode
            })

            return provider_pb2.ValidateResponse(success=True, output=output_struct)

        except Exception as e:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "Failed to execute command", str(e))
            return provider_pb2.ValidateResponse(success=False, diagnostics=[diag])

    # --- Minimal Implementations for other required RPCs ---
    def Configure(self, request, context):
        return provider_pb2.ConfigureResponse()

    def ApplyResourceChange(self, request, context):
        diag = self._create_diagnostic(provider_pb2.Diagnostic.WARNING, "This provider does not manage resources.")
        return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

    def ReadResource(self, request, context):
        return provider_pb2.ReadResourceResponse()

    def DeleteResource(self, request, context):
        return provider_pb2.DeleteResourceResponse()

    def Execute(self, request, context):
        yield provider_pb2.ExecuteResponse(log="Execute is not applicable for this provider.")

    def HealthCheck(self, request, context):
        return provider_pb2.HealthCheckResponse(healthy=True, version="0.1.0")

if __name__ == '__main__':
    from v2.runtime import create_provider_server
    create_provider_server(CommandAssertionProvider())