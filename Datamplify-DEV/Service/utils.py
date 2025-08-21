from sqlalchemy import text
from Datamplify.settings import logger
from django.utils.timezone import now
from Datamplify import settings
import datetime,json,io,base64
from cryptography.fernet import Fernet
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from authentication import models as auth_models
from Connections import models as conn_models
from FlowBoard import models as flow_models
from TaskPlan import models as task_models
from rest_framework.pagination import PageNumberPagination
# from Connections.utils import generate_engine
import boto3,os,uuid

# def encode_value(value):
#     f = Fernet(settings.Fernet_Key)
#     encrypted = f.encrypt(value.encode())
#     return encrypted.decode()


# def decode_value(encrypted_value) :
#     f = Fernet(settings.Fernet_Key)
#     decrypted = f.decrypt(encrypted_value.encode())
#     return decrypted.decode()

try:
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY)
except Exception as e:
    print(e)

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)

def encode_value(input_string):
    input_bytes = str(input_string).encode('utf-8')
    encoded_bytes = base64.b64encode(input_bytes)
    encoded_string = encoded_bytes.decode('utf-8')
    return encoded_string

def decode_value(encoded_string):
    decoded_bytes = base64.b64decode(encoded_string.encode('utf-8'))
    decoded_string = decoded_bytes.decode('utf-8')
    return decoded_string



def file_files_save(file_path,file_path112):
    if settings.file_save_path=='s3':
        # t1=created_at.strftime('%Y-%m-%d_%H-%M-%S')+str(file_path)
        t1=str(datetime.datetime.now()).replace(' ','_').replace(':','_')+'_IN_'+str(file_path)
        file_path1 = f'Datamplify/files/{t1}'
        print(file_path1)
        try:
            file_path112.seek(0)
            s3.upload_fileobj(file_path112, settings.AWS_STORAGE_BUCKET_NAME, file_path1, ExtraArgs={'ACL': 'public-read'})
        except:
            try:
                with open(file_path112.temporary_file_path(), 'rb') as data:  ## read that binary data in a file(before replace file data)
                    s3.upload_fileobj(data, settings.AWS_STORAGE_BUCKET_NAME, file_path1)  ## pass that data in data and replaced file name in file key.
            except:
                data = ContentFile(file_path112.read())
                s3.upload_fileobj(data, settings.AWS_STORAGE_BUCKET_NAME, file_path1, ExtraArgs={'ACL': 'public-read'})
        file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_path1}"
        data_fn={
            "file_key":file_path1,
            "file_url":file_url
        }
        return data_fn
    else:
        # t1=created_at.strftime('%Y-%m-%d_%H-%M-%S')+str(file_path)
        t1=str(datetime.datetime.now()).replace(' ','_').replace(':','_')+'_IN_'+str(file_path)
        file_path1 = f'insightapps/files/{t1}'   
        # with default_storage.open(file_path112, 'w') as file:
        #     file.write(file_path1)   
        file_content = ContentFile(file_path112.read())
        default_storage.save(file_path1, file_content)
        file_url = f"{settings.file_save_url}media/{file_path1}"
        data_fn={
            "file_key":file_path1,
            "file_url":file_url
        }
        return data_fn  



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')

def get_last_model_id(type):
    if type.lower() =='flow':
        last_obj = flow_models.FlowBoard.objects.count()
    elif type.lower() =='task':
        last_obj = task_models.TaskPlan.objects.count()
    else:
        0
    return last_obj if last_obj else 0

def generate_user_unique_code(request,type):
    """Generate a unique code using IP + timestamp + model last ID."""
    ip = get_client_ip(request).replace('.', '')  
    timestamp = now().strftime("%Y%m%d%H%M%S")     
    last_id = get_last_model_id(type)         

    seed = f"{ip}-{timestamp}-{last_id}"
    # hash_part = hashlib.md5(seed.encode()).hexdigest()[:6].upper()  # Short hash

    # return f"{ip}-{hash_part}-{last_id}"
    return seed



def delete_file(data):
    try: 
        a1='media/'+str(data)
        os.remove(a1)
    except:
        pass



def file_save_1(data,server_id,queryset_id,ip,dl_key):
    if settings.file_save_path=='s3':
        t1=str(datetime.datetime.now()).replace(' ','_').replace(':','_')
        file_path = f'{t1}{server_id}{queryset_id}.txt'
        # with open(file_path, 'w') as file:
        #     json.dump(data, file, indent=4)
        json_data = json.dumps(data, indent=4)
        file_buffer = io.BytesIO(json_data.encode('utf-8'))
        file_key = f'Datamplify/{ip}/{file_path}'
        if dl_key=="":
            s3.upload_fileobj(file_buffer, Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)
            file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_key}"
        else:
            s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=str(dl_key))
            s3.upload_fileobj(file_buffer, Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)
            file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_key}"
        data_fn={
            "file_key":file_key,
            "file_url":file_url
        }
        return data_fn
    else:
        if dl_key=="" or dl_key==None:
            pass
        else:
            delete_file(str(dl_key))
        
        # t1=created_at.strftime('%Y-%m-%d_%H-%M-%S')
        t1=str(datetime.datetime.now()).replace(' ','_').replace(':','_')
        file_path = f'insightapps/{ip}/{t1}.txt'
        json_data = json.dumps(data, indent=4)
        with default_storage.open(file_path, 'w') as file:
            file.write(json_data)
        file_url = f"{settings.file_save_url}media/{file_path}"
        data_fn={
            "file_key":file_path,
            "file_url":file_url
        }
        return data_fn
    

class CustomPaginator(PageNumberPagination):
    page = 10000 # records per page
    page_size_query_param = 'page_size'
    max_page_size = 1000000 #max records per page