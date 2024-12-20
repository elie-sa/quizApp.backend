from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Course, Major, Notebook, Rating, Team, FlashDeck, FlashCard, Note, Quiz
from django.db.models import Q
from .serializers import NotebookSerializer, FlashCardSerializer
from rest_framework import status

# Flashdeck
@api_view(['POST'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_flashdeck(request):
    notebook_id = request.data['notebook_id']
    title = request.data['title']

    duplicateFlashDecks = FlashDeck.objects.filter(title = title, notebook = Notebook.objects.get(id = notebook_id))
    if duplicateFlashDecks:
        return Response("A flashdeck with this name already exists.", status = status.HTTP_400_BAD_REQUEST)

    try:
        FlashDeck.objects.create(
            title = title,
            notebook = Notebook.objects.get(id = notebook_id)
        )
    except:
        return Response("Invalid body parameters.")
    
    return Response(f"Successfully created flashdeck: {title}.", status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_flashdeck(request, flashdeck_id):
    try:
        flashdeck = FlashDeck.objects.get(id=flashdeck_id)
    except:
        return Response("Invalid flashdeck_id provided", status=status.HTTP_400_BAD_REQUEST)

    flashdeck.delete()
    return Response("The flashdeck has been successfully deleted.", status = status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_flashcard(request):
    flashdeck_id = request.data['flashdeck_id']
    try:
        flashdeck = FlashDeck.objects.get(id = flashdeck_id)
    except:
        return Response("Flashdeck ID invalid.", status=status.HTTP_400_BAD_REQUEST)

    try:
        FlashCard.objects.create(
            title = request.data['title'],
            question = request.data['question'],
            answer = request.data['answer'],
            difficulty = request.data['difficulty'],
            deck = flashdeck
        )
    except:
        return Response({"error":"Invalid body parameters provided."}, status = status.HTTP_400_BAD_REQUEST)
    
    return Response({"message": "Successfully created flashcard."}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_flashcard(request, flashcard_id):
    try:
        flashcard = FlashCard.objects.get(id=flashcard_id)
    except FlashCard.DoesNotExist:
        return Response({"error": "Flashcard not found."}, status=status.HTTP_404_NOT_FOUND)
    
    flashcard.delete()
    return Response({"message": "Flashcard successfully deleted."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_elements(request):
    notebook_id = request.query_params.get('notebook_id')
    try:
        notebook = Notebook.objects.get(id=notebook_id)
    except:
        return Response("Invalid notebook_id", status=status.HTTP_400_BAD_REQUEST)
    
    flashdecks = FlashDeck.objects.filter(notebook=notebook)
    quizzes = Quiz.objects.filter(notebook=notebook)
    notes = Note.objects.filter(notebook=notebook)

    flashdecks_data = [
        {
            "id": flashdeck.id,
            "title": flashdeck.title,
        }
        for flashdeck in flashdecks
    ]

    quizzes_data = [
        {
            "id": quiz.id,
            "name": quiz.name,
            "time": quiz.questiontime
        }
        for quiz in quizzes
    ]

    notes_data = [
        {
            "id": note.id,
            "title": note.title
        }
        for note in notes
    ]

    response_data = {
        "FlashDecks": flashdecks_data,
        "Quizzes": quizzes_data,
        "Notes": notes_data,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_flashcards(request):
    flashdeck_id = request.query_params.get('flashdeck_id')
    try:
        flashdeck = FlashDeck.objects.get(id=flashdeck_id)
    except:
        return Response({"error": "Invalid or Missing flashdeck_id"}, status=status.HTTP_400_BAD_REQUEST)
    
    flashcards = FlashCard.objects.filter(deck = flashdeck)

    serializer = FlashCardSerializer(flashcards, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
    
