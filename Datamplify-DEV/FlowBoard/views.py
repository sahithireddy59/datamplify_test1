from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction 
from Service.utils import generate_user_unique_code,file_save_1,s3,UUIDEncoder,CustomPaginator
from FlowBoard.serializers import Create_FLow,Update_FlowBoard
from FlowBoard import models as flow_model
from FlowBoard.services.publish import publish_flowboard
from app.scheduler.models import Scheduler
from Connections import models as conn_models
from authentication import models as auth_models
from authentication.utils import token_function
from drf_yasg.utils import swagger_auto_schema

from Monitor.utils import airflow_token
from datetime import datetime
from Datamplify import settings
from pytz import utc
import os,json,requests,uuid
from datetime import timezone
import time
import logging
from FlowBoard.ai_mapping import suggest_mappings, parse_nl_mappings
from FlowBoard.ai_llm import is_ollama_available, suggest_mappings_llm

logger = logging.getLogger(__name__)





class FlowBoard(APIView):

    serializer_class = Create_FLow
    @swagger_auto_schema(request_body=Create_FLow)
    @csrf_exempt
    @transaction.atomic
    def post(self, request):
        """
        To Create a FlowBoard and save and Create a DAG on it
        """
        tok1 = token_function(request)
        if tok1["status"]==200:
            user_id = tok1['user_id']
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                flow_name = serializer.validated_data['flow_name']
                flow = serializer.validated_data['flow_plan']
                drawflow = serializer.validated_data['drawflow']
                user = auth_models.UserProfile.objects.get(id=user_id)
                if flow_model.FlowBoard.objects.filter(Flow_name__exact=flow_name,user_id = user_id).exists():
                    return Response({'message':f'Flow name already Exists'},status=status.HTTP_406_NOT_ACCEPTABLE)  
                Flow_id = generate_user_unique_code(request,'FLOW')
                flow['dag_id'] = Flow_id
                flow['flow_name'] = flow_name
                flow['username'] = user.username
                flow['user_id'] = user_id
                configs_dir = os.path.join(settings.config_dir, 'FlowBoard', str(user_id))
                os.makedirs(configs_dir, exist_ok=True)
                file_path = os.path.join(configs_dir, f'{Flow_id}.json')
                with open(file_path, 'w') as f:
                    json.dump(flow,f, indent=4,cls=UUIDEncoder)
                file_data = drawflow.read().decode('utf-8')  
                file_path = file_save_1(file_data,'',Flow_id,'FlowBoard',"")
                created_flow = flow_model.FlowBoard.objects.create(
                    Flow_id=Flow_id,
                    Flow_name=flow_name,
                    DrawFlow=file_path['file_url'],
                    user_id=user
                )
                flow_data = {
                    'id': str(created_flow.id),
                    'flow_id': Flow_id,
                    'flow_name': flow_name,
                    'created_at': datetime.now(utc),
                    'updated_at': datetime.now(utc),
                    'parsed': False,
                    'schedule': None
                }
                # Auto-trigger DAG creation and execution
                try:
                    trigger_result = self._auto_trigger_dag(Flow_id, request)
                    if trigger_result.get('success'):
                        logger.info(f"Auto-triggered DAG for FlowBoard {Flow_id}: {trigger_result['message']}")
                    else:
                        logger.warning(f"Auto-trigger failed for FlowBoard {Flow_id}: {trigger_result['message']}")
                except Exception as e:
                    logger.error(f"Auto-trigger error for FlowBoard {Flow_id}: {str(e)}")
                
                return Response({'message':'Saved SucessFully','Flow_Board_id': str(created_flow.id)},status=status.HTTP_200_OK)
            else:
                return Response({'message':'Serializer Error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)
        
    serializer_class1 = Update_FlowBoard
    @swagger_auto_schema(request_body=Update_FlowBoard)

    def put(self, request):
        tok1 = token_function(request)
        if tok1["status"]==200:
            user_id = tok1['user_id']
            serializer = self.serializer_class1(data = request.data)
            if serializer.is_valid(raise_exception=True):
                id = serializer.validated_data['id']
                flow_name = serializer.validated_data['flow_name']
                flow = serializer.validated_data['flow_plan']
                drawflow = serializer.validated_data['drawflow']
                user = auth_models.UserProfile.objects.get(id=user_id)
                if flow_model.FlowBoard.objects.filter(Flow_name__exact=flow_name,user_id = user_id).exclude(id=id).exists():
                    return Response({'message':f'Flow name already Exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
                if flow_model.FlowBoard.objects.filter(id = id,user_id = tok1['user_id']).exists():
                    Flow_data = flow_model.FlowBoard.objects.get(id = id,user_id = tok1['user_id'])
                else:
                        return Response({'message':'Data Flow Not Created'},status=status.HTTP_404_NOT_FOUND)
                        
                flow['user_id'] = str(tok1['user_id'])
                flow['username'] = user.username
                flow['dag_id'] = Flow_data.Flow_id
                flow['flow_name'] = flow_name
                configs_dir = os.path.join(settings.config_dir, 'FlowBoard', str(user_id))
                os.makedirs(configs_dir, exist_ok=True)
                file_path = os.path.join(configs_dir, f'{Flow_data.Flow_id}.json')
                data = flow
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4,cls=UUIDEncoder)
                datasrc_key = Flow_data.DrawFlow.split('FlowBoard/')[1]
                file_data = drawflow.read().decode('utf-8')  
                file_path = file_save_1(file_data,'',Flow_data.Flow_id,'FlowBoard',f'Datamplify/FlowBoard/{datasrc_key}')
                updated_data = flow_model.FlowBoard.objects.filter(id = id).update(
                    Flow_name  = flow_name,
                    DrawFlow = file_path['file_url'],
                    updated_at=datetime.now(utc),
                    user_id = user
                )                
                
                # Auto-trigger DAG update and execution
                try:
                    trigger_result = self._auto_trigger_dag(Flow_data.Flow_id, request)
                    if trigger_result.get('success'):
                        logger.info(f"Auto-triggered DAG for updated FlowBoard {Flow_data.Flow_id}: {trigger_result['message']}")
                    else:
                        logger.warning(f"Auto-trigger failed for updated FlowBoard {Flow_data.Flow_id}: {trigger_result['message']}")
                except Exception as e:
                    logger.error(f"Auto-trigger error for updated FlowBoard {Flow_data.Flow_id}: {str(e)}")
                
                return Response({'message':'updated SucessFully','Flow_Board_id':str(id)},status=status.HTTP_200_OK)
            else:
                    return Response({'message':'Serializer Error'},status=status.HTTP_400_BAD_REQUEST)
        else:
                return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)
        


    def _auto_trigger_dag(self, dag_id, request):
        """
        Automatically trigger DAG creation and execution after FlowBoard save/update.
        Mirrors logic used by Flow_List._auto_trigger_dag but scoped to this class
        so calls like self._auto_trigger_dag(...) work.

        Args:
            dag_id (str): The FlowBoard ID to use as DAG ID
            request: The original HTTP request for auth forwarding
        Returns:
            dict: Result with success status and message
        """
        try:
            # Wait briefly for Airflow to pick up the new config file
            time.sleep(2)

            # Build internal URL to Monitor trigger endpoint
            scheme = 'https' if request.is_secure() else 'http'
            base = f"{scheme}://{request.get_host()}"
            # Important: do NOT include trailing slash before query params, since APPEND_SLASH=False
            trigger_url = f"{base}/v1/monitor/Trigger/{dag_id}?type=flowboard"

            # Forward auth header if present
            headers = {}
            if 'Authorization' in request.headers:
                headers['Authorization'] = request.headers.get('Authorization')

            # Retry trigger with timeout for DAG registration
            max_wait_seconds = 120
            interval = 2
            deadline = time.time() + max_wait_seconds

            while time.time() <= deadline:
                try:
                    resp = requests.post(trigger_url, headers=headers, timeout=10)
                    if resp.status_code in [200, 201]:
                        return {
                            'success': True,
                            'message': f'DAG {dag_id} triggered successfully',
                            'response': resp.json() if resp.content else {}
                        }
                    elif resp.status_code == 404:
                        # DAG not found yet, wait and retry
                        logger.info(f"DAG {dag_id} not found yet, retrying...")
                        time.sleep(interval)
                        continue
                    else:
                        return {
                            'success': False,
                            'message': f'Trigger failed with status {resp.status_code}: {resp.text}'
                        }
                except requests.RequestException as e:
                    logger.warning(f"Trigger request failed for {dag_id}: {e}")
                    time.sleep(interval)
                    continue

            return {
                'success': False,
                'message': f'DAG {dag_id} trigger timed out after {max_wait_seconds}s'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Auto-trigger error: {str(e)}'
            }


class MappingSuggest(APIView):
    @csrf_exempt
    def post(self, request):
        """
        Suggest schema mappings dynamically using free heuristics (no external AI).

        Request JSON:
        {
          "source": [{"name": "cust_id", "type": "int", "description": ""}, ...],
          "target": [{"name": "customer_id", "type": "integer"}, ...],
          "max_sources_per_target": 1,
          "to_attribute_mapper": false
        }

        Response JSON:
        {
          "mappings": [{"target": str, "source": str, "transform": str|null, "cast": str|null, "confidence": float, "rationale": str}],
          "unresolved": [{"target": str, "reasons": [str]}],
          "attribute_mapper": [[target, "", source_col, data_type]]  // when requested
        }
        """
        tok1 = token_function(request)
        if tok1.get("status") != 200:
            return Response({'message': tok1.get('message', 'Unauthorized')}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            payload = request.data if isinstance(request.data, dict) else {}
            source = payload.get('source') or []
            target = payload.get('target') or []
            max_sources_per_target = int(payload.get('max_sources_per_target', 1) or 1)

            ai_provider = payload.get('ai_provider', 'heuristic')  # heuristic, ollama, perplexity
            model = payload.get('model', None)
            result = None
            llm_meta = {}
            # Optional natural language instruction like: "map cust_id to customer_id; cast amount to double as total_amount"
            instruction = payload.get('instruction')
            nl_result = None
            if instruction:
                src_names = [s.get('name') for s in (source or []) if s.get('name')]
                tgt_names = [t.get('name') for t in (target or []) if t.get('name')]
                nl_result = parse_nl_mappings(instruction, src_names, tgt_names)
            
            # Try AI providers if requested
            if ai_provider == 'ollama' and is_ollama_available():
                llm_result = suggest_mappings_llm(source, target, model=model or DEFAULT_MODEL)
                llm_meta = {k: v for k, v in llm_result.items() if k not in ('mappings', 'unresolved')}
                if llm_result.get('mappings') or llm_result.get('unresolved'):
                    result = { 'mappings': llm_result.get('mappings', []), 'unresolved': llm_result.get('unresolved', []) }
            elif ai_provider in ['perplexity', 'google']:
                # Use AI (Perplexity or Google) for enhanced mapping suggestions
                from .ai_llm import query_llm
                import json
                
                # Build comprehensive prompt for AI
                source_cols = [f"{s.get('name')} ({s.get('type', 'unknown')})" for s in source]
                target_cols = [f"{t.get('name')} ({t.get('type', 'unknown')})" for t in target]
                
                prompt = f"""You are a data mapping expert. Create SQL mapping expressions for ETL data transformation.

SOURCE COLUMNS: {source_cols}
TARGET COLUMNS: {target_cols}
INSTRUCTION: {instruction or 'Create one-to-one mapping from source to target'}

Generate mappings in this EXACT JSON format (no additional text):
{{"mappings": [{{"target": "target_column_name", "source": "source_column_name", "cast": "target_data_type"}}], "unresolved": []}}

Rules:
1. Map each target column to the best matching source column
2. Use exact column names from the lists above
3. For one-to-one mapping, map columns with similar names
4. Include data type casting when needed
5. Return valid JSON only"""
                
                try:
                    # Use appropriate model based on provider
                    default_model = "sonar" if ai_provider == "perplexity" else "gemini-2.0-flash-exp"
                    llm_response = query_llm(prompt, ai_provider, model or default_model)
                    logger.info(f"{ai_provider.capitalize()} AI response: {llm_response}")
                    
                    if llm_response:
                        # Clean response to extract JSON
                        response_clean = llm_response.strip()
                        if response_clean.startswith('```json'):
                            response_clean = response_clean[7:]
                        if response_clean.endswith('```'):
                            response_clean = response_clean[:-3]
                        response_clean = response_clean.strip()
                        
                        parsed = json.loads(response_clean)
                        if parsed.get('mappings'):
                            result = parsed
                            logger.info(f"{ai_provider.capitalize()} AI mappings generated: {len(parsed.get('mappings', []))} mappings")
                        else:
                            logger.warning(f"{ai_provider.capitalize()} AI response has no mappings")
                    else:
                        logger.warning(f"No response from {ai_provider.capitalize()} AI")
                except json.JSONDecodeError as e:
                    logger.error(f"{ai_provider.capitalize()} AI JSON decode error: {str(e)}, response: {llm_response}")
                except Exception as e:
                    logger.error(f"{ai_provider.capitalize()} AI error: {str(e)}")
                    # Fallback to heuristic if AI fails

            if result is None:
                result = suggest_mappings(source, target, max_sources_per_target=max_sources_per_target)

            # If we also have NL directives, merge them (NL wins for overlapping targets)
            if nl_result:
                by_target = {m.get('target'): m for m in result.get('mappings', []) if m.get('target')}
                for m in nl_result.get('mappings', []):
                    tgt = m.get('target')
                    if tgt:
                        by_target[tgt] = m
                result['mappings'] = list(by_target.values())
                # Combine unresolved
                result['unresolved'] = (result.get('unresolved') or []) + (nl_result.get('unresolved') or [])

            # Optionally include attribute_mapper format for Load_into_database
            if payload.get('to_attribute_mapper'):
                target_types = { (t.get('name') or ''): (t.get('type') or '') for t in (target or []) }
                attribute_mapper = []
                for m in result.get('mappings', []):
                    tgt = m.get('target')
                    # Use transform expression if present; otherwise use source column
                    src_expr = m.get('transform') or m.get('source')
                    # dtype: prefer explicit cast; fallback to target declared type; default TEXT
                    dtype = (m.get('cast') or target_types.get(tgt) or 'TEXT')
                    attribute_mapper.append([tgt, "", src_expr, dtype])
                result['attribute_mapper'] = attribute_mapper

            # Include meta about which engine was used
            result['engine'] = 'llm' if use_llm and (llm_meta or is_ollama_available()) else 'heuristic'
            if llm_meta:
                result['llm_meta'] = llm_meta

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'failed to suggest mappings: {e}'}, status=status.HTTP_400_BAD_REQUEST)

class FlowOperation(APIView):  
    @csrf_exempt
    @transaction.atomic()
    def get(self,request,id):
        tok1 = token_function(request)
        if tok1["status"]==200:
            user_id = tok1['user_id']
            if flow_model.FlowBoard.objects.filter(id=id,user_id=user_id).exists():
                data = flow_model.FlowBoard.objects.get(id = id,user_id=user_id)
                dag_id = data.Flow_id
                configs_dir = f'{settings.config_dir}/FlowBoard/{str(user_id)}'
                file_path = os.path.join(configs_dir, f'{dag_id}.json')
                # Ensure flow plan JSON exists; if not, instruct client to save the flow again
                if not os.path.exists(file_path):
                    return Response({
                        'message': 'Flow definition missing. Please open and save the flow again to regenerate the config JSON.',
                        'expected_path': file_path,
                        'flow_id': dag_id
                    }, status=status.HTTP_404_NOT_FOUND)

                with open(file_path, 'r') as f:
                    dag_json = json.load(f)

                # Resolve DrawFlow which can be stored as:
                # - a full URL to the JSON
                # - a raw JSON string (legacy or fallback "{}")
                # - an S3 key/path without scheme
                transformations_flow = {}
                try:
                    draw_ref = (data.DrawFlow or '').strip()
                    if not draw_ref or draw_ref == '{}':
                        # Nothing stored; return empty structure
                        transformations_flow = {}
                    elif draw_ref.startswith('{') and draw_ref.endswith('}'):
                        # Inline JSON stored in DB
                        transformations_flow = json.loads(draw_ref)
                    elif draw_ref.startswith('http://') or draw_ref.startswith('https://'):
                        # Remote URL
                        resp = requests.get(draw_ref, timeout=10)
                        resp.raise_for_status()
                        transformations_flow = resp.json() if resp.content else {}
                    else:
                        # Assume S3 key/path. Try to derive key and fetch from S3
                        # Examples: '.../FlowBoard/<user>/<id>.json' or 'FlowBoard/<user>/<id>.json'
                        try:
                            if 'FlowBoard/' in draw_ref:
                                s3_key = f"Datamplify/FlowBoard/{draw_ref.split('FlowBoard/')[1]}"
                            else:
                                # If already relative under Datamplify
                                s3_key = draw_ref.lstrip('/')
                            obj = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_key)
                            body = obj['Body'].read()
                            transformations_flow = json.loads(body.decode('utf-8')) if body else {}
                        except Exception:
                            transformations_flow = {}
                except Exception:
                    transformations_flow = {}

                return Response({
                        'message': 'success',
                        'id':id,
                        'Flow_id': dag_id,
                        'flow_plan':dag_json,
                        'drawflow':transformations_flow,
                        'flow_name':data.Flow_name
                    }, status=status.HTTP_200_OK)
                
            else:
                return Response({'message':'Flow Plan Not Found'},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)
        
    
        
    def delete(self,request,id):
        tok1 = token_function(request)
        if tok1["status"]==200:
            user_id = tok1['user_id']
            if flow_model.FlowBoard.objects.filter(id = id,user_id = user_id).exists():
                flow_data = flow_model.FlowBoard.objects.get(id = id,user_id = user_id)
                air_token = airflow_token()
                url =f"{settings.airflow_host}/api/v2/dags/{flow_data.Flow_id}"
                headers = {
                    "Authorization": f"Bearer {air_token}"
                }
                response = requests.delete(url, headers=headers)
                configs_dir = f'{settings.config_dir}/FlowBoard/{str(user_id)}'
                file_path = os.path.join(configs_dir, f'{flow_data.Flow_id}.json')
                if os.path.exists(file_path):
                    os.remove(file_path)
                datasrc_key = flow_data.DrawFlow.split('FlowBoard/')[1]
                s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=f'Datamplify/FlowBoard/{str(datasrc_key)}')               
                flow_model.FlowBoard.objects.filter(id = id,user_id=user_id).delete()
                return Response({'message':'Deleted Successfully'},status=status.HTTP_200_OK)
            else:
                return Response({'message':'Data Flow Not Created'},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)
            




class FlowRun(APIView):
    @csrf_exempt
    @transaction.atomic()
    def post(self, request, id):
        """
        Ensure the FlowBoard JSON exists on disk (create/update from payload if provided)
        and trigger the DAG via Monitor endpoint.
        """
        tok1 = token_function(request)
        if tok1["status"] != 200:
            return Response({'message': tok1['message']}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = tok1['user_id']
        # Validate ownership and get DAG id
        if not flow_model.FlowBoard.objects.filter(id=id, user_id=user_id).exists():
            return Response({'message': 'Flow not found'}, status=status.HTTP_404_NOT_FOUND)

        data = flow_model.FlowBoard.objects.get(id=id, user_id=user_id)
        dag_id = data.Flow_id
        user = auth_models.UserProfile.objects.get(id=user_id)

        # Ensure config JSON exists where Airflow reads it
        configs_dir = os.path.join(settings.config_dir, 'FlowBoard', str(user_id))
        file_path = os.path.join(configs_dir, f'{dag_id}.json')
        os.makedirs(configs_dir, exist_ok=True)

        # If a flow_plan payload is provided, write/overwrite the JSON so Airflow can parse the latest graph
        incoming_plan = request.data.get('flow_plan') if isinstance(request.data, dict) else None
        if incoming_plan:
            try:
                # Normalize minimal required keys
                incoming_plan['dag_id'] = dag_id
                incoming_plan['flow_name'] = data.Flow_name
                incoming_plan['user_id'] = str(user_id)
                incoming_plan['username'] = user.username
                with open(file_path, 'w') as f:
                    json.dump(incoming_plan, f, indent=4, cls=UUIDEncoder)
            except Exception as e:
                return Response({'message': f'Failed to write flow plan: {e}'}, status=status.HTTP_400_BAD_REQUEST)

        # If still missing and no payload provided, return helpful error
        if not os.path.exists(file_path):
            return Response({
                'message': 'Flow definition missing. Provide flow_plan in request or save the flow before running.',
                'expected_path': file_path
            }, status=status.HTTP_404_NOT_FOUND)

        # Preflight: wait briefly until Airflow registers the DAG (poll API)
        try:
            dag_check_url = f"{settings.airflow_host}/api/v1/dags/{dag_id}"
            auth = (settings.airflow_username, settings.airflow_password)
            max_wait = 60
            end = time.time() + max_wait
            while time.time() <= end:
                try:
                    r = requests.get(dag_check_url, auth=auth, timeout=5)
                    if r.status_code == 200:
                        break
                except Exception:
                    pass
                time.sleep(2)
        except Exception:
            # Non-fatal; we still attempt trigger with retry below
            pass

        # Build internal URL to existing Monitor trigger endpoint
        scheme = 'https' if request.is_secure() else 'http'
        base = f"{scheme}://{request.get_host()}"
        # Important: APPEND_SLASH=False, route is defined without trailing slash
        trigger_url = f"{base}/v1/monitor/Trigger/{dag_id}?type=flowboard"

        try:
            # Forward auth header if present (optional)
            headers = {}
            if 'Authorization' in request.headers:
                headers['Authorization'] = request.headers.get('Authorization')

            # Retry trigger for a short window to allow Airflow to register the DAG
            max_wait_seconds = 120
            interval = 3
            deadline = time.time() + max_wait_seconds
            last_body = {'message': 'No response'}
            last_status = 502

            while time.time() <= deadline:
                resp = requests.post(trigger_url, headers=headers, timeout=10)
                try:
                    body = resp.json()
                except Exception:
                    body = {'message': resp.text}

                # Success or non-404 -> return immediately
                if resp.status_code != 404:
                    return Response(body, status=resp.status_code)

                # If 404 DAG not found, wait and retry
                last_body = body
                last_status = resp.status_code
                time.sleep(interval)

            # If we exhausted retries, return the last 404 body
            return Response(last_body, status=last_status)
        except requests.RequestException as e:
            return Response({'message': f'Trigger request failed: {e}'}, status=status.HTTP_502_BAD_GATEWAY)


class Flow_List(APIView):
    @csrf_exempt
    @transaction.atomic()
    def get(self,request):
        tok1 = token_function(request)  
        if tok1["status"] ==200:
            from math import ceil
            paginator = CustomPaginator()
            page_number = request.query_params.get(paginator.page_query_param, 1)
            page_size = request.query_params.get(paginator.page_size_query_param, paginator.page_size)
            search = request.query_params.get('search','')
            try:
                page_number = int(page_number)
                page_size = min(int(page_size), paginator.max_page_size)
            except (ValueError, TypeError):
                return Response({"error": "Invalid pagination parameters"}, status=400)
            total_records = flow_model.FlowBoard.objects.filter(
                user_id=tok1['user_id'],
                Flow_name__icontains=search
            ).count()

            total_pages = ceil(total_records / page_size)
            offset = (page_number - 1) * page_size
            limit = page_size
            # Get the paginated queryset
            queryset = flow_model.FlowBoard.objects.filter(
                user_id=tok1['user_id'],
                Flow_name__icontains=search
            ).order_by('-created_at')[offset:offset + limit]
            
            # Determine which flowboards have schedulers in bulk
            flow_ids = [str(f.id) for f in queryset]
            sched_flow_ids = set(
                str(x) for x in Scheduler.objects.filter(flowboard_id__in=flow_ids).values_list('flowboard_id', flat=True)
            )

            # Build response data with scheduling information
            data = []
            for flow in queryset:
                data.append({
                    'id': str(flow.id),
                    'Flow_id': flow.Flow_id,
                    'Flow_name': flow.Flow_name,
                    'DrawFlow': flow.DrawFlow,
                    'user_id': str(flow.user_id.id) if getattr(flow, 'user_id', None) else None,
                    'parsed': flow.parsed,
                    'has_scheduler': str(flow.id) in sched_flow_ids
                })
            
            return Response({
                'data': data,
                'total_pages': total_pages,
                'total_records': total_records,
                'page_number': page_number,
                'page_size': page_size
            }, status=status.HTTP_200_OK)
            # pag = pagination(request,trans_list,request.GET.get('page',1),request.GET.get('page_count',10))

        else:
           return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)
    
    def _auto_trigger_dag(self, dag_id, request):
        """
        Automatically trigger DAG creation and execution after FlowBoard save/update.
        
        Args:
            dag_id (str): The FlowBoard ID to use as DAG ID
            request: The original HTTP request for auth forwarding
            
        Returns:
            dict: Result with success status and message
        """
        try:
            # Wait briefly for Airflow to pick up the new config file
            time.sleep(2)
            
            # Build internal URL to Monitor trigger endpoint
            scheme = 'https' if request.is_secure() else 'http'
            base = f"{scheme}://{request.get_host()}"
            trigger_url = f"{base}/v1/monitor/Trigger/{dag_id}?type=flowboard"
            
            # Forward auth header if present
            headers = {}
            if 'Authorization' in request.headers:
                headers['Authorization'] = request.headers.get('Authorization')
            
            # Retry trigger with timeout for DAG registration
            max_wait_seconds = 30
            interval = 2
            deadline = time.time() + max_wait_seconds
            
            while time.time() <= deadline:
                try:
                    resp = requests.post(trigger_url, headers=headers, timeout=10)
                    
                    if resp.status_code in [200, 201]:
                        return {
                            'success': True,
                            'message': f'DAG {dag_id} triggered successfully',
                            'response': resp.json() if resp.content else {}
                        }
                    elif resp.status_code == 404:
                        # DAG not found yet, wait and retry
                        logger.info(f"DAG {dag_id} not found yet, retrying...")
                        time.sleep(interval)
                        continue
                    else:
                        return {
                            'success': False,
                            'message': f'Trigger failed with status {resp.status_code}: {resp.text}'
                        }
                        
                except requests.RequestException as e:
                    logger.warning(f"Trigger request failed for {dag_id}: {e}")
                    time.sleep(interval)
                    continue
            
            return {
                'success': False,
                'message': f'DAG {dag_id} trigger timed out after {max_wait_seconds}s'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Auto-trigger error: {str(e)}'
            }