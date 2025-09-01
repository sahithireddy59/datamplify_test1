from django.shortcuts import render
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from authentication.utils import token_function
from Monitor.utils import airflow_token
from Datamplify import settings
# Create your views here.
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from pytz import utc
import requests
import os, json
from datetime import timezone,datetime
from Monitor.serializers import flow_status,task_status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.timezone import now, timedelta
from FlowBoard.models import FlowBoard
from TaskPlan.models import TaskPlan
from .models import RunHistory
from django.db.models import Count
from .utils import  time_ago
import logging
logger = logging.getLogger(__name__)

def _safe_json(response):
    try:
        return response.json()
    except Exception:
        txt = (response.text or '').strip()
        return {"detail": txt if txt else f"HTTP {response.status_code}"}


@csrf_exempt
def airflow_token_api(request):
    if request.method == 'GET':
        login_url = settings.airflow_url
        payload = {
            "username": settings.airflow_username,
            "password": settings.airflow_password
        }
        try:
            response = requests.post(
                login_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code in (200, 201):
                data = response.json()
                return JsonResponse({'token': data.get('access_token')}, status=200)
            else:
                # Return body to help diagnose (e.g., 401)
                try:
                    body = response.json()
                except Exception:
                    body = (response.text or '').strip()
                return JsonResponse({'error': 'Unauthorized', 'detail': body, 'status_code': response.status_code}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



class Trigger_dag(APIView):
    def create_simple_dag(self, dag_id, user_id, user_name, config):
        """Create a simple DAG when Airflow is not available in Django process"""
        try:
            # Import DAG directly
            from airflow.models.dag import DAG
            from airflow.operators.dummy import DummyOperator
            from airflow.utils.dates import days_ago
            
            # Create a simple DAG
            dag = DAG(
                dag_id=dag_id,
                default_args={
                    'owner': user_name,
                    'depends_on_past': False,
                    'start_date': days_ago(1),
                },
                schedule_interval=None,
                catchup=False,
                tags=['manual', user_id]
            )
            
            # Add a simple task
            DummyOperator(
                task_id='run_task',
                dag=dag,
            )
            
            logger.info(f"Created simple DAG: {dag_id}")
            return dag
        except Exception as e:
            logger.error(f"Error creating simple DAG: {str(e)}")
            raise
    
    @csrf_exempt
    @transaction.atomic()
    def get(self, request, id=None):
        """List available DAGs in Airflow. 'id' is optional to support routes like /Trigger/<id>."""
        try:
            available_dags = self.list_available_dags()
            return Response({
                "available_dags": available_dags,
                "count": len(available_dags)
            })
        except Exception as e:
            return Response({
                "error": f"Failed to list DAGs: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @csrf_exempt
    @transaction.atomic()
    def dag_exists(self, dag_id):
        """Check if a DAG exists in Airflow"""
        try:
            air_token = airflow_token()
            url_v2 = f"{settings.airflow_host}/api/v2/dags/{dag_id}"
            url_v1 = f"{settings.airflow_host}/api/v1/dags/{dag_id}"
            headers_base = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            logger.info(f"Checking if DAG {dag_id} exists at {url_v2}")
            response = None
            if air_token:
                headers_bearer = {**headers_base, "Authorization": f"Bearer {air_token}"}
                response = requests.get(url_v2, headers=headers_bearer)
                if response.status_code == 401:
                    # fallback to basic
                    response = requests.get(url_v2, headers=headers_base, auth=(settings.airflow_username, settings.airflow_password))
            else:
                # no token available, use basic
                response = requests.get(url_v2, headers=headers_base, auth=(settings.airflow_username, settings.airflow_password))

            logger.info(f"DAG {dag_id} exists check returned status: {response.status_code}")
            if response.status_code == 404:
                # Try v1 endpoint
                logger.info(f"v2 404; retrying DAG exists on {url_v1}")
                if air_token:
                    headers_bearer = {**headers_base, "Authorization": f"Bearer {air_token}"}
                    response = requests.get(url_v1, headers=headers_bearer)
                    if response.status_code == 401:
                        response = requests.get(url_v1, headers=headers_base, auth=(settings.airflow_username, settings.airflow_password))
                else:
                    response = requests.get(url_v1, headers=headers_base, auth=(settings.airflow_username, settings.airflow_password))
                logger.info(f"DAG {dag_id} exists (v1) check returned status: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error checking if DAG {dag_id} exists: {str(e)}")
            return False

    def list_available_dags(self):
        """List available DAGs in Airflow"""
        try:
            air_token = airflow_token()
            url_v2 = f"{settings.airflow_host}/api/v2/dags"
            url_v1 = f"{settings.airflow_host}/api/v1/dags"
            headers = {
                "Authorization": f"Bearer {air_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            response = requests.get(url_v2, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return [dag["dag_id"] for dag in data.get("dags", [])]
            elif response.status_code == 404:
                # Fallback to v1 (and handle auth absence)
                if not air_token:
                    response = requests.get(url_v1, headers={"Content-Type": "application/json", "Accept": "application/json"}, auth=(settings.airflow_username, settings.airflow_password))
                else:
                    response = requests.get(url_v1, headers=headers)
                    if response.status_code == 401:
                        response = requests.get(url_v1, headers={"Content-Type": "application/json", "Accept": "application/json"}, auth=(settings.airflow_username, settings.airflow_password))
                if response.status_code == 200:
                    data = response.json()
                    return [dag["dag_id"] for dag in data.get("dags", [])]
            else:
                logger.error(f"Failed to list DAGs: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error listing DAGs: {str(e)}")
            return []

    @csrf_exempt
    @transaction.atomic()
    def post(self,request,id):
        tok1 = token_function(request)
        if tok1["status"]==200:
            type = request.query_params.get('type','flowboard')
            if type.lower() =='flowboard':
                model_data = FlowBoard.objects.get(Flow_id = id)
                name = model_data.Flow_name
                logger.info(f"FlowBoard details: ID={id}, Name={name}, UUID={model_data.id}, DrawFlow={model_data.DrawFlow}")

                # Build candidate DAG IDs dynamically
                candidates = []

                # 1) Prefer IDs specified inside the saved JSON config (dag_id, dag_ids, dag_name)
                try:
                    user_folder = str(getattr(model_data, 'user_id_id', None) or getattr(model_data.user_id, 'id', ''))
                    cfg_path = None
                    # Primary expected path by user folder
                    if user_folder:
                        expected = os.path.join(settings.config_dir, 'FlowBoard', user_folder, f'{id}.json')
                        if os.path.exists(expected):
                            cfg_path = expected
                        else:
                            logger.info(f"No config at expected path: {expected}; will scan all FlowBoard subfolders for {id}.json")
                    # Fallback: scan all subfolders for <id>.json
                    if not cfg_path:
                        root_dir = os.path.join(settings.config_dir, 'FlowBoard')
                        for root, dirs, files in os.walk(root_dir):
                            if f"{id}.json" in files:
                                cfg_path = os.path.join(root, f"{id}.json")
                                discovered_user_folder = os.path.basename(os.path.dirname(cfg_path))
                                logger.info(f"Discovered config for {id} under user folder: {discovered_user_folder} at {cfg_path}")
                                break
                    if cfg_path and os.path.exists(cfg_path):
                        with open(cfg_path, 'r') as f:
                            cfg = json.load(f)
                        if isinstance(cfg, dict):
                            cfg_candidates = []
                            if cfg.get('dag_id'):
                                cfg_candidates.append(str(cfg['dag_id']))
                            if isinstance(cfg.get('dag_ids'), list):
                                cfg_candidates.extend([str(x) for x in cfg['dag_ids'] if x])
                            if cfg.get('dag_name'):
                                cfg_candidates.append(str(cfg['dag_name']))
                            if cfg_candidates:
                                logger.info(f"Config-derived DAG IDs for {id}: {cfg_candidates}")
                                candidates.extend(cfg_candidates)
                    else:
                        logger.info(f"No config file found when building candidates for {id}; scanned FlowBoard directory.")
                except Exception as e:
                    logger.warning(f"Failed to read config for FlowBoard {id} for DAG candidates: {e}")

                # 2) Next, consider any mapping from settings
                mapping_value = getattr(settings, 'FLOWBOARD_TO_DAG_MAPPING', {}).get(id) if hasattr(settings, 'FLOWBOARD_TO_DAG_MAPPING') else None
                if mapping_value:
                    if isinstance(mapping_value, list):
                        candidates.extend(mapping_value)
                    else:
                        candidates.append(mapping_value)

                # 3) Lastly, consider the FlowBoard ID itself
                candidates.append(id)

                # Deduplicate preserving order
                seen = set()
                candidates = [x for x in candidates if not (x in seen or seen.add(x))]
                logger.info(f"Candidate DAG IDs for {id}: {candidates}")

                # Probe Airflow for a valid DAG ID
                dag_id = None
                logger.info(f"Probing Airflow for valid DAG ID among candidates: {candidates}")
                for cand in candidates:
                    logger.info(f"Trying DAG ID: {cand} for FlowBoard ID: {id}")
                    try:
                        exists = self.dag_exists(cand)
                        logger.info(f"DAG {cand} exists in Airflow: {exists}")
                        if exists:
                            dag_id = cand
                            logger.info(f"Found valid DAG ID: {dag_id} for FlowBoard ID: {id}")
                            break
                    except Exception as e:
                        logger.error(f"Error checking if DAG {cand} exists: {str(e)}")

                # Also check if the DAG exists in the globals
                if not dag_id:
                    logger.info(f"Checking if any candidate DAGs exist in globals: {candidates}")
                    for cand in candidates:
                        in_globals = cand in globals()
                        logger.info(f"Candidate {cand} in globals: {in_globals}")
                        if in_globals:
                            dag_obj = globals()[cand]
                            has_dag_id = hasattr(dag_obj, 'dag_id')
                            logger.info(f"Candidate {cand} has dag_id attribute: {has_dag_id}")
                            if has_dag_id:
                                dag_id = cand
                                logger.info(f"Found valid DAG ID in globals: {dag_id} for FlowBoard ID: {id}")
                                break

                # If no DAG was found, wait briefly for Airflow to register it from the config JSON
                if not dag_id:
                    logger.info(f"No DAG found for FlowBoard ID: {id}. Will wait for scheduler to register configs.")
                    # Ensure config exists so scheduler can pick it up
                    try:
                        user_folder = str(getattr(model_data, 'user_id_id', None) or getattr(model_data.user_id, 'id', ''))
                        cfg_path = None
                        if user_folder:
                            expected = os.path.join(settings.config_dir, 'FlowBoard', user_folder, f'{id}.json')
                            if os.path.exists(expected):
                                cfg_path = expected
                        if not cfg_path:
                            root_dir = os.path.join(settings.config_dir, 'FlowBoard')
                            for root, dirs, files in os.walk(root_dir):
                                if f"{id}.json" in files:
                                    cfg_path = os.path.join(root, f"{id}.json")
                                    break
                        if cfg_path and os.path.exists(cfg_path):
                            logger.info(f"Confirmed config exists at: {cfg_path}")
                        else:
                            logger.warning(f"Config not found under FlowBoard directory for id {id}")
                    except Exception as e:
                        logger.warning(f"While confirming config path for {id}: {e}")

                    # Poll Airflow for up to ~45 seconds
                    import time as _time
                    start_time = datetime.now(timezone.utc)
                    deadline = start_time + timedelta(seconds=45)
                    current_time = start_time
                    while current_time < deadline and not dag_id:
                        for cand in candidates:
                            try:
                                exists = self.dag_exists(cand)
                                logger.info(f"Retry probe: DAG {cand} exists: {exists}")
                                if exists:
                                    dag_id = cand
                                    break
                            except Exception as e:
                                logger.warning(f"Retry probe error for {cand}: {e}")
                        if not dag_id:
                            _time.sleep(2)
                            current_time = datetime.now(timezone.utc)
                    if dag_id:
                        logger.info(f"DAG registered after wait: {dag_id}")

                if not dag_id:
                    available_dags = self.list_available_dags()
                    return Response({
                        "error": f"No valid DAG ID found for FlowBoard ID: {id}",
                        "tried": candidates,
                        "available_dags": available_dags,
                        "suggestion": "Ensure the config JSON's dag_id/dag_ids match an Airflow DAG or adjust candidates logic."
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                model_data = TaskPlan.objects.get(Task_id=id)
                name=model_data.Task_name
                # For TaskPlan, use the ID directly as DAG ID
                dag_id = id

            print(model_data)
            air_token = airflow_token()
            # Log the DAG ID being used
            logger.info(f"Final DAG ID selected: {dag_id} for FlowBoard ID: {id}")
            # Prefer Airflow API v2, but fall back to v1 if not available
            url_v2 = f"{settings.airflow_host}/api/v2/dags/{dag_id}/dagRuns"
            url_v1 = f"{settings.airflow_host}/api/v1/dags/{dag_id}/dagRuns"
            headers_base = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            # Log the URLs being used
            logger.info(f"Attempting to trigger DAG {dag_id} at {url_v2}")
            logger.info(f"Airflow host: {settings.airflow_host}")
            logger.info(f"Airflow username: {settings.airflow_username}")
            now = datetime.now(timezone.utc)
            iso_time = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            # Airflow v2: logical_date allowed; Airflow v1: expects dag_run_id and conf only
            run_id = f"manual__{now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3].replace(':','-')}"
            payload_v2 = {
                "conf": {},
                "logical_date": iso_time,
                "dag_run_id": run_id
            }
            payload_v1 = {
                "dag_run_id": run_id,
                "conf": {}
            }
            used_url = url_v2
            auth_used = None
            # Try Bearer if available
            if air_token:
                headers_bearer = {**headers_base, "Authorization": f"Bearer {air_token}"}
                response = requests.post(url_v2, headers=headers_bearer, json=payload_v2)
                auth_used = "bearer"
            else:
                # No token; try Basic Auth directly
                response = requests.post(url_v2, headers=headers_base, auth=(settings.airflow_username, settings.airflow_password), json=payload_v2)
                auth_used = "basic"
            # If bearer failed with 401, retry with Basic on the same URL
            if response.status_code == 401 and auth_used == "bearer":
                response = requests.post(url_v2, headers=headers_base, auth=(settings.airflow_username, settings.airflow_password), json=payload_v2)
                auth_used = "basic"
            # Fallback to v1 if v2 not found
            if response.status_code == 404:
                used_url = url_v1
                if auth_used == "basic":
                    response = requests.post(url_v1, headers=headers_base, auth=(settings.airflow_username, settings.airflow_password), json=payload_v1)
                else:
                    # bearer first if token present
                    if air_token:
                        headers_bearer = {**headers_base, "Authorization": f"Bearer {air_token}"}
                        response = requests.post(url_v1, headers=headers_bearer, json=payload_v1)
                        if response.status_code == 401:
                            response = requests.post(url_v1, headers=headers_base, auth=(settings.airflow_username, settings.airflow_password), json=payload_v1)
                            auth_used = "basic"
                    else:
                        response = requests.post(url_v1, headers=headers_base, auth=(settings.airflow_username, settings.airflow_password), json=payload_v1)
                        auth_used = "basic"
            if response.status_code in (200, 201):
                data = response.json()
                logger.info(f"Received successful response from Airflow: {data}")
                resp = {
                    "run_id":data.get("dag_run_id"),
                    "dag_id":data.get("dag_id"),
                    "status": "success"
                }
                logger.info(f"Successfully triggered DAG {dag_id} with run_id {resp['run_id']}")
                RunHistory.objects.create(
                    run_id = data.get("dag_run_id"),
                    source_type = type.lower(),
                    source_id = dag_id,
                    name = name,
                    status = 'running',
                    started_at = now,
                    finished_at = None
                )
                return Response(resp,status=status.HTTP_200_OK)
            elif response.status_code == 404:
                logger.warning("Airflow trigger 404: url=%s auth=%s body=%s", used_url, auth_used, (response.text or '').strip())
                return Response({'message': _safe_json(response), 'status_code': response.status_code, 'url': used_url, 'auth': auth_used}, status=status.HTTP_404_NOT_FOUND)
            else:
                logger.warning("Airflow trigger non-2xx: status=%s url=%s auth=%s body=%s", response.status_code, used_url, auth_used, (response.text or '').strip())
                return Response({'message': _safe_json(response), 'status_code': response.status_code, 'url': used_url, 'auth': auth_used}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)



class DataFlow_status(APIView):
    serializer_class = flow_status

    @csrf_exempt
    @transaction.atomic()
    def post(self,request):
        tok1 = token_function(request)
        if tok1["status"]==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                dag_id = serializer.validated_data['dag_id']
                run_id = serializer.validated_data['run_id']
                air_token = airflow_token()
                url =f"{settings.airflow_host}/api/v2/dags/{dag_id}/dagRuns/{run_id}/taskInstances"
                headers_base = {"Content-Type": "application/json", "Accept": "application/json"}
                response = None
                if air_token:
                    headers_bearer = {**headers_base, "Authorization": f"Bearer {air_token}"}
                    response = requests.get(url, headers=headers_bearer)
                    if response.status_code == 401:
                        # Fallback to basic auth
                        response = requests.get(url, headers=headers_base, auth=(settings.airflow_username, settings.airflow_password))
                else:
                    # No token available; use basic auth directly
                    response = requests.get(url, headers=headers_base, auth=(settings.airflow_username, settings.airflow_password))
                if response.status_code ==200:
                    data = response.json()
                    response_data = {
                        "tasks": [ {"task": task['task_id'], "state": task['state']} for task in data['task_instances'] ]
                    }
                    url =f"{settings.airflow_host}/api/v2/dags/{dag_id}/dagRuns/{run_id}"
                    if air_token:
                        headers_bearer = {**headers_base, "Authorization": f"Bearer {air_token}"}
                        response = requests.get(url, headers=headers_bearer)
                        if response.status_code == 401:
                            response = requests.get(url, headers=headers_base, auth=(settings.airflow_username, settings.airflow_password))
                    else:
                        response = requests.get(url, headers=headers_base, auth=(settings.airflow_username, settings.airflow_password))
                    if response.status_code ==200:
                        data = response.json()
                        final_status = data.get('state')
                        response_data['status'] = final_status
                        RunHistory.objects.filter(run_id=run_id,source_id = dag_id).update(status = final_status.lower(),finished_at = datetime.now(timezone.utc))
                        return Response(response_data,status=status.HTTP_200_OK)
                    else:
                        return Response(_safe_json(response), status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(_safe_json(response), status=status.HTTP_400_BAD_REQUEST)
            else:
                 return Response({'message':'Serializer Error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)



class Dataflow_Task_status(APIView):
    serializer_class = task_status

    @csrf_exempt
    @transaction.atomic()
    def post(self,request):
        tok1 = token_function(request)
        if tok1["status"]==200:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                dag_id = serializer.validated_data['dag_id']
                run_id = serializer.validated_data['run_id']
                task_id = serializer.validated_data['task_id']
                air_token = airflow_token()
                logs_url = f"{settings.airflow_host}/api/v2/dags/{dag_id}/dagRuns/{run_id}/taskInstances/{task_id}/logs/1?map_index=-1"
                headers = {
                        "Authorization": f"Bearer {air_token}"
                }
                response = requests.get(logs_url, headers=headers)
                if response.status_code ==200:
                    return Response(response.json(), status=status.HTTP_200_OK)
                else:
                    return Response(_safe_json(response), status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message':'Serializer Error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)



################################# Dashboard Page ###################################

class ListDagsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        """List available DAGs in Airflow instance"""
        try:
            from .utils import list_airflow_dags
            result = list_airflow_dags()

            if "error" in result:
                return Response({"error": result["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"dags": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardStatsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        """Get dashboard statistics"""
        try:
            # Get basic stats
            from django.db.models import Count, Q
            
            # Get FlowBoard stats
            flowboard_count = FlowBoard.objects.count()
            
            # Get TaskPlan stats
            taskplan_count = TaskPlan.objects.count()
            
            # Get RunHistory stats
            total_runs = RunHistory.objects.count()
            successful_runs = RunHistory.objects.filter(status="success").count()
            failed_runs = RunHistory.objects.filter(status="failed").count()
            running_runs = RunHistory.objects.filter(status="running").count()
            
            # Get recent runs
            recent_runs = RunHistory.objects.order_by("-started_at")[:10]
            
            return Response({
                "flowboards": flowboard_count,
                "taskplans": taskplan_count,
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "failed_runs": failed_runs,
                "running_runs": running_runs,
                "recent_runs": [
                    {
                        "run_id": run.run_id,
                        "name": run.name,
                        "status": run.status,
                        "started_at": run.started_at.isoformat() if run.started_at else None,
                        "finished_at": run.finished_at.isoformat() if run.finished_at else None
                    } for run in recent_runs
                ]
            })
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
