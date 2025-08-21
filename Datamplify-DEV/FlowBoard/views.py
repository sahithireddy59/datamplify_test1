from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction 
from Service.utils import generate_user_unique_code,file_save_1,s3,UUIDEncoder,CustomPaginator
from FlowBoard.serializers import Create_FLow,Update_FlowBoard
from FlowBoard import models as flow_model
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
                id = flow_model.FlowBoard.objects.create(
                    Flow_id = Flow_id,
                    Flow_name=flow_name,
                    DrawFlow=file_path['file_url'],
                    user_id = user
                )
                return Response({'message':'Saved SucessFully','Flow_Board_id':id.id},status=status.HTTP_200_OK)
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
                configs_dir = f'{settings.config_dir}/FlowBoard/{str(user_id)}'
                file_path = os.path.join(configs_dir, f'{Flow_data.Flow_id}.json')
                new_file_path = os.path.join(configs_dir, f'{Flow_data.Flow_id}.json')
                data = flow
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4,cls=UUIDEncoder)
                os.rename(file_path,new_file_path)
                datasrc_key = Flow_data.DrawFlow.split('FlowBoard/')[1]
                file_data = drawflow.read().decode('utf-8')  
                file_path = file_save_1(file_data,'',Flow_data.Flow_id,'FlowBoard',f'Datamplify/FlowBoard/{datasrc_key}')
                updated_data = flow_model.FlowBoard.objects.filter(id = id).update(
                    Flow_name  = flow_name,
                    DrawFlow = file_path['file_url'],
                    updated_at=datetime.now(utc),
                    user_id = user
                )                
                return Response({'message':'updated SucessFully','Flow_Board_id':str(id)},status=status.HTTP_200_OK)
            else:
                    return Response({'message':'Serializer Error'},status=status.HTTP_400_BAD_REQUEST)
        else:
                return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)
        


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
                with open(file_path, 'r') as f:
                    dag_json = json.load(f)

                transformation = requests.get(data.DrawFlow)
                transformations_flow = transformation.json()

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
            data = flow_model.FlowBoard.objects.filter(user_id = tok1['user_id'],Flow_name__icontains = search).values('id','Flow_name','Flow_id','created_at','updated_at')[offset:offset + limit]
            return Response({'data':data,
                            'total_pages': total_pages,
                            "total_records":total_records,
                            'page_number': page_number,
                            'page_size': page_size},status=status.HTTP_200_OK)
            # pag = pagination(request,trans_list,request.GET.get('page',1),request.GET.get('page_count',10))

        else:
           return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)