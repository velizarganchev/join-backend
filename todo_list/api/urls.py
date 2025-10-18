from django.contrib import admin
from django.urls import path, include

from todo_list.api.views import Task_View, Subtask_View

"""
URL configuration for the todo_list API.
This module defines REST-style endpoints for Task and Subtask resources, mapping
HTTP requests to their respective class-based views:
Routes:
    tasks/                  -> Task_View (collection endpoint: list, create)
    tasks/<int:task_id>/    -> Task_View (detail endpoint: retrieve, update, delete)
    subtask/                -> Subtask_View (collection endpoint: list, create)
    subtask/<int:subtask_id>/ -> Subtask_View (detail endpoint: retrieve, update, delete)
Each view is expected to implement the appropriate HTTP method handlers (e.g.,
get, post, put/patch, delete) for operating on Task and Subtask objects.
Naming:
    task-list, task-detail, subtask-list, subtask-detail
facilitate reverse URL resolution within the Django application.
"""


urlpatterns = [
    path('tasks/', Task_View.as_view(), name='task-list'),
    path('tasks/<int:task_id>/', Task_View.as_view(), name='task-detail'),
    path('subtask/', Subtask_View.as_view(), name='subtask-list'),
    path('subtask/<int:subtask_id>/',
         Subtask_View.as_view(), name='subtask-detail'),
]
