import re
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.shortcuts import render
from .models import EmailConfirmationToken
from .serializers import PasswordChangeSerializer, UserSerializer
from django.core.mail import send_mail
from django.template.loader import get_template
import pyotp
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    email = request.data.get('email')
    username = request.data.get('username')

    if username and User.objects.filter(username=username).exists():
        return Response({'username': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if email and User.objects.filter(email=email).exists():
        return Response({'email': 'The email address is already in use.'}, status=status.HTTP_400_BAD_REQUEST)

    if serializer.is_valid():
        user = serializer.save()
        password = request.data.get('password')
        user.set_password(password)
        user.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        email_token = EmailConfirmationToken.objects.create(user=user)
        send_confirmation_email(email=user.email, token_id=email_token.pk, user_id=user.pk, access_token=access_token)

        response = Response({
            'access': access_token,
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)

        return response

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    login_credential = request.data["login_credential"].strip()

    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    if re.match(email_pattern, login_credential):
        login_kind = "email"
        try:
            user = User.objects.get(email__iexact=login_credential)
        except:
            return Response(f"Invalid {login_kind} or password.", status=status.HTTP_400_BAD_REQUEST)
    else:
        login_kind = "email"
        try:
            user = User.objects.get(username=login_credential)
        except:
            return Response(f"Invalid {login_kind} or password.", status=status.HTTP_400_BAD_REQUEST)
        
    if not user.profile.is_confirmed:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return Response({
            "message": "Invalid login credentials. Email Verification is needed.",
            'access': access_token,
            'refresh': str(refresh),
            }, status=status.HTTP_403_FORBIDDEN)
    

    if not user.check_password(request.data['password']):
        return Response(f"Invalid {login_kind} or password.", status=status.HTTP_400_BAD_REQUEST)
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    serializer = UserSerializer(user)

    response = Response({
        'access': access_token,
        'user': serializer.data
    })

    return response

# @api_view(['POST'])
# def login(request):
#     login_credential = request.data["login_credential"].strip()

#     email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

#     if re.match(email_pattern, login_credential):
#         login_kind = "email"
#         try:
#             user = User.objects.get(email__iexact=login_credential)
#         except:
#             return Response(f"Invalid {login_kind} or password.", status=status.HTTP_400_BAD_REQUEST)
#     else:
#         login_kind = "email"
#         try:
#             user = User.objects.get(username=login_credential)
#         except:
#             return Response(f"Invalid {login_kind} or password.", status=status.HTTP_400_BAD_REQUEST)
        
#     if not user.profile.is_confirmed:
#         return Response("Invalid login credentials. Email Verification is needed.", status=status.HTTP_403_FORBIDDEN)
#     if not user.check_password(request.data['password']):
#         return Response(f"Invalid {login_kind} or password.", status=status.HTTP_400_BAD_REQUEST)
    
#     refresh = RefreshToken.for_user(user)
#     access_token = str(refresh.access_token)

#     serializer = UserSerializer(user)

#     response = Response({
#         'access': access_token,
#         'user': serializer.data
#     })

#     return response

@api_view(['POST'])
def logout(request):
    response = Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
    return response

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_email_token(request):
    user = request.user
    token = EmailConfirmationToken.objects.create(user=user)

    access_token = request.headers.get('Authorization').split(' ')[1] if request.headers.get('Authorization') else None
    send_confirmation_email(email=user.email, token_id=token.pk, user_id=user.pk, access_token=access_token)
    return Response(data=None, status=status.HTTP_201_CREATED)

def send_confirmation_email(email, token_id, user_id, access_token):
    data = {
        'token_id': str(token_id),
        'user_id': str(user_id),
        'auth_token': access_token
    }
    message = get_template('confirmation_email.txt').render(data)
    send_mail(
        subject='Please confirm your email',
        message=message,
        recipient_list=[email],
        from_email="e.sawmaawad@gmail.com",
        fail_silently=False
    )
  
@csrf_exempt
def confirm_email_view(request):
    token_id = request.GET.get('token_id', None)
    auth_token = request.GET.get('auth_token', None) 

    try:
        token = EmailConfirmationToken.objects.get(pk=token_id)
        user = token.user
        user.save()
        profile = user.profile
        profile.is_confirmed = True
        profile.save()
        token.delete()
        
        data = {'is_email_confirmed': True, 'token': auth_token}
        return render(request, template_name='confirm_email_view.html', context=data)    
    except EmailConfirmationToken.DoesNotExist:
        data = {'is_email_confirmed': False, 'token': auth_token}
        return render(request, template_name='confirm_email_view.html', context=data)

@api_view(['POST'])
def forgot_password(request):
    try:
        email = request.data['email']
    except: 
        return Response("Error in JSON body, please include an email.", status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.filter(email=email).first()
    if user:
        send_otp(user)
        return Response("Success! The email address you provided has been found.", status=status.HTTP_200_OK)
    else:
        return Response("Error: The email address you entered could not be found.", status=status.HTTP_400_BAD_REQUEST)
    
#After calling the forgot password (service)
def send_otp(user):
    user.profile.generate_secret_key()
    totp = pyotp.TOTP(user.profile.secret_key, interval=60)
    otp = totp.now()

    send_mail(
        'Your OTP Code',
        f'Your OTP code is {otp}. It is valid for the next minute.',
        "e.sawmaawad@gmail.com",
        [user.email],
        fail_silently=False,
    )

@api_view(['POST'])
def verify_otp(request):
    try:
        email = request.data['email']
        otp = request.data['otp']
    except KeyError:
        return Response("Error in JSON body, please include both email and otp.", status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.filter(email=email).first()
    if user and user.profile.secret_key:
        if verify_otp_service(user.profile.secret_key, otp):
            return Response("OTP is valid.", status=status.HTTP_200_OK)
        else:
            return Response("Invalid OTP or OTP expired.", status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response("User not found or secret key missing.", status=status.HTTP_400_BAD_REQUEST)

def verify_otp_service(user_secret_key, otp):
    totp = pyotp.TOTP(user_secret_key, interval=60)
    return totp.verify(otp)

@api_view(['POST'])
def change_forgotten_password(request):
    serializer = PasswordChangeSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        new_password = serializer.validated_data['new_password']
        
        user = User.objects.filter(email=email).first()
        if user:
            user.set_password(new_password)
            user.save()
            return Response("Password has been successfully changed.", status=status.HTTP_200_OK)
        else:
            return Response("User not found.", status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)