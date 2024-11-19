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
    serializer = TeamSerializer(request.user.teams, many=True)
    return Response(serializer.data, status.HTTP_200_OK)

