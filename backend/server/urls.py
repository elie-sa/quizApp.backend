from django.urls import path
from . import views, views_auth, views_notebook, views_teams, views_elements, admin
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Authentication APIs
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup', views_auth.signup, name="signup"),
    path('login', views_auth.login, name="login"),
    path('user/confirmEmail', views_auth.confirm_email_view, name="confirm_email_view"),
    path('user/sendConfirmationEmail', views_auth.create_email_token, name = "send_confirmation_email"),
    # Forgot Password APIs
    path('user/forgotPassword', views_auth.forgot_password, name="check_email"),
    path('user/verifyOtp', views_auth.verify_otp, name="verify_otp"),
    path('user/changeForgottenPassword', views_auth.change_forgotten_password, name="change_forgotten_password"),

    # GET APIs
    path('majors', views.get_majors, name="get_majors"),
    path('courses', views.get_courses, name="get_courses"),

    # Notebook APIs
    #POST
    path('user/createNotebook', views_notebook.user_create_notebook, name="user_create_notebook"),
    path('user/bookmarkNotebook', views_notebook.user_bookmark_notebook, name = "user_bookmark_notebook"),
    path('team/createNotebook', views_notebook.team_create_notebook, name="team_create_notebook"),
    #GET
    path('user/notebooks', views_notebook.get_public_notebooks, name="get_public_notebooks"),
    path('user/myNotebooks', views_notebook.get_my_notebooks, name="get_my_notebooks"),
    path('user/bookmarkedNotebooks', views_notebook.get_bookmarked_notebooks, name="get_bookmarked_notebooks"), 
    path('team/notebooks', views_notebook.get_team_notebooks, name="get_team_notebooks"),  

    # Teams
    path('user/createTeam', views_teams.create_team, name="create_team"),
    path('user/teams', views_teams.get_my_teams, name="get_my_teams"),

    # Elements
    path('createFlashDeck', views_elements.create_flashdeck, name="create_flashdeck"),
    path('deleteFlashDeck/<flashdeck_id>', views_elements.delete_flashdeck, name="delete_flashdeck"),
    path('createFlashCard', views_elements.create_flashcard, name="create_flashcard"),
    path('deleteFlashCard/<flashcard_id>', views_elements.delete_flashcard, name="delete_flashcard"),

    # GET
    path('notebook/elements', views_elements.get_elements, name="get_elements"),
    path('flashdeck/flashcards', views_elements.get_flashcards, name = "get_flashcards"),

    # Quizzes
    path('createQuiz', views_elements.create_quiz, name = "create_quiz"),
    path('quiz/createMCQ', views_elements.create_mcq_question, name = "create_mcq_question"),
    path('quiz/createTorF', views_elements.create_boolean_question, name = "create_boolean_questions"),
    path('quiz/deleteQuestion', views_elements.delete_question, name = "delete_question"),
    path('deleteQuiz', views_elements.delete_quiz, name = "delete_quiz"),
    path('quiz/questions', views_elements.get_quiz_questions, name = "get_quiz_questions"),

    # Notes
    path('create_note/', views_elements.create_note, name='create_note'),
    path('notes/delete', views_elements.delete_note, name = "delete_note"),

    # Testing
    path('', views.index, name='index'),

    # Rating system
    
]
