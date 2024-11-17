from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Course, Major, Notebook, Rating, Team
from django.db.models import Q
from .serializers import NotebookSerializer
from rest_framework import status

@api_view(['POST'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_create_notebook(request):
    user = request.user
    title = request.data.get('title')
    color = request.data.get('color')
    course_ids = request.data.get('courses', [])

    testNotebook = Notebook.objects.filter(user_creator = user, title = title)
    if testNotebook:
        return Response({"title": "A notebook with this title already exists. Please choose a different title. "})

    try:
        notebook = Notebook.objects.create(
            title = title,
            color = color,
            user_creator = user
    )
    except:
        return Response("Invalid/Missing Request", status=status.HTTP_400_BAD_REQUEST)

    if course_ids:
        courses = Course.objects.filter(id__in=course_ids)
        notebook.courses.add(*courses)

    serializer = NotebookSerializer(notebook)
    return Response(serializer.data, status = status.HTTP_201_CREATED)
    
@api_view(['POST'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def team_create_notebook(request):
    user = request.user
    team_id = request.data.get('team_id')
    title = request.data.get('title')
    color = request.data.get('color')
    course_ids = request.data.get('courses', [])

    try:
        team = Team.objects.get(id = team_id)
    except:
        return Response("Invalid team_id provided", status= status.HTTP_400_BAD_REQUEST)
    
    if not team.members.filter(id=user.id).exists():
        return Response({"forbidden": "User does not belong to this team."}, status=status.HTTP_403_FORBIDDEN)

    testNotebook = Notebook.objects.filter(user_creator = user, title = title)
    if testNotebook:
        return Response({"title": "A notebook with this title already exists. Please choose a different title. "})

    try:
        notebook = Notebook.objects.create(
            title = title,
            color = color,
            team_creator = team
    )
    except:
        return Response("Invalid/Missing Request", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if course_ids:
        courses = Course.objects.filter(id__in=course_ids)
        notebook.courses.add(*courses)

    serializer = NotebookSerializer(notebook)
    return Response(serializer.data, status = status.HTTP_201_CREATED)
        
