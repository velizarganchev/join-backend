from django.contrib import admin
from django.urls import path, include

from todo_list.api.views import SubtaskDetailView, TaskListCreateView, TaskDetailView, SubtaskListCreateView

urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='task-list'),
    path('tasks/<int:task_id>/', TaskDetailView.as_view(), name='task-detail'),
    path('subtask/', SubtaskListCreateView.as_view(), name='subtask-list'),
    path('subtask/<int:subtask_id>/',
         SubtaskDetailView.as_view(), name='subtask-detail'),
]
