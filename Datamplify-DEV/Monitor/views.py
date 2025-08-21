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
            if response.status_code == 201:
                data = response.json()
                return JsonResponse({'token': data.get('access_token')}, status=200)
            else:
                return JsonResponse({'error': 'Unauthorized'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)     
   
         

class Trigger_dag(APIView):
    @csrf_exempt
    @transaction.atomic()
    def post(self,request,id):
        tok1 = token_function(request)  
        if tok1["status"]==200:
            type = request.query_params.get('type','flowboard')
            if type.lower() =='flowboard':
                model_data = FlowBoard.objects.get(Flow_id = id)
                name = model_data.Flow_name
            else:
                model_data = TaskPlan.objects.get(Task_id=id)
                name=model_data.Task_name
            print(model_data)
            air_token = airflow_token()
            url =f"{settings.airflow_host}/api/v2/dags/{id}/dagRuns"
            headers = {
                "Authorization": f"Bearer {air_token}"
            }
            now = datetime.now(timezone.utc)
            iso_time = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            payload ={
                "conf":{},
                "logical_date": f"{iso_time}",

                }
            response = requests.post(url, headers=headers,json=payload)
            if response.status_code == 200:
                data = response.json()
                resp = {
                    "run_id":data.get("dag_run_id"),
                    "dag_id":data.get("dag_id"),
                }
                RunHistory.objects.create(
                    run_id = data.get("dag_run_id"),
                    source_type = type.lower(),
                    source_id = id,
                    name = name,
                    status = 'running',
                    started_at = now,
                    finished_at = None        
                )
                return Response(resp,status=status.HTTP_200_OK)
            elif response.status_code ==404:
                return Response({'message':response.json()},status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'message':response.json()},status=status.HTTP_400_BAD_REQUEST)
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
                headers = {
                    "Authorization": f"Bearer {air_token}"
                }
                response = requests.get(url, headers=headers)
                if response.status_code ==200:
                    data = response.json()
                    response_data = {
                        "tasks": [ {"task": task['task_id'], "state": task['state']} for task in data['task_instances'] ]
                    }
                    url =f"{settings.airflow_host}/api/v2/dags/{dag_id}/dagRuns/{run_id}"
                    headers = {
                        "Authorization": f"Bearer {air_token}"
                    }
                    response = requests.get(url, headers=headers)
                    if response.status_code ==200:
                        data = response.json()
                        final_status = data.get('state')
                        response_data['status'] = final_status
                        RunHistory.objects.filter(run_id=run_id,source_id = dag_id).update(status = final_status.lower(),finished_at = datetime.now(timezone.utc))
                        return Response(response_data,status=status.HTTP_200_OK)
                    else:
                        return Response( response.json(),status=status.HTTP_400_BAD_REQUEST) 
                else:
                    return Response( response.json(),status=status.HTTP_400_BAD_REQUEST) 
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
                    return Response(response.json(),status=status.HTTP_200_OK)
                else:
                    return Response(response.json(),status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message':'Serializer Error'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)
 







################################# Dashboard Page ###################################

class DashboardStatsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        period_days = int(request.query_params.get("period", 7))
        type = request.query_params.get('type',None)
        today = datetime.now(timezone.utc)
        current_start = today - timedelta(days=period_days)
        previous_start = today - timedelta(days=2 * period_days)

        # --- Totals (static) ---
        total_flowboard = FlowBoard.objects.count()
        total_taskplan = TaskPlan.objects.count()
        # --- Runs (current & previous) ---
        current_runs = RunHistory.objects.filter(started_at__gte=current_start)
        previous_runs = RunHistory.objects.filter(
            started_at__gte=previous_start,
            started_at__lt=current_start
        )

        # Current counts
        total_runs = current_runs.count()
        success_count = current_runs.filter(status="success").count()
        failure_count = current_runs.filter(status="failure").count()
        running_count = current_runs.filter(status="running").count()

        #taskplan
        taskplan_success_count = current_runs.filter(status="success",source_type = 'taskplan').count()
        taskplan_failure_count = current_runs.filter(status="failure",source_type='taskplan').count()
        taskplan_running_count = current_runs.filter(status="running",source_type = 'taskplan').count()

        taskplan_data = [
            {'name':'sucess','value':taskplan_success_count},
            {'name':'failure','value':taskplan_failure_count},
            {'name':'running','value':taskplan_running_count}
        ]

        #flowboard
        flowboard_success_count = current_runs.filter(status="success",source_type = 'flowboard').count()
        flowboard_failure_count = current_runs.filter(status="failure",source_type = 'flowboard').count()
        flowboard_running_count = current_runs.filter(status="running",source_type = 'flowboard').count()

        flowboard_data = [
            {'name':'sucess','value':flowboard_success_count},
            {'name':'failure','value':flowboard_failure_count},
            {'name':'running','value':flowboard_running_count}
        ]

        # TaskBoard rates
        # task_success_rate = (taskplan_success_count / total_runs * 100) if total_runs else 0
        # task_failure_rate = (taskplan_failure_count / total_runs * 100) if total_runs else 0
        # task_running_rate = (taskplan_running_count / total_runs * 100) if total_runs else 0

        # Flowboard rates
        # flow_success_rate = (flowboard_success_count / total_runs * 100) if total_runs else 0
        # flow_failure_rate = (flowboard_failure_count / total_runs * 100) if total_runs else 0
        # flow_running_rate = (flowboard_running_count / total_runs * 100) if total_runs else 0

        # Rates
        success_rate = (success_count / total_runs * 100) if total_runs else 0
        failure_rate = (failure_count / total_runs * 100) if total_runs else 0
        running_rate = (running_count / total_runs * 100) if total_runs else 0

        # Previous period counts
        prev_total = previous_runs.count()
        prev_success = previous_runs.filter(status="success").count()
        prev_failure = previous_runs.filter(status="failure").count()
        prev_running = previous_runs.filter(status="running").count()

        # --- Trend Calculation ---
        def calc_trend(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return round(((current - previous) / previous) * 100, 1)

        trends = {
            "success": calc_trend(success_count, prev_success),
            "failure": calc_trend(failure_count, prev_failure),
            "running": calc_trend(running_count, prev_running),
            "total_runs": calc_trend(total_runs, prev_total),
        }

        top_flowboards = (
            RunHistory.objects
            .filter(source_type="flowboard")
            .values("source_id", "name")
            .annotate(total_runs=Count("id"))
            .order_by("-total_runs")[:5]
        )

        # Top 5 TaskPlan runs
        top_taskplans = (
            RunHistory.objects
            .filter(source_type="taskplan")
            .values("source_id", "name")
            .annotate(total_runs=Count("id"))
            .order_by("-total_runs")[:5]
        )

        # --- Status Distribution ---
        status_distribution = {
            'taskplan':taskplan_data,
            'flowboard':flowboard_data
        }
        activity_list = ['recent','sucess','failed','running']
        # --- Recent Activity (last 10 runs) ---
        activity = {}

        for type in activity_list:
            if type ==None or type.lower() =='recent':
                recent_runs = current_runs.order_by("-started_at")[:10]
            else:
                recent_runs = current_runs.filter(status=type).order_by("-started_at")[:10]
            activity_list=[]
            for run in recent_runs:
                if run.source_type.lower() == "flowboard":
                    source = FlowBoard.objects.filter(Flow_id=run.source_id).first()
                    name = source.Flow_name if source else "Unknown Flow"
                else:
                    source = TaskPlan.objects.filter(Task_id=run.source_id).first()
                    name = source.Task_name if source else "Unknown Task"

                activity_list.append({
                    "name": name,
                    "type": run.source_type,
                    "status": run.status,
                    "started_at": time_ago(run.started_at),
                })
            activity[type] = activity_list


        # --- Final Response ---
        data = {
            "kpis": {
                "success_rate": round(success_rate, 1),
                "failure_rate": round(failure_rate, 1),
                "running_rate": round(running_rate, 1),
                "total_flowboard": total_flowboard,
                "total_taskplan": total_taskplan,
                "total_runs": total_runs,
            },
            "bar":{
                "flowboard":top_flowboards,
                "taskplan":top_taskplans
            },
            "status_distribution": status_distribution,
            "trends": trends,  # ⬅️ Added here
            "recent_activity": activity,
        }
        return Response(data)