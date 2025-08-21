from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from .serializers import ServerConnect,File_upload,server_Files
from Connections import models as conn_models
from authentication import models as auth_models
from rest_framework.response import Response
from rest_framework import status
from Service.utils import encode_value,file_files_save,CustomPaginator,s3
from Connections.utils import server_connection,get_table_details
from authentication.utils import token_function
import uuid,datetime,os
from pytz import utc
from drf_yasg.utils import swagger_auto_schema
from frictionless import Resource
from Datamplify import settings
from django.db.models import Q, Subquery
from sqlalchemy import text

created_at=datetime.datetime.now(utc)
updated_at=datetime.datetime.now(utc)


class Server_Connection(APIView):
    serializer_class = ServerConnect
    @swagger_auto_schema(request_body=ServerConnect)
    @transaction.atomic()
    @csrf_exempt
    def post(self,request):
        tok1 = token_function(request)
        if tok1["status"]==200:
            user_id =tok1['user_id']
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                db_type = serializer.validated_data['database_type']
                hostname = serializer.validated_data['hostname']
                port = serializer.validated_data['port']
                username = serializer.validated_data['username']
                password = serializer.validated_data['password']
                db_name = serializer.validated_data['database']
                connection_name = serializer.validated_data['connection_name']
                service_name = serializer.validated_data['service_name']
                server_path = serializer.validated_data['path']
                schema = serializer.validated_data['schema']
                if conn_models.DatabaseConnections.objects.filter(connection_name__iexact = connection_name, user_id=user_id).exists():
                    return Response({'message': ' Connection Name  Exists'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                try:
                    conn_type = conn_models.DataSources.objects.get(id=db_type, type__iexact='DATABASE')
                except conn_models.DataSources.DoesNotExist:
                    return Response({'message': ' Connection Not Implemented'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                encoded_passw=encode_value(password)
                server_conn=server_connection(username, encoded_passw, db_name, hostname,port,service_name,conn_type.name.upper(),server_path)
                User = auth_models.UserProfile.objects.get(id = user_id)
                if server_conn['status']==200:
                    connection =conn_models.DatabaseConnections.objects.create(
                        server_type = conn_type,
                        hostname = hostname,
                        username = username,
                        password = encoded_passw,
                        database = db_name,
                        database_path = server_path,
                        service_name = service_name,
                        port = port,
                        connection_name = connection_name,
                        is_connected = True,
                        user_id = User,
                        schema = schema,
                    )
                    conn_id =conn_models.Connections.objects.create(
                            table_id = connection.id,
                            type = conn_type,
                            user_id = User
                        )
                    return Response({'message':'Connection Successfull','id':conn_id.id},status=status.HTTP_200_OK)
                else:
                    return Response({'message':server_conn['message']},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message':"Invalid Values"},status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
             return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)
        

class Server_Connection_update(APIView):
    serializer_class = ServerConnect
    @swagger_auto_schema(request_body=ServerConnect)
    @transaction.atomic()
    @csrf_exempt
    def put(self,request,id):
        tok1 = token_function(request)
        if tok1["status"]==200:
            user_id =tok1['user_id']
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid(raise_exception=True):
                db_type = serializer.validated_data['database_type']
                hostname = serializer.validated_data['hostname']
                port = serializer.validated_data['port']
                username = serializer.validated_data['username']
                password = serializer.validated_data['password']
                db_name = serializer.validated_data['database']
                connection_name = serializer.validated_data['connection_name']
                service_name = serializer.validated_data['service_name']
                server_path = serializer.validated_data['path']
                schema = serializer.validated_data['schema']
                conn_data = conn_models.Connections.objects.get(id=id,user_id = user_id)
                if conn_models.DatabaseConnections.objects.filter(connection_name__iexact = connection_name, user_id=user_id).exclude(id=conn_data.table_id).exists():
                    return Response({'message': ' Connection Name  Exists'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                try:
                    conn_type = conn_models.DataSources.objects.get(id=db_type, type__iexact='DATABASE')
                except conn_models.DataSources.DoesNotExist:
                    return Response({'message': ' Connection Not Implemented'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                
                encoded_passw=encode_value(password)
                server_conn=server_connection(username, encoded_passw, db_name, hostname,port,service_name,conn_type.name.upper(),server_path)
                User = auth_models.UserProfile.objects.get(id = user_id)
                if server_conn['status']==200:
                    connection =conn_models.DatabaseConnections.objects.filter(id=conn_data.table_id).update(
                        server_type = conn_type,
                        hostname = hostname,
                        username = username,
                        password = encoded_passw,
                        database = db_name,
                        database_path = server_path,
                        service_name = service_name,
                        port = port,
                        connection_name = connection_name,
                        schema = schema,
                    )
                    return Response({'message':'Update Successfull','id':id},status=status.HTTP_200_OK)
                else:
                    return Response({'message':server_conn['message']},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message':"Invalid Values"},status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
             return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)
        
    @transaction.atomic()
    @csrf_exempt
    def get(self, request, id):
        tok1 = token_function(request)
        if tok1["status"] == 200:
            user_id = tok1['user_id']
            try:
                connection_data = conn_models.Connections.objects.get(id=id,user_id=user_id)
            except conn_models.Connections.DoesNotExist:
                return Response({'message': 'Connection not found'}, status=status.HTTP_404_NOT_FOUND)
            try:
                Database_data = conn_models.DatabaseConnections.objects.get(id=connection_data.table_id, user_id=user_id,is_connected = True)
            except conn_models.DatabaseConnections.DoesNotExist:
                return Response({'message': 'Connection not found'}, status=status.HTTP_404_NOT_FOUND)

            # Prepare response data
            connection_data = {
                'id': connection_data.id,
                'database_type': Database_data.server_type.id,
                'hostname': Database_data.hostname,
                'port': Database_data.port,
                'username': Database_data.username,
                'database': Database_data.database,
                'connection_name': Database_data.connection_name,
                'service_name': Database_data.service_name,
                'path': Database_data.database_path,
                'schema': Database_data.schema,
                'created_at': Database_data.created_at,
                'updated_at': Database_data.updated_at,
            }

            return Response(connection_data, status=status.HTTP_200_OK)
        else:
            return Response({'message': tok1['message']}, status=status.HTTP_401_UNAUTHORIZED)
        
    @transaction.atomic()
    @csrf_exempt
    def delete(self, request, id):
        tok1 = token_function(request)
        if tok1["status"] == 200:
            user_id = tok1['user_id']
            try:
                connection = conn_models.Connections.objects.get(id=id, user_id=user_id)
            except conn_models.Connections.DoesNotExist:
                return Response({'message': 'Connection not found '}, status=status.HTTP_404_NOT_FOUND)

            try:
                db_conn = conn_models.DatabaseConnections.objects.get(id=connection.table_id, user_id=user_id)
            except conn_models.DatabaseConnections.DoesNotExist:
                return Response({'message': ' connection not found'}, status=status.HTTP_404_NOT_FOUND)

            # Delete both records
            connection.delete()
            db_conn.delete()

            return Response({'message': 'Connection deleted successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': tok1['message']}, status=status.HTTP_401_UNAUTHORIZED)


class File_Connection(APIView):
    serializer_class = File_upload
    @swagger_auto_schema(request_body=File_upload)
    @transaction.atomic()
    def post(self, request):
        tok1 = token_function(request)
        if tok1["status"]==200:
            user_id=tok1['user_id']
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                file_type = serializer.validated_data['file_type']
                file_path112 = serializer.validated_data['file_path']
                conn_name = serializer.validated_data['connection_name']
                if conn_models.FileConnections.objects.filter(connection_name__iexact = conn_name, user_id=user_id).exists():
                    return Response({'message': ' Connection Name  Exists'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                try:
                    conn_type = conn_models.DataSources.objects.get(id=file_type, type__iexact='FILES')
                except conn_models.DataSources.DoesNotExist:
                    return Response({'message': 'Database Connection Not Implemented'}, status=status.HTTP_406_NOT_ACCEPTABLE)

                file_path=file_path112.name.replace(' ','').replace('&','').replace('-','_') ## .replace('_','')
                # t1=str(file_path.replace(' ','').replace('&',''))
                # click_file_path = f'{t1}'  
                if conn_models.DataSources.objects.filter(id=file_type).exists():
                    ft = conn_models.DataSources.objects.get(id=file_type)
                    file_save=file_files_save(file_path,file_path112)
                    file_url=file_save['file_url']
                    file_path1=file_save['file_key']
                    user= auth_models.UserProfile.objects.get(id=user_id)
                    file_conn=conn_models.FileConnections.objects.create(
                        file_type = ft,
                        source = file_url,
                        datapath=file_path1,
                        connection_name = conn_name,
                        user_id = user,
                        uploaded_at=created_at,
                        updated_at=updated_at
                    )
                    conn_id =conn_models.Connections.objects.create(
                        table_id = file_conn.id,
                        type = conn_type,
                        user_id = user,
                    )
                    return Response({'message':'Upload Succesfully','id': conn_id.id},status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Unsupported file type'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:  
                return Response({'message':"Invali Data"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
             return Response({'message':tok1['message']},status=status.HTTP_401_UNAUTHORIZED)


class File_operations(APIView):
    serializer_class = File_upload

    csrf_exempt
    @transaction.atomic()
    @swagger_auto_schema(request_body=File_upload)
    def put(self, request, id):
        tok1 = token_function(request)
        if tok1["status"] == 200:
            user_id = tok1["user_id"]
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                conn_name = serializer.validated_data["connection_name"]
                file_type = serializer.validated_data["file_type"]
                file_obj = serializer.validated_data["file_path"]
                conn_obj = conn_models.Connections.objects.get(id=id, user_id=user_id)

                if conn_models.FileConnections.objects.filter(connection_name__iexact = conn_name, user_id=user_id).exclude(conn_obj.table_id).exists():
                    return Response({'message': ' Connection Name  Exists'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                try:
                    file_conn = conn_models.FileConnections.objects.get(id=conn_obj.table_id, user_id=user_id)
                except conn_models.Connections.DoesNotExist:
                    return Response({"message": "Connection not found"}, status=status.HTTP_404_NOT_FOUND)

                # Delete old file from S3
                if file_conn.datapath:
                    try:
                        s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=str(file_conn.datapath))
                    except Exception as e:
                        return Response({"message": f"S3 Deletion Failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

                # Save new file
                new_filename = file_obj.name.replace(' ', '').replace('&', '').replace('-', '_')
                file_save = file_files_save(new_filename, file_obj)
                file_url = file_save["file_url"]
                file_key = file_save["file_key"]

                conn_type = conn_models.DataSources.objects.get(id=file_type, type__iexact="FILES")
                user = auth_models.UserProfile.objects.get(id=user_id)

                file_conn.file_type = conn_type
                file_conn.source = file_url
                file_conn.datapath = file_key
                file_conn.connection_name = conn_name
                file_conn.user_id = user
                file_conn.save()

                return Response({"message": "File updated successfully", "id": conn_obj.id}, status=status.HTTP_200_OK)
        else:
            return Response({'message': tok1['message']}, status=status.HTTP_401_UNAUTHORIZED)

    csrf_exempt
    @transaction.atomic()
    def get(self, request, id):
        tok1 = token_function(request)
        if tok1["status"] == 200:
            user_id = tok1["user_id"]
            try:
                conn_obj = conn_models.Connections.objects.get(id=id, user_id=user_id)
                file_conn = conn_models.FileConnections.objects.get(id=conn_obj.table_id, user_id=user_id)
            except conn_models.Connections.DoesNotExist:
                return Response({"message": "Connection not found"}, status=status.HTTP_404_NOT_FOUND)

            data = {
                "id": conn_obj.id,
                "file_type": file_conn.file_type.id,
                "connection_name": file_conn.connection_name,
                "file_url": file_conn.source,
                "datapath": str(file_conn.datapath),
                "uploaded_at": file_conn.uploaded_at,
                "updated_at": file_conn.updated_at,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'message': tok1['message']}, status=status.HTTP_401_UNAUTHORIZED)

    csrf_exempt
    @transaction.atomic()
    def delete(self, request, id):
        tok1 = token_function(request)
        if tok1["status"] == 200:
            user_id = tok1["user_id"]
            try:
                conn_obj = conn_models.Connections.objects.get(id=id, user_id=user_id)
                file_conn = conn_models.FileConnections.objects.get(id=conn_obj.table_id, user_id=user_id)
            except conn_models.Connections.DoesNotExist:
                return Response({"message": "Connection not found"}, status=status.HTTP_404_NOT_FOUND)

            # Delete file from S3
            try:
                if file_conn.datapath:
                    s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=str(file_conn.datapath))
            except Exception as e:
                return Response({"message": f"Failed to delete file from S3: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            # Delete DB records
            file_conn.delete()
            conn_obj.delete()

            return Response({"message": "File connection deleted successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({'message': tok1['message']}, status=status.HTTP_401_UNAUTHORIZED)



class Connection_list(APIView):
    @csrf_exempt
    @transaction.atomic()
    def get(self, request):
        tok1 = token_function(request)
        if tok1["status"] != 200:
            return Response({'message': tok1['message']}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = tok1['user_id']

        paginator = CustomPaginator()
        page_number = request.query_params.get(paginator.page_query_param, 1)
        page_size = request.query_params.get(paginator.page_size_query_param, 1000)
        search = request.query_params.get('search', '').strip()

        try:
            page_number = int(page_number)
            page_size = min(int(page_size), paginator.max_page_size)
        except (ValueError, TypeError):
            return Response({"error": "Invalid pagination parameters"}, status=400)

        offset = (page_number - 1) * page_size
        limit = page_size
        index = offset + limit

        # -------------------------
        # Filter Connections first based on search on related tables
        # -------------------------
        db_ids = conn_models.DatabaseConnections.objects.filter(
            user_id=user_id,
            is_connected=True,
            connection_name__icontains=search
        ).values_list('id', flat=True)

        file_ids = conn_models.FileConnections.objects.filter(
            user_id=user_id,
            connection_name__icontains=search
        ).values_list('id', flat=True)

        # Filter connections based on matching table_id in filtered DB or File connections
        connections = conn_models.Connections.objects.filter(
            user_id=user_id
        ).filter(
            Q(type=1, table_id__in=db_ids) |
            Q(type=2, table_id__in=file_ids)
        ).order_by('id')  # Optional: add sorting

        total_count = connections.count()
        connections = connections[offset:index]

        response_data = []

        for i in connections:
            server_type = conn_models.DataSources.objects.get(id=i.type.id)
            try:
                if server_type.type == 'DATABASE':
                    server_data = conn_models.DatabaseConnections.objects.get(
                        id=i.table_id,
                        user_id=user_id,
                        is_connected=True,
                        connection_name__icontains=search
                    )
                elif server_type.type == 'FILES':
                    server_data = conn_models.FileConnections.objects.get(
                        id=i.table_id,
                        user_id=user_id,
                        connection_name__icontains=search
                    )
                else:
                    continue

                response_data.append({
                    'display_name': server_data.connection_name,
                    'hierarchy_id': i.id,
                    'server_type': server_type.name,
                    'type': server_type.type,
                    'created_at': server_data.created_at,
                    'updated_at': server_data.updated_at
                })
            except Exception:
                continue

        return Response({
            'data': response_data,
            'page': page_number,
            'page_size': page_size,
            'total_items': total_count
        }, status=status.HTTP_200_OK)
    

class ETL_connection_list(APIView):
    @csrf_exempt
    @transaction.atomic()
    def get(self, request):
        tok1 = token_function(request)
        if tok1["status"] != 200:
            return Response({'message': tok1['message']}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = tok1['user_id']

        paginator = CustomPaginator()
        page_number = request.query_params.get(paginator.page_query_param, 1)
        page_size = request.query_params.get(paginator.page_size_query_param, 1000)
        search = request.query_params.get('search','')
        connection_type = request.query_params.get('type',1) 
        try:
            page_number = int(page_number)
            page_size = min(int(page_size), paginator.max_page_size)
        except (ValueError, TypeError):
            return Response({"error": "Invalid pagination parameters"}, status=400)

        offset = (page_number - 1) * page_size
        limit = page_size
        index=int((offset + limit) / 2)
        try:
            conn_models.DataSources.objects.get(id=connection_type)
        except:
            return Response({'message':'Connection Type Does Not Exist'},status=status.HTTP_404_NOT_FOUND)

        Connection_data = conn_models.Connections.objects.filter(user_id=user_id,type =connection_type)[offset:index]
        response_data = []
        for i in Connection_data:
            server_type = conn_models.DataSources.objects.get(id = i.type.id)
            match server_type.type:
                case 'DATABASE':
                    server_data = conn_models.DatabaseConnections.objects.get(id = i.table_id,user_id=user_id,is_connected=True,connection_name__icontains = search)
                    response_data.append({
                        'display_name': server_data.connection_name,
                        'hierarchy_id': i.id,
                        'server_id': server_data.id,
                        'server_type': server_type.name,
                        'type':'SERVER',
                    })
                case 'FILES':
                    files_data = conn_models.FileConnections.objects.get(id = i.table_id,user_id=user_id)
                    response_data.append({
                        'display_name': files_data.connection_name,
                        'hierarchy_id': i.id,
                        'server_id': files_data.id,
                        'server_type': server_type.name,
                        'type':'SERVER',
                    })
                case _:
                    return Response({'message':'Unspported Source'},status=status.HTTP_404_NOT_FOUND)
        response_data = {
             'data':response_data,
             'page': page_number,
            'page_size': page_size
        }
        return Response(response_data, status=status.HTTP_200_OK)



class Server_tables(APIView):
    @transaction.atomic
    def get(self,request,id):
        tok1 = token_function(request)
        if tok1["status"]==200:
            user_id = tok1['user_id']
            if conn_models.Connections.objects.filter(id=id,user_id=user_id).exists():
                connections_data = conn_models.Connections.objects.get(id = id,user_id=user_id)
                Database_data = conn_models.DatabaseConnections.objects.get(id=connections_data.table_id)
                server_type = conn_models.DataSources.objects.get(id=connections_data.type.id)
                server_conn=server_connection(Database_data.username,Database_data.password,Database_data.database,Database_data.hostname,Database_data.port,Database_data.service_name,server_type.name.upper(),Database_data.database_path)
                if server_conn['status']==200:
                    tables_list = get_table_details(server_type.name,server_conn['cursor'],Database_data.schema)
                    schema_map = {
                        "SQLITE": "main",
                        "ORACLE": Database_data.username.upper() if Database_data.username else None
                    }

                    Database_data.schema = schema_map.get(server_type.name.upper(), "public" if Database_data.server_type is None else Database_data.schema)
                    return Response({'message':'sucess','tables':tables_list,'database_name':Database_data.database,'schema':Database_data.schema,'connection_name':Database_data.connection_name,'id':connections_data.id},status = status.HTTP_200_OK)
                else:
                    return Response({'message':server_conn['message']},status=server_conn['status'])
            else:
                return Response({'message':'Connection Not Found'},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message":tok1['message']},status=status.HTTP_404_NOT_FOUND)
        


class FileSchema(APIView):
    @transaction.atomic
    def get(self, request, id):
        tok1 = token_function(request)
        if tok1["status"] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        user_id = tok1['user_id']
        if not conn_models.Connections.objects.filter(id=id,user_id = user_id).exists():
            return Response({'message': 'Connection not found'}, status=status.HTTP_404_NOT_FOUND)
        connection_data = conn_models.Connections.objects.get(id = id,user_id=user_id)
        File_data = conn_models.FileConnections.objects.get(id = connection_data.table_id,user_id= user_id)
        file_path = str(File_data.source.url if hasattr(File_data.source, 'url') else File_data.source)
        file_name = File_data.connection_name
        connection_name = getattr(File_data, "connection_name", file_name)

        try:
            tables = []
            if file_name.endswith((".xls", ".xlsx")):
                # package = Package(file_path)
                # for resource in package.resources:
                #     resource.infer()
                #     schema = resource.schema.to_descriptor()
                #     columns = [
                #         {"col": field["name"], "dtype": field.get("type", "any")}
                #         for field in schema.get("fields", [])
                #     ]
                #     tables.append({
                #         "tables": resource.name,  # sheet name
                #         "columns": columns
                #     })
                return Response({'message':'Not Implemeted AT'},status=status.HTTP_204_NO_CONTENT)
            else:
                resource = Resource(path=file_path)
                resource.infer()
                schema = resource.schema.to_descriptor()
                columns = [
                    {"col": field["name"], "dtype": field.get("type", "any")}
                    for field in schema.get("fields", [])
                ]
                tables.append({
                    "tables": file_name.split(".")[0],  # table name = file name without extension
                    "columns": columns
                })

            return Response({
                "message": "success",
                "tables": tables,
                "database_name": file_name,
                "schema": "file",
                "connection_name": connection_name,
                "id": id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': f'Error reading file: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class ListFilesView(APIView):
    def get(self, request):
        tok1 = token_function(request)
        if tok1["status"] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        user_id = tok1['user_id']
        path = request.query_params.get('path','')
        base_dir = f'/var/www/AB_Client/client2'
        directory = os.path.abspath(os.path.join(base_dir, path))
        try:
            files = [
                f for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f))
            ]
            return Response({"files": files}, status=status.HTTP_200_OK)
        except FileNotFoundError:
            return Response(
                {"error": f"Directory '{directory}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError:
            return Response(
                {"error": f"No permission to access '{directory}'."},
                status=status.HTTP_403_FORBIDDEN
            )
        


class ServerFileSchemaView(APIView):
    serializer_class = server_Files
    @swagger_auto_schema(request_body=server_Files)
    @csrf_exempt
    @transaction.atomic
    def post(self, request):
        tok1 = token_function(request)
        if tok1['status'] != 200:
            return Response({"message": tok1['message']}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            source_type = serializer.validated_data['source_type']
            file_name = serializer.validated_data['file_name']

            try:
                tables = []
                if file_name.endswith((".xls", ".xlsx")):
                    # package = Package(file_path)
                    # for resource in package.resources:
                    #     resource.infer()
                    #     schema = resource.schema.to_descriptor()
                    #     columns = [
                    #         {"col": field["name"], "dtype": field.get("type", "any")}
                    #         for field in schema.get("fields", [])
                    #     ]
                    #     tables.append({
                    #         "tables": resource.name,  # sheet name
                    #         "columns": columns
                    #     })
                    return Response({'message':'Not Supported'},status=status.HTTP_204_NO_CONTENT)
                elif file_name.endswith(".csv"):
                    resource = Resource(path=f'/var/www/AB_Client/client2/{source_type}/{file_name}')
                    resource.infer()
                    schema = resource.schema.to_descriptor()
                    columns = [
                        {"col": field["name"], "dtype": field.get("type", "any")}
                        for field in schema.get("fields", [])
                    ]
                    tables.append({
                        "tables": file_name.split(".")[0],  # table name = file name without extension
                        "columns": columns
                    })
                else:
                    return Response({'message':'Not Supported'},status=status.HTTP_204_NO_CONTENT)

                return Response({
                    "message": "success",
                    "tables": tables,
                    "database_name": file_name,
                    "schema": "file",
                    "connection_name": file_name
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'message': f'Error reading file: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'message':'Serializer Error'},status=status.HTTP_400_BAD_REQUEST)
        


@api_view(['POST'])
def get_available_schemas(request):
    tok1 = token_function(request)
    
    if tok1["status"] != 200:
        return Response(tok1, status=tok1['status'])
        
    try:
        # Get connection details from request
        data = request.data
        try:
            conn_type = conn_models.DataSources.objects.get(id=data['database_type'], type__iexact='DATABASE')
        except conn_models.DataSources.DoesNotExist:
            return Response({'message': ' Connection Not Implemented'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        server_conn = server_connection(
            data['username'],
            encode_value(data['password']),
            data['database'],
            data['hostname'],
            data['port'],
            data.get('service_name',''),
            conn_type.name.upper(),
            data.get('path','')
        )
        
        if server_conn['status'] != 200:
            return Response({'message': server_conn['message']}, status=server_conn['status'])
            
        # Get schemas
        cursor = server_conn['cursor']
        schemas_query = cursor.execute(text("""
            SELECT nspname 
            FROM pg_catalog.pg_namespace 
            WHERE nspname NOT LIKE 'pg_%' 
            AND nspname <> 'information_schema';
        """))
        schemas = [row[0] for row in schemas_query.fetchall()]
        
        return Response({'schemas': schemas}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)