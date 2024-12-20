from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Course, Major, Notebook, Rating, Team, FlashDeck, FlashCard, Note, Quiz, McqQuestion, McqAnswer, BooleanQuestion
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
    
    
# Quizzes
@api_view(['POST'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_quiz(request):
    notebook_id = request.data['notebook_id']

    try:
        notebook = Notebook.objects.get(id = notebook_id)
    except:
        return Response("Invalid notebook id", status=status.HTTP_400_BAD_REQUEST)

    quizzes = Quiz.objects.filter(title=request.data['title'])
    if quizzes:
        return Response("The quiz name you provided already exists", status=status.HTTP_400_BAD_REQUEST)

    try:
        Quiz.objects.create(
            title = request.data['title'],
            questionTime = request.data['time'],
            difficulty = request.data['difficulty'],
            notebook = notebook
        )
    except:
        return Response({"error":"Invalid body parameters provided."}, status = status.HTTP_400_BAD_REQUEST)
    
    return Response({"message": "Successfully created quiz."}, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_mcq_question(request):
    try:
        quiz = Quiz.objects.get(id=request.data.get('quiz_id'))
    except:
        return Response("Invalid quiz id provided.", status=status.HTTP_400_BAD_REQUEST)
    
    created_question = McqQuestion.objects.create(
        question = request.data.get('question'),
        points = request.data.get('points'),
        quiz = quiz
    )

    possible_answers = request.data.get('possible_answers', [])
    if not isinstance(possible_answers, list):
        return Response({"error": "Possible answers must be a list."}, status=status.HTTP_400_BAD_REQUEST)

    for answer_data in possible_answers:
        answer_text = answer_data.get('answer')
        is_correct = answer_data.get('isCorrect')
        if answer_text is not None and is_correct is not None:
            McqAnswer.objects.create(
                mcq_question=created_question,
                answer=answer_text,
                isCorrect=is_correct
            )
        else:
            return Response({"error": "Each possible answer must include 'answer' and 'isCorrect' fields."},
                            status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Question and possible answers created successfully."}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_boolean_question(request):
    try:
        quiz = Quiz.objects.get(id=request.data.get('quiz_id'))
    except:
        return Response("Invalid quiz id provided.", status=status.HTTP_400_BAD_REQUEST)
    
    try:
        BooleanQuestion.objects.create(
            quiz = quiz,
            question = request.data.get('question'),
            answer = request.data.get('answer'),
            points = request.data.get('points'),
        )
    except:
        return Response("Missing or Incorrect body parameters", status=status.HTTP_400_BAD_REQUEST)
    
    return Response("Created Boolean Question Correctly", status=status.HTTP_200_OK)


@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_question(request):
    question_id = request.query_params.get('question_id')
    question_type = request.query_params.get('question_type')
    
    if not question_id or not question_type:
        return Response({"error": "Both 'question_id' and 'question_type' must be provided."}, 
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        if question_type == "boolean":
            question = BooleanQuestion.objects.get(id=question_id)
        elif question_type == "mcq":
            question = McqQuestion.objects.get(id=question_id)
        else:
            return Response({"error": "Invalid question type. Must be 'boolean' or 'mcq'."}, 
                            status=status.HTTP_400_BAD_REQUEST)
    except (BooleanQuestion.DoesNotExist, McqQuestion.DoesNotExist):
        return Response({"error": "Invalid question ID."}, status=status.HTTP_400_BAD_REQUEST)

    question.delete()
    return Response({"message": "Question deleted successfully."}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_quiz(request):
    quiz_id = request.query_params.get('quiz_id')
    
    if not quiz_id:
        return Response({"error": "The 'quiz_id' parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        return Response({"error": "Invalid quiz ID. Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
    
    quiz.delete()
    return Response({"message": "Quiz deleted successfully."}, status=status.HTTP_200_OK)

from random import shuffle

@api_view(['GET'])
@authentication_classes([SessionAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_quiz_questions(request):
    quiz_id = request.query_params.get('quiz_id')

    if not quiz_id:
        return Response({"error": "The 'quiz_id' parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        return Response({"error": "Invalid quiz ID. Quiz not found."}, status=status.HTTP_404_NOT_FOUND)

    mcq_questions = McqQuestion.objects.filter(quiz=quiz)
    mcq_data = []

    for mcq in mcq_questions:
        possible_answers = McqAnswer.objects.filter(mcq_question=mcq)
        answers_data = [
            {"answer": answer.answer, "is_correct": answer.isCorrect}
            for answer in possible_answers
        ]
        
        mcq_data.append({
            "type": "mcq",
            "id": mcq.id,
            "question": mcq.question,
            "points": mcq.points,
            "answers": answers_data 
        })

    boolean_questions = BooleanQuestion.objects.filter(quiz=quiz)
    boolean_data = [
        {
            "type": "boolean",
            "id": boolean.pk,
            "question": boolean.question,
            "points": boolean.points,
            "is_true": boolean.answer
        }
        for boolean in boolean_questions
    ]

    all_questions = mcq_data + boolean_data
    shuffle(all_questions)

    return Response(all_questions, status=status.HTTP_200_OK)
