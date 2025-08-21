from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction 
from TaskPlan.serializers import CreateTask,Update_TaskPlan
from authentication import models as auth_models
from TaskPlan import models as task_models
from Service.utils import generate_user_unique_code,file_save_1,UUIDEncoder,s3,CustomPaginator
from Monitor.utils import airflow_token
from authentication.utils import token_function
from Datamplify import settings
from drf_yasg.utils import swagger_auto_schema

from datetime import datetime 
from pytz import utc
import os,json,requests




class TaskPlan(APIView):
    serializer_class = CreateTask
    @swagger_auto_schema(request_body=CreateTask)
    @transaction.atomic()
    @csrf_exempt
    def post(self,request):
        tok1 = token_function(request)
        if tok1["status"]==200:
            user_id = tok1['user_id']
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                task_name = serializer.validated_data['task_name']
                task_plan = serializer.validated_data['task_plan']
                drawflow = serializer.validated_data['drawflow']
            
                user = auth_models.UserProfile.objects.get(id=user_id)
                if task_models.TaskPlan.objects.filter(Task_name__exact=task_name,user_id = user_id).exists():
                    return Response({'message':f'Task name already Exists'},status=status.HTTP_406_NOT_ACCEPTABLE)  
                Task_id = generate_user_unique_code(request,'TASK')
                task_plan['dag_id'] = Task_id
                task_plan['task_name'] = task_name
                task_plan['username'] = user.username
                task_plan['user_id'] = user_id

                configs_dir = os.path.join(settings.config_dir, 'TaskPlan', str(user_id))

                os.makedirs(configs_dir, exist_ok=True)
                file_path = os.path.join(configs_dir, f'{Task_id}.json')
                with open(file_path, 'w') as f:
                    json.dump(task_plan,f, indent=4,cls=UUIDEncoder)
                file_data = drawflow.read().decode('utf-8')  
                file_path = file_save_1(file_data,'',Task_id,'TaskPlan',"")
                id = task_models.TaskPlan.objects.create(
                    Task_name = task_name,
                    Task_id  = Task_id,
                    DrawFlow = file_path['file_url'],
                    user_id = user,
                )
                return Response({'message':'Saved SucessFully','Task_Plan_id':id.id},status=status.HTTP_200_OK)
            else:
                return Response({'message':'Serializer Error'},status=status.HTTP_400_BAD_REQUEST)
        else:
             return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)
        
    serializer_class1 = Update_TaskPlan
    @swagger_auto_schema(request_body=Update_TaskPlan)

    def put(self, request):
        tok1 = token_function(request)
        if tok1["status"]==200:
            user_id = tok1['user_id']
            serializer = self.serializer_class1(data = request.data)
            if serializer.is_valid(raise_exception=True):
                id = serializer.validated_data['id']
                task_name = serializer.validated_data['task_name']
                task = serializer.validated_data['task_plan']
                drawflow = serializer.validated_data['drawflow']
                user = auth_models.UserProfile.objects.get(id=user_id)
                if task_models.TaskPlan.objects.filter(Task_name__exact=task_name,user_id = user_id).exclude(id=id).exists():
                    return Response({'message':f'Task name already Exists'},status=status.HTTP_406_NOT_ACCEPTABLE)
                if task_models.TaskPlan.objects.filter(id = id,user_id = user_id).exists():
                    Task_data = task_models.TaskPlan.objects.get(id = id,user_id = user_id)
                else:
                     return Response({'message':'Data Flow Not Created'},status=status.HTTP_404_NOT_FOUND)
                     
                task['user_id'] = tok1['user_id']
                task['username'] = user.username
                task['dag_id'] = Task_data.Task_id
                task['task_name'] = task_name
                configs_dir = f'{settings.config_dir}/TaskPlan/{str(user_id)}'
                file_path = os.path.join(configs_dir, f'{Task_data.Task_id}.json')
                new_file_path = os.path.join(configs_dir, f'{Task_data.Task_id}.json')
                data = task
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4,cls=UUIDEncoder)
                os.rename(file_path,new_file_path)
                datasrc_key = Task_data.DrawFlow.split('TaskPlan/')[1]
                file_data = drawflow.read().decode('utf-8')  
                file_path = file_save_1(file_data,'',Task_data.Task_id,'TaskPlan',f'Datamplify/TaskPlan/{datasrc_key}')
                updated_data = task_models.TaskPlan.objects.filter(id = id).update(
                    Task_name  = task_name,
                    DrawFlow = file_path['file_url'],
                    updated_at=datetime.now(utc),
                    user_id = user
                )                
                return Response({'message':'updated SucessFully','Task_Plan_id':str(id)},status=status.HTTP_200_OK)
            else:
                 return Response({'message':'Serializer Error'},status=status.HTTP_400_BAD_REQUEST)
        else:
             return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)
class Taskoperations(APIView):
    @csrf_exempt
    @transaction.atomic()
    def get(self,request,id):
        tok1 = token_function(request)
        if tok1["status"]==200:
            user_id = tok1['user_id']
            if task_models.TaskPlan.objects.filter(id=id,user_id=user_id).exists():
                data = task_models.TaskPlan.objects.get(id = id,user_id=user_id)
                dag_id = data.Task_id
                configs_dir = f'{settings.config_dir}/TaskPlan/{str(user_id)}'
                file_path = os.path.join(configs_dir, f'{dag_id}.json')
                with open(file_path, 'r') as f:
                    dag_json = json.load(f)

                transformation = requests.get(data.DrawFlow)
                transformations_flow = transformation.json()

                return Response({
                        'message': 'success',
                        'id':id,
                        'Task_id': dag_id,
                        'task_plan':dag_json,
                        'drawflow':transformations_flow,
                        'task_name':data.Task_name
                    }, status=status.HTTP_200_OK)
                
            else:
                return Response({'message':'Task Not Found'},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)
        
    
        
    def delete(self,request,id):
        tok1 = token_function(request)
        if tok1["status"]==200:
            user_id = tok1['user_id']
            if task_models.TaskPlan.objects.filter(id = id,user_id = user_id).exists():
                flow_data = task_models.TaskPlan.objects.get(id = id,user_id = user_id)
                air_token = airflow_token()
                url =f"{settings.airflow_host}/api/v2/dags/{flow_data.Task_id}"
                headers = {
                    "Authorization": f"Bearer {air_token}"
                }
                response = requests.delete(url, headers=headers)
                configs_dir = f'{settings.config_dir}/TaskPlan/{str(user_id)}'
                file_path = os.path.join(configs_dir, f'{flow_data.Task_id}.json')
                if os.path.exists(file_path):
                    os.remove(file_path)
                datasrc_key = flow_data.DrawFlow.split('TaskPlan/')[1]
                s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=f'Datamplify/TaskPlan/{str(datasrc_key)}')               
                task_models.TaskPlan.objects.filter(id = id,user_id=user_id).delete()
                return Response({'message':'Deleted Successfully'},status=status.HTTP_200_OK)
            else:
                return Response({'message':'Task Plan Not Created'},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)



class Task_List(APIView):
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
            total_records = task_models.TaskPlan.objects.filter(
                user_id=tok1['user_id'],
                Task_name__icontains=search
            ).count()

            total_pages = ceil(total_records / page_size)
            offset = (page_number - 1) * page_size
            limit = page_size
            data = task_models.TaskPlan.objects.filter(user_id = tok1['user_id'],Task_name__icontains = search).values('id','Task_name','created_at','updated_at')[offset:offset + limit]
            return Response({'data':data,
                            'total_pages': total_pages,
                            "total_records":total_records,
                            'page_number': page_number,
                            'page_size': page_size},status=status.HTTP_200_OK)
            # pag = pagination(request,trans_list,request.GET.get('page',1),request.GET.get('page_count',10))

        else:
           return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)