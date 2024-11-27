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
    user_id = request.query_params.get('user_id', None)
    team_id = request.query_params.get('team_id', None)

    if not user_id or not team_id:
        return Response({"Invalid JSON Format": "user_id or team_id missing"})
    
    try:
        Team.objects.get(id=team_id)
    except:
        return Response("Invalid team_id provided.")

    try:
        user = User.objects.get(id = user_id)
    except:
        return Response("Invalid user_id provided.")
    
    data = {
        'user_id': user_id,
        'user_name': f"{user.first_name} {user.last_name}",
        'team_id': team_id
    }

    message = get_template('send_team_request.txt').render(data)
    send_mail(
        subject='Team Invitation Request',
        message=message,
        recipient_list=[user.email],
        from_email="e.sawmaawad@gmail.com",
        fail_silently=False
    )
