import json
import logging
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_api_key.models import APIKey
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from typing import Dict, List, Any, Optional
from .ai_mapping import suggest_mappings, parse_nl_mappings
from .ai_llm import query_llm, is_ollama_available, suggest_mappings_llm
from django.conf import settings

logger = logging.getLogger(__name__)

class MappingGenerator(APIView):
    """
    API endpoint for generating schema mappings using AI.
    Requires a valid API key for authentication.
    """
    permission_classes = [HasAPIKey]
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        """
        Generate schema mappings based on source and target schemas with an optional natural language description.
        
        Request format:
        {
            "source_schema": [
                {"name": "column1", "type": "string", "description": "Description of column1"},
                ...
            ],
            "target_schema": [
                {"name": "target_col1", "type": "string", "description": "Description of target_col1"},
                ...
            ],
            "description": "Natural language description of how to map the schemas",
            "provider": "perplexity"  # Optional: "heuristic", "ollama", or "perplexity"
        }
        
        Response format:
        {
            "mappings": [
                {
                    "target": "target_column_name",
                    "source": "source_column_name",
                    "transform": "optional_transform_expression",
                    "cast": "optional_target_type",
                    "confidence": 0.95,
                    "rationale": "Explanation of the mapping"
                },
                ...
            ],
            "unresolved": [
                {
                    "target": "unmapped_target_column",
                    "reasons": ["No matching source column found"]
                }
            ]
        }
        """
        try:
            data = request.data
            source_schema = data.get('source_schema', [])
            target_schema = data.get('target_schema', [])
            description = data.get('description', '')
            provider = data.get('provider', 'heuristic')
            
            if not source_schema or not target_schema:
                return Response(
                    {"error": "Both source_schema and target_schema are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # If there's a description, try to use NLP to parse it
            if description:
                source_columns = [col['name'] for col in source_schema if 'name' in col]
                target_columns = [col['name'] for col in target_schema if 'name' in col]
                
                # First try to parse the natural language description
                parsed = parse_nl_mappings(description, source_columns, target_columns)
                
                if parsed.get('mappings'):
                    return Response(parsed)
            
            # Fall back to AI-based mapping if no description or parsing failed
            if provider == 'perplexity' or (provider == 'ollama' and is_ollama_available()):
                result = suggest_mappings_llm(
                    source=source_schema,
                    target=target_schema,
                    model="sonar" if provider == 'perplexity' else None
                )
            else:
                # Fall back to heuristic-based mapping
                result = suggest_mappings(
                    source=source_schema,
                    target=target_schema
                )
            
            return Response(result)
            
        except Exception as e:
            logger.exception("Error generating mappings")
            return Response(
                {"error": f"Failed to generate mappings: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class APIKeyManager(APIView):
    """
    API endpoint for managing API keys.
    Requires authentication to create/revoke keys.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Create a new API key for the authenticated user.
        
        Request format:
        {
            "name": "My API Key",
            "expiry_days": 30  # Optional, key will not expire if not provided
        }
        """
        try:
            name = request.data.get('name', 'Datamplify Mapping API Key')
            expiry_days = request.data.get('expiry_days')
            
            # Create API key
            api_key, key = APIKey.objects.create_key(
                name=f"{request.user.username}:{name}",
                expiry_days=expiry_days
            )
            
            return Response({
                "name": api_key.name,
                "prefix": api_key.prefix,
                "key": key,  # Only time the full key is shown
                "created": api_key.created,
                "expires": api_key.expiry_date if hasattr(api_key, 'expiry_date') else None
            })
            
        except Exception as e:
            logger.exception("Error creating API key")
            return Response(
                {"error": f"Failed to create API key: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """List all API keys for the authenticated user"""
        try:
            user_prefix = f"{request.user.username}:"
            keys = APIKey.objects.filter(name__startswith=user_prefix)
            
            result = []
            for key in keys:
                result.append({
                    "id": key.id,
                    "name": key.name.replace(user_prefix, '', 1),
                    "prefix": key.prefix,
                    "created": key.created,
                    "expires": key.expiry_date if hasattr(key, 'expiry_date') else None,
                    "revoked": bool(key.revoked)
                })
                
            return Response(result)
            
        except Exception as e:
            logger.exception("Error listing API keys")
            return Response(
                {"error": f"Failed to list API keys: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, key_id):
        """Revoke an API key"""
        try:
            user_prefix = f"{request.user.username}:"
            key = APIKey.objects.get(id=key_id, name__startswith=user_prefix)
            key.delete()
            return Response({"message": "API key revoked successfully"})
            
        except APIKey.DoesNotExist:
            return Response(
                {"error": "API key not found or access denied"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception("Error revoking API key")
            return Response(
                {"error": f"Failed to revoke API key: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
