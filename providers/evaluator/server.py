import grpc
import os
import json
import uuid
from concurrent import futures
from typing import Dict, Any, List
from google.protobuf.struct_pb2 import Struct
from google.protobuf.json_format import MessageToDict, ParseDict

import proto.provider_pb2 as provider_pb2
import proto.provider_pb2_grpc as provider_pb2_grpc

class EvaluatorProvider(provider_pb2_grpc.ProviderServicer):
    def __init__(self):
        self.resources: Dict[str, Dict[str, Any]] = {}

    def _create_diagnostic(self, severity, summary, detail=""):
        return provider_pb2.Diagnostic(severity=severity, summary=summary, detail=detail)

    def Configure(self, request, context):
        return provider_pb2.ConfigureResponse()

    def ApplyResourceChange(self, request, context):
        config = MessageToDict(request.config)
        resource_name = config.get('aiclResourceName', '')
        
        if request.type_name == "grade":
            return self._grade_response(resource_name, config, request.type_name)
        elif request.type_name == "experiment":
            return self._run_experiment(resource_name, config, request.type_name)
        elif request.type_name == "compare":
            return self._compare_results(resource_name, config, request.type_name)
        else:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, f"Unsupported resource type: {request.type_name}")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

    def _grade_response(self, resource_name, config, type_name):
        """Grade a response against criteria"""
        response_text = config.get('response', '')
        criteria = config.get('criteria', [])
        context_provided = config.get('context', '')
        
        if not response_text:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "No response provided for grading")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

        # Calculate metrics
        scores = {}
        total_score = 0
        max_score = 0
        
        for criterion in criteria:
            name = criterion.get('name', 'unnamed')
            check_type = criterion.get('type', 'contains')
            value = criterion.get('value', '')
            weight = criterion.get('weight', 1)
            
            max_score += weight
            
            # Check criteria
            score = 0
            if check_type == 'contains':
                if value.lower() in response_text.lower():
                    score = weight
            elif check_type == 'not_contains':
                if value.lower() not in response_text.lower():
                    score = weight
            elif check_type == 'min_length':
                if len(response_text) >= int(value):
                    score = weight
            elif check_type == 'max_length':
                if len(response_text) <= int(value):
                    score = weight
            
            scores[name] = {
                'score': score,
                'max': weight,
                'passed': score == weight
            }
            total_score += score
        
        # Calculate characteristics
        characteristics = {
            'response_length': len(response_text),
            'word_count': len(response_text.split()),
            'contains_code': '```' in response_text or 'def ' in response_text or 'class ' in response_text,
            'context_size': len(context_provided) if context_provided else 0
        }
        
        # Extract what the model focused on
        focus_keywords = []
        if context_provided:
            # Simple keyword extraction - look for terms from context that appear in response
            context_words = set(context_provided.lower().split())
            response_words = set(response_text.lower().split())
            common = context_words & response_words
            focus_keywords = list(common)[:20]  # Top 20 common terms
        
        output_attributes = {
            'total_score': total_score,
            'max_score': max_score,
            'percentage': (total_score / max_score * 100) if max_score > 0 else 0,
            'scores': scores,
            'characteristics': characteristics,
            'focus_keywords': focus_keywords,
            'passed': total_score == max_score
        }
        
        resource_id = f"grade-{resource_name}" if resource_name else f"grade-{uuid.uuid4().hex[:8]}"
        
        output_struct = Struct()
        ParseDict(output_attributes, output_struct)
        
        new_state = provider_pb2.ResourceState(
            id=resource_id,
            type=type_name,
            attributes=output_struct,
            status='ready'
        )
        return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)

    def _run_experiment(self, resource_name, config, type_name):
        """Run an experiment with metadata tracking"""
        experiment_id = config.get('experiment_id', uuid.uuid4().hex[:8])
        model = config.get('model', 'unknown')
        context_type = config.get('context_type', 'unknown')
        context_size = config.get('context_size', 0)
        response = config.get('response', '')
        
        output_attributes = {
            'experiment_id': experiment_id,
            'model': model,
            'context_type': context_type,
            'context_size': context_size,
            'response': response,
            'response_length': len(response),
            'word_count': len(response.split()),
            'timestamp': str(uuid.uuid1())
        }
        
        resource_id = f"experiment-{experiment_id}"
        
        output_struct = Struct()
        ParseDict(output_attributes, output_struct)
        
        new_state = provider_pb2.ResourceState(
            id=resource_id,
            type=type_name,
            attributes=output_struct,
            status='ready'
        )
        return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)

    def _compare_results(self, resource_name, config, type_name):
        """Compare multiple experiment or grade results"""
        results = config.get('results', [])
        
        if not results:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "No results provided for comparison")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
        
        comparison = {
            'total_experiments': len(results),
            'results': results
        }
        
        # Calculate statistics from grade results (which have total_score/percentage)
        if results:
            # Support both old 'score' and new 'percentage' or 'total_score' fields
            percentages = []
            for r in results:
                if 'percentage' in r:
                    # Convert to float if it's a string from interpolation
                    pct = float(r['percentage']) if isinstance(r['percentage'], (str, int, float)) else 0
                    percentages.append(pct)
                elif 'total_score' in r and 'max_score' in r:
                    total = float(r['total_score']) if isinstance(r['total_score'], (str, int, float)) else 0
                    max_score = float(r.get('max_score', 1)) if isinstance(r.get('max_score', 1), (str, int, float)) else 1
                    percentages.append((total / max_score * 100) if max_score > 0 else 0)
                elif 'score' in r:
                    score = float(r['score']) if isinstance(r['score'], (str, int, float)) else 0
                    percentages.append(score)
            
            if percentages:
                comparison['avg_percentage'] = sum(percentages) / len(percentages)
                comparison['max_percentage'] = max(percentages)
                comparison['min_percentage'] = min(percentages)
                # Handle passed field - convert string 'True'/'False' to boolean
                comparison['all_passed'] = all(
                    r.get('passed') in [True, 'True', 'true', 1, '1'] for r in results
                )
        
        resource_id = f"compare-{resource_name}" if resource_name else f"compare-{uuid.uuid4().hex[:8]}"
        
        output_struct = Struct()
        ParseDict(comparison, output_struct)
        
        new_state = provider_pb2.ResourceState(
            id=resource_id,
            type=type_name,
            attributes=output_struct,
            status='ready'
        )
        return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)

    def DeleteResource(self, request, context):
        return provider_pb2.DeleteResourceResponse()

    def GetSchema(self, request, context):
        return provider_pb2.GetSchemaResponse()

    def ReadResource(self, request, context):
        return provider_pb2.ReadResourceResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    provider_pb2_grpc.add_ProviderServicer_to_server(EvaluatorProvider(), server)
    port = os.getenv("PORT", "50051")
    server.add_insecure_port(f'[::]:{port}')
    print(f"Evaluator provider listening on port {port}...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
