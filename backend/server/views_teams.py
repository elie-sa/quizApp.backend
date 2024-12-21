from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Course, Major, Notebook, Rating, Team
from django.db.models import Q
from .serializers import NotebookSerializer, TeamSerializer
from rest_framework import status
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import get_template

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_team(request):
    user = request.user
    name = request.data.get('name')

    testTeam = Team.objects.filter(name=name)
    if testTeam.exists():
        return Response({"error": f"Team with  name {name} already exists. Please provide a unique team name."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        team = Team.objects.create(name=name)
        team.members.add(user)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    serializer = TeamSerializer(team)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_my_teams(request):
    search_entry = request.query_params.get("search_entry")
    teams = request.user.teams
    if search_entry:
        teams = teams.filter(name__icontains=search_entry)

    serializer = TeamSerializer(teams, many=True)
    return Response(serializer.data, status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_team_member(request):
    email = request.query_params.get('email', None)
    team_id = request.query_params.get('team_id', None)

    if not email or not team_id:
        return Response({"Invalid JSON Format": "email or team_id missing"})

    try:
        team = Team.objects.get(id=team_id)
    except:
        return Response("Invalid team_id provided.")

    try:
        user = User.objects.get(email=email)
    except:
        return Response({"error": "Wrong email user not found."}, status=status.HTTP_400_BAD_REQUEST)
    
    data = {
        'user_id': user.pk,
        'user_name': f"{user.first_name} {user.last_name}",
        'team_id': team_id,
        'team_name': team.name
    }

    message = get_template('send_team_request.txt').render(data)
    send_mail(
        subject='Team Invitation Request',
        message=message,
        recipient_list=[user.email],
        from_email="e.sawmaawad@gmail.com",
        fail_silently=False
    )

    return Response("Sent invitation successfully", status=status.HTTP_200_OK)

@api_view(['GET'])
def add_service(request):
    user_id = request.query_params.get('user_id')
    team_id = request.query_params.get('team_id')
    team = Team.objects.get(id=team_id)
    user = User.objects.get(id=user_id)
    team.members.add(user)

    return Response("Successfully Added User", status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_team_members(request):
    team_id = request.query_params.get('team_id')
    try:
        team = Team.objects.get(id=team_id)
    except:
        return Response({"error": "Invalid team_id provided."})
    
    serializer = TeamSerializer(team)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def exit_team(request):
    user = request.user
    team_id = request.query_params.get('team_id')

    try:
        team = Team.objects.get(id = team_id)
    except:
        return Response({"error": "Invalid team_id provided"})
    
    team.members.remove(user)
    team.save()
    return Response({"message": "You have been successfully removed from the team."}, status=status.HTTP_200_OK)