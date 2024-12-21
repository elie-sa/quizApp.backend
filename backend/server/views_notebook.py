from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Course, Major, Notebook, Rating, Team
from django.db.models import Q, Exists, OuterRef
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
    is_public = request.data.get('is_public', False)

    testNotebook = Notebook.objects.filter(user_creator = user, title = title)
    if testNotebook:
        return Response({"title": "You already have a notebook with this name. Please choose a different name."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        notebook = Notebook.objects.create(
            title = title,
            color = color,
            user_creator = user,
            public_access = is_public
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

    testNotebook = Notebook.objects.filter(team_creator = team, title = title)
    if testNotebook:
        return Response({"title": "This team already has a notebook with this name. Please choose a different name."}, status=status.HTTP_400_BAD_REQUEST)

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
        
@api_view(['GET'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_public_notebooks(request):
    user = request.user
    search_entry = request.query_params.get("search_entry", None)
    major_id = request.query_params.get('major_id', None)
    course_id = request.query_params.get('course_id', None)

    if major_id and course_id:
        return Response({"error": "Can't search according to major and course simultaneously."}, status=status.HTTP_400_BAD_REQUEST)
    
    query = Q()
    if search_entry:
        query &= Q(title__icontains=search_entry)
    if course_id: 
        query &= Q(courses__id=course_id)
    if major_id:
        query &= Q(courses__major__id=major_id)

    query &= Q(public_access=True)

    notebooks = (
        Notebook.objects.filter(query)
        .annotate(is_bookmarked=Exists(
            Notebook.bookmark_users.through.objects.filter(
                notebook_id=OuterRef('pk'),
                user_id=user.id
            )
        ))
        .order_by('title')
    )

    serialized_notebooks = NotebookSerializer(notebooks, many=True).data
    return Response(serialized_notebooks, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_my_notebooks(request):
    search_entry = request.query_params.get("search_entry", None)
    major_id = request.query_params.get('major_id', None)
    course_id = request.query_params.get('course_id', None)

    if major_id and course_id:
        return Response({"error": "Can't search according to major and course simultaneously."}, status=status.HTTP_400_BAD_REQUEST)
    
    query = Q()
    if search_entry:
        query &= Q(title__icontains=search_entry)
    if course_id: 
        query &= Q(courses__id=course_id)
    if major_id:
        query &= Q(courses__major__id=major_id)
    query &= Q(user_creator=request.user)

    notebooks = Notebook.objects.filter(query).order_by('title')
    return Response(NotebookSerializer(notebooks, many=True).data, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_team_notebooks(request):
    team_id = request.query_params.get('team_id', None)
    search_entry = request.query_params.get('search_entry', None)

    if not team_id:
        return Response({"error": "team_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        return Response({"error": "Invalid team_id provided."}, status=status.HTTP_400_BAD_REQUEST)

    if not team.members.filter(id=request.user.id).exists():
        return Response({"error": "Unauthorized access. User is not part of this team."}, status=status.HTTP_403_FORBIDDEN)

    notebooks = Notebook.objects.filter(team_creator=team.id, title__icontains=search_entry)

    serializer = NotebookSerializer(notebooks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_bookmark_notebook(request):
    user = request.user
    notebook_id = request.data.get('notebook_id')

    try:
        notebook = Notebook.objects.get(id = notebook_id)
    except:
        return Response({"error": "Invalid notebook id provided."}, status = status.HTTP_400_BAD_REQUEST)
    
    if notebook.public_access is True:
        notebook.bookmark_users.add(user)
        return Response("Notebook successfully bookmarked", status = status.HTTP_201_CREATED)
    
    return Response({"error": "The notebook you provided is private."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_unboomark_notebook(request):
    notebook_id = request.query_params.get('notebook_id')
    try:
        notebook = Notebook.objects.get(id = notebook_id)
    except:
        return Response({"error": "Invalid notebook_id provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    notebook.bookmark_users.remove(request.user)

    return Response("Successfully unbookmarked notebook.", status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_bookmarked_notebooks(request):
    user = request.user
    search_entry = request.query_params.get('search_entry')
    notebooks = Notebook.objects.filter(bookmark_users=user, title__icontains=search_entry)
    
    serializer = NotebookSerializer(notebooks, many = True)

    return Response(serializer.data, status=status.HTTP_200_OK)


    