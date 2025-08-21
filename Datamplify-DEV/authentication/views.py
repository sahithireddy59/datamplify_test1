from rest_framework.views import APIView
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from authentication import models as auth_models
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from Datamplify import settings
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from authentication import serializers
from oauth2_provider.models import AccessToken
from django.contrib.auth.hashers import make_password,check_password
from authentication.utils import get_access_token
from pytz import utc
import random,datetime
from drf_yasg.utils import swagger_auto_schema
from oauth2_provider.decorators import protected_resource
from django.http import JsonResponse
import re

########### SIGN UP #########




created_at=datetime.datetime.now(utc)
updated_at=datetime.datetime.now(utc)
expired_at=datetime.datetime.now()+datetime.timedelta(days=2)


@protected_resource()
def user_info_view(request):
    user = request.resource_owner
    return JsonResponse({
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role.name if hasattr(user, 'role') else 'standard_user',
    })

class SignUp(APIView):
    serializer_class= serializers.RegisterSerializer
    @swagger_auto_schema(request_body=serializers.RegisterSerializer)
    @transaction.atomic()
    @csrf_exempt
    def post(self,request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid(raise_exception=True):
            u=serializer.validated_data['username']
            email = serializer.validated_data['email']
            pwd=serializer.validated_data['password']
            try:
                unique_id = get_random_string(length=64)
                current_site = str(settings.Link_url)
                api = 'authentication/email-activation/'
                Gotp = random.randint(10000,99999)
                context = {'Gotp': Gotp,'api':api,'unique_id':unique_id,'current_site':current_site,'username':u}
                html_message = render_to_string('registration.html', context)
        
                message = 'Hello, welcome to our website!'
                subject = "Welcome to Datamplify: Verify your account"
                from_email = settings.EMAIL_HOST_USER
                to_email = [email.lower()]
                send_mail(subject, message, from_email, to_email, html_message=html_message)
                adtb=auth_models.UserProfile.objects.create_user(username=u,password=pwd,email=email,is_active=False)
                auth_models.Account_Activation.objects.create(user = adtb, key = unique_id, otp=Gotp,email=email)
            except Exception as e:
                return Response({"message":f"SMTP Error"},status=status.HTTP_400_BAD_REQUEST)
            data = {
                "message" : "Account Activation Email Sent",
                "email" : email.lower(),
                "emailActivationToken"  : unique_id
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"Serializer Value Error"},status=status.HTTP_400_BAD_REQUEST)  


class AccountActivate(APIView):
    serializer_class = serializers.ActivationSerializer
    @swagger_auto_schema(request_body=serializers.ActivationSerializer)

    @csrf_exempt
    @transaction.atomic
    def post(self,request,token):
        try:
            token = auth_models.Account_Activation.objects.get(key=token)
        except:
            return Response({"message" : "Invalid Token in URL"}, status=status.HTTP_404_NOT_FOUND)
        if token.expiry_date > datetime.datetime.now(utc):
            serializer=self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                u_id = token.user.id
                otp_valid = token.otp
                otp = serializer.validated_data['otp']
                if len(str(otp)) < 5:
                    return Response({'message':'OTP field cannot be empty'},status=status.HTTP_406_NOT_ACCEPTABLE)
                if otp_valid ==otp:
                    auth_models.UserProfile.objects.filter(id=u_id).update(is_active='True')
                    auth_models.Account_Activation.objects.filter(user = u_id).delete()
                    user = auth_models.UserProfile.objects.get(id=u_id)
                    password = f"Dataplify_{user.username}_{user.id}_role"
                    # create_airflow_user(
                    #         username=user.username,
                    #         email=user.email,
                    #         password=password
                    #     )
                    return Response({"message" : "Account successfully activated"},status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Incorrect OTP, Please try again"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"message":"Enter OTP"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message" : "Activation Token/ OTP Expired"} , status=status.HTTP_401_UNAUTHORIZED)  
        

class Login(APIView):
    serializer_class = serializers.LoginSerializer
    @swagger_auto_schema(request_body=serializers.LoginSerializer)
    @csrf_exempt
    def post(self,request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid(raise_exception=True):
            email  = serializer.data['email']
            password = serializer.data['password']

            if (auth_models.UserProfile.objects.filter(email__iexact=email).exists()):
                if (auth_models.UserProfile.objects.filter(email__iexact=email,is_active=True).exists()):
                    data = auth_models.UserProfile.objects.get(email__iexact=email)
                    try:
                        print(password)
                        user = authenticate(username=data, password=password)
                    except Exception as e:
                        print(e)
                        return Response({"message":"Incorrect Password"}, status=status.HTTP_401_UNAUTHORIZED) 
                    AccessToken.objects.filter(expires__lte=datetime.datetime.now(utc)).delete()
                    print(user)
                    if user is not None:
                        access_token=get_access_token(data.username,password)
                        if access_token['status']==200:
                            # AccessToken.objects.filter(token=access_token['data']['access_token']).update(is_allowed=False)
                            login(request, user)
                            print(access_token)
                            data = ({
                                "accessToken":access_token['data']['access_token'],
                                "username":data.username,
                                "email":data.email,
                                "first_name":data.first_name,
                                "last_name":data.last_name,
                                "user_id":data.id,
                                "is_active":data.is_active,
                                "created_at":data.created_at
                            })
                            return Response(data, status=status.HTTP_200_OK)
                        else:
                            return Response(access_token,status=access_token['status'])
                    else:
                        return Response({"message" : "Incorrect password"},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message":'Account is in In-Active, please Activate your account'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return Response({"message" :"You do not have an account, Please SIGNUP with Datamplify"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"message" : "Enter Email and Password"}, status=status.HTTP_400_BAD_REQUEST)



# class Account_reactivate(CreateAPIView):
#     serializer_class = serializers.ForgetPasswordSerializer

#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             email = serializer.validated_data['email']
#             if UserProfile.objects.filter(email__iexact=email,is_active=True).exists():
#                 return Response({"message":"Account already Activated, please login"},status=status.HTTP_408_REQUEST_TIMEOUT)
#             elif UserProfile.objects.filter(email__iexact=email).exists():
#                 pass
#             else:
#                 return Response({"message":"You do not have an account, Please SIGNUP with Analytify"},status=status.HTTP_404_NOT_FOUND)
#             name = UserProfile.objects.get(email__iexact=email)
#             up_data=models.UserRole.objects.filter(user_id=name.id).values('created_by')
#             for u1 in up_data:
#                 if not name.id==u1['created_by']:
#                     return Response({'message':'Not allowed to re-activate the account'},status=status.HTTP_406_NOT_ACCEPTABLE)
#             try:
#                 unique_id = get_random_string(length=64)
#                 # protocol ='https://'
#                 # current_site = 'hask.io/'
#                 current_site = str(settings.link_url)
#                 api = 'authentication/activate_account/'
#                 Gotp = random.randint(10000,99999)
#                 context = {'Gotp': Gotp,'api':api,'unique_id':unique_id,'current_site':current_site}
#                 html_message = render_to_string('account_reactivate.html', context)
        
#                 message = 'Hello, welcome to Analytify website!'
#                 subject = "Welcome to Analytify: Verify your account"
#                 from_email = settings.EMAIL_HOST_USER
#                 to_email = [email.lower()]
#                 send_mail(subject, message, from_email, to_email, html_message=html_message)

#                 Account_Activation.objects.create(user = name.id, key = unique_id,otp=Gotp,email=email,created_at=created_at,expiry_date=expired_at)
#                 data = {
#                     "message" : "Account Activation Email Sent",
#                     "email" : email.lower(),
#                     "emailActivationToken"  : unique_id
#                 }
#                 return Response(data, status=status.HTTP_201_CREATED)
#             except :
#                 return Response({"message":"SMTP Error"},status=status.HTTP_503_SERVICE_UNAVAILABLE)
#         else:
#             return Response ({"message":"Serializer Value Error"}, status=status.HTTP_400_BAD_REQUEST)
        


class ForgotPasswordView(APIView):
    serializer_class = serializers.ForgetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            if auth_models.UserProfile.objects.filter(email__iexact=email).exists():
                pass
            else:
                return Response({"message":"You do not have an account, Please SIGNUP with Analytify"},status=status.HTTP_404_NOT_FOUND)
            name = auth_models.UserProfile.objects.get(email__iexact=email)
            u_id = name.id
            auth_models.Reset_Password.objects.filter(user=u_id).delete()
            try:
                unique_id = get_random_string(length=32)
                # current_site = 'hask.io/'
                # protocol ='https://'
                current_site = str(settings.Link_url)
                # interface = get_user_agent(request)
                auth_models.Reset_Password.objects.create(user=u_id, key=unique_id,created_at=created_at)
                subject = "Datamplify Reset Password Assistance"
                api = 'authentication/reset-password/'
                context = {'username':name.username,'api':api,'unique_id':unique_id,'current_site':current_site}
                html_message = render_to_string('reset_password.html', context)

                send_mail(
                    subject = subject,
                    message = "Hi {}, \n\nThere was a request to change your password! \n\nIf you did not make this request then please ignore this email. \n\nYour password reset link \n {}{}{}".format(name.username,current_site, api, unique_id),
                    from_email = settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    html_message=html_message
                )
                data = {
                    "message" : "Password reset email sent",
                    "Passwordresettoken" : unique_id
                }
                return Response(data,status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                return Response({"message" : "SMTP error"},status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response ({"message":"Serializer Value Error"}, status=status.HTTP_400_BAD_REQUEST)
        


class ConfirmPasswordView(APIView):
    serializer_class = serializers.ConfirmPasswordSerializer

    def put(self, request, token):
        try:
            token = auth_models.Reset_Password.objects.get(key=token)
        except:
            return Response({"message":"Token Doesn't Exists"},status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            name = token.user
            use = auth_models.UserProfile.objects.get(id=name)
            email = use.email
            pwd=serializer.validated_data['password']
            cnfpwd=serializer.validated_data['confirmPassword']
            pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$!%*?&])[A-Za-z\d@#$!%*?&]{8,}$"
            r= re.findall(pattern,pwd)
            if not r:
                data={
                    "message":"Password is invalid.Min 8 character. Password must contain at least :one small alphabet one capital alphabet one special character \nnumeric digit."
                }
                return Response(data,status=status.HTTP_406_NOT_ACCEPTABLE)
            elif pwd!=cnfpwd:
                return Response({"message":"Passsword did not matched"},status=status.HTTP_401_UNAUTHORIZED)
            else:
                pass

            try:
                date_string = datetime.datetime.now().date()
                date_obj = datetime.datetime.strptime(str(date_string), '%Y-%m-%d')
                date = date_obj.strftime('%d %b %Y').upper()
                time_string = datetime.datetime.now().time()  # Current time Format 12:34:46.9875
                time = str(time_string).split('.')[0] # Converted Time 12:34:46
                context = {'username':use.username,"date":date,"time":time,"login_url":'http://202.65.155.119/authentication/login'}
                html_message = render_to_string('reset_password_success.html', context)
                subject = "Password change alert Acknowledgement"
                send_mail(
                    subject = subject,
                    message = "Hi {}, \nYou have successfully changed your Analytify Login password on {} at {} . Do not share with anyone..\nDo not disclose any confidential information such as Username, Password, OTP etc. to anyone.\n\nBest regards,\nThe Analytify Team".format(use.username,date,time),
                    from_email = settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    html_message=html_message
                )
                auth_models.UserProfile.objects.filter(id=name).update(password=make_password(pwd),updated_at=datetime.datetime.now())
                auth_models.Reset_Password.objects.filter(user=use.id).delete()
                return Response({"message" : "Password changed Successfully, Please Login"}, status=status.HTTP_200_OK)
            except:
                return Response({"message" : "SMTP error"},status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"message":"Password Fields didn't Match"}, status=status.HTTP_400_BAD_REQUEST)
        


# # Update/Change Password 
# class UpdatePasswordAPI(CreateAPIView):
#     serializer_class = serializers.UpdatePasswordSerializer

#     @transaction.atomic
#     def put(self,request,token):
#         tok1 = views.test_token(token)
#         if tok1["status"]==200:
#             usertable=UserProfile.objects.get(id=tok1['user_id'])
#             serializer = self.get_serializer(data = request.data)
#             if serializer.is_valid(raise_exception=True):
#                 current_pwd = serializer.validated_data['current_password']
#                 new_pwd = serializer.validated_data['new_password']
#                 confirm_pwd = serializer.validated_data['confirm_password']
#                 pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$!%*?&])[A-Za-z\d@#$!%*?&]{8,}$"
#                 r=re.findall(pattern,new_pwd)
#                 if check_password(current_pwd, usertable.password):
#                     pass
#                 else:
#                     return Response({"message":"Incorrect Current Password"}, status=status.HTTP_406_NOT_ACCEPTABLE)
#                 if not r:
#                     data={
#                         "message":"Password is invalid.Min 8 character. Password must contain at least :one small alphabet one capital alphabet one special character \nnumeric digit."
#                     }
#                     return Response(data,status=status.HTTP_406_NOT_ACCEPTABLE)
#                 elif len(new_pwd)<8 or len(confirm_pwd)<8:
#                     return Response({"message":"Check Password Length"}, status=status.HTTP_400_BAD_REQUEST)
#                 elif new_pwd!=confirm_pwd:
#                     return Response({"message":"Password did not matched"},status=status.HTTP_406_NOT_ACCEPTABLE)
#                 elif current_pwd==confirm_pwd:
#                     return Response({"message":"New password is same as old password, Not acceptable"},status=status.HTTP_406_NOT_ACCEPTABLE)
#                 if new_pwd==confirm_pwd:
#                     UserProfile.objects.filter(id=usertable.id).update(password=make_password(new_pwd),updated_at=datetime.datetime.now())
#                     return Response({"message":"Password Updated Successfully"}, status=status.HTTP_200_OK)
#                 else:
#                     return Response({"message":"There was an error with your Password combination"}, status=status.HTTP_406_NOT_ACCEPTABLE)                        
#             else:
#                 return Response({"message":"Serializer Value Errors"}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response(tok1,status=tok1['status'])


# class UpdateEMAILAPI(CreateAPIView):
#     serializer_class = serializers.ForgetPasswordSerializer

#     @transaction.atomic
#     def post(self,request,token):
#         tok1 = views.test_token(token)
#         if tok1["status"]==200:
#             serializer = self.get_serializer(data = request.data)
#             if serializer.is_valid(raise_exception=True):
#                 email = serializer.validated_data['email']
#                 if UserProfile.objects.filter(email__iexact=email).exists():
#                     return Response({"message":"Email already Exists"},status=status.HTTP_406_NOT_ACCEPTABLE)
#                 else:
#                     pass
#                 try:
#                     Account_Activation.objects.filter(email__iexact=email).delete()
#                     unique_id = get_random_string(length=64)
#                     # protocol ='https://'
#                     # current_site = 'hask.io/'
#                     current_site = str(settings.link_url)
#                     api = 'core/activate_account/'

#                     Gotp = random.randint(10000,99999)
#                     message = "Hi {},\n\n Request For Email Update.\nYour One-Time Password is {}\nTo Change your Email, please click on the following url:\n {}{}{}\n".format(tok1['username'],Gotp,current_site,api,unique_id)
#                     subject = "Analytify Email Update Request"
#                     from_email = settings.EMAIL_HOST_USER
#                     to_email = [email]
#                     send_mail(subject, message, from_email, to_email)
#                     Account_Activation.objects.create(user=tok1['user_id'], key = unique_id, otp=Gotp, email=email,created_at=created_at,expiry_date=expired_at)

#                     data = {
#                         "message" : "Requested for Email Update", 
#                         "emailActivationToken": unique_id
#                         }
#                     return Response(data, status=status.HTTP_200_OK)
#                 except:
#                     return Response({"message" : "SMTP error"},status=status.HTTP_401_UNAUTHORIZED)
#             else:
#                 return Response({"message":"Serializer Value Errors"}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response(tok1,status=tok1['status'])

            