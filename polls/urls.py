from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.QuestionView.as_view(), name='question'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>', views.UserView.as_view(), name='user'),
    path('<int:pk>/add_comment/', views.CreateCommentView.as_view(), name='add_comment'),
]
