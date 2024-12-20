from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Course, Major
from django.db.models import Q
from .serializers import MajorSerializer

@api_view(['GET'])
def get_majors(request):
    majors = Major.objects.all().order_by('name')
    major_data = []
    for major in majors:
        num_courses = major.courses.count()
        serializer = MajorSerializer(major)
        major_info = serializer.data
        major_info['num_courses'] = num_courses
        major_data.append(major_info)
    return Response(major_data)    

@api_view(['GET'])
def get_courses(request):
    major_id = request.query_params.get('major_id', None)
    search_entry = request.query_params.get('search_entry', None)

    query = Q()
    if major_id:
        query &= Q(major_id=major_id)
    if search_entry:
        query &= Q(name__icontains=search_entry)
    
    courses = Course.objects.filter(query).order_by('name')

    course_data = []
    for course in courses:
        major_name = course.major.name
        course_code = f"{course.major.code}{course.code}"
        
        course_info = {
            "id": course.id,
            "name": course.name,
            "major": major_name,
            "code": course_code,
        }
        course_data.append(course_info)

    return Response(course_data)

from django.shortcuts import render

def index(request):
    return render(request, 'upload_note.html')