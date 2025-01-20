from django.urls import path
from . import views

urlpatterns = [
    path("questions/", views.handle_questions, name="handle_questions"),
    path("question-1/", views.question_1, name="question_1"),
    path("question-2/", views.question_2, name="question_2"),
    path("question-3/", views.question_3, name="question_3"),
    path("", views.index, name="index"),  # Points to the index view),
]
