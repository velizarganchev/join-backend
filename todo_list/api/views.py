from todo_list.models import Subtask, Task
from .serializers import TaskItemSerializer, SubtaskSerializer
from .throttling import TaskThrottle
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, authentication
from rest_framework import generics, status

# Docstring for class Task_View
"""
API view for managing Task instances.
This view supports CRUD operations on Task objects through the following HTTP methods:
- POST: Create a new task.
- GET: Retrieve a single task by ID or list all tasks.
- PUT: Partially update an existing task by ID.
- DELETE: Delete a task by ID.
Permissions:
    - Requires an authenticated user (IsAuthenticated).
Throttling:
    - Uses TaskThrottle to rate-limit task creation and modifications.
Responses:
    - 200 OK: Successful retrieval, update, or deletion (returns updated collection for delete/create).
    - 201 Created: Task successfully created (returns full task list).
    - 400 Bad Request: Validation errors.
    - 404 Not Found: Task with the given ID does not exist.
Notes:
    - PUT operation is implemented as a partial update (partial=True).
    - After creation (POST) or deletion (DELETE), the full list of tasks is returned for client-side state sync.
"""
# Docstring for method Task_View.post
"""
Create a new Task.
Expects a JSON body matching TaskItemSerializer input fields.
Parameters:
    request (Request): The incoming HTTP request containing task data.
    format (str | None): Optional DRF format suffix (unused).
Returns:
    Response: On success (201), returns serialized list of all tasks.
              On validation failure (400), returns serializer errors.
"""
# Docstring for method Task_View.get
"""
Retrieve one Task by ID or list all Tasks.
Parameters:
    request (Request): The incoming HTTP request.
    task_id (int | None): Primary key of the task to retrieve. If omitted or None, all tasks are returned.
    format (str | None): Optional DRF format suffix (unused).
Returns:
    Response:
        - 200 OK with serialized task data (single or list).
        - 404 Not Found if a specific task_id does not exist.
"""
# Docstring for method Task_View.put
"""
Partially update an existing Task.
Parameters:
    request (Request): The incoming HTTP request containing fields to update.
    task_id (int): Primary key of the task to update.
    format (str | None): Optional DRF format suffix (unused).
Returns:
    Response:
        - 200 OK with updated task data.
        - 400 Bad Request with validation errors.
        - 404 Not Found if the task does not exist.
Notes:
    - Uses partial=True allowing partial field updates.
"""
# Docstring for method Task_View.delete
"""
Delete a Task by ID.
Parameters:
    request (Request): The incoming HTTP request.
    task_id (int): Primary key of the task to delete.
    format (str | None): Optional DRF format suffix (unused).
Returns:
    Response:
        - 200 OK with the serialized list of remaining tasks after deletion.
        - 404 Not Found if the task does not exist.
Side Effects:
    - Permanently removes the Task instance from the database.
"""
# Docstring for class Subtask_View
"""
API view for managing Subtask instances associated with Tasks.
Supports CRUD operations on Subtask objects through:
- POST: Create a new subtask for a given task.
- GET: Retrieve a single subtask by ID or list all subtasks.
- PUT: Partially update a subtask.
- DELETE: Delete a subtask.
Responses:
    - 200 OK: Successful retrieval or update.
    - 201 Created: Subtask successfully created.
    - 204 No Content: Successful deletion (returns JSON body with deleted flag).
    - 400 Bad Request: Validation errors.
    - 404 Not Found: Task or Subtask not found.
Notes:
    - Creation requires a valid 'task' field referencing an existing Task.
    - Updates are partial (partial=True).
"""
# Docstring for method Subtask_View.post
"""
Create a new Subtask for a specified Task.
Expects JSON with required Subtask fields, including a 'task' field referencing the parent task ID.
Parameters:
    request (Request): The incoming HTTP request containing subtask data.
    format (str | None): Optional DRF format suffix (unused).
Returns:
    Response:
        - 201 Created with serialized subtask data.
        - 404 Not Found if the referenced Task does not exist.
        - 400 Bad Request with validation errors.
"""
# Docstring for method Subtask_View.get
"""
Retrieve one Subtask by ID or list all Subtasks.
Parameters:
    request (Request): The incoming HTTP request.
    subtask_id (int | None): Primary key of the subtask to retrieve. If None, returns all subtasks.
    format (str | None): Optional DRF format suffix (unused).
Returns:
    Response:
        - 200 OK with serialized subtask (single) or list.
        - 404 Not Found if a specific subtask_id does not exist.
Note:
    - The exception handling for a missing subtask should catch Subtask.DoesNotExist (not Task.DoesNotExist).
"""
# Docstring for method Subtask_View.put
"""
Partially update an existing Subtask.
Parameters:
    request (Request): The incoming HTTP request containing fields to update.
    subtask_id (int): Primary key of the subtask to update.
    format (str | None): Optional DRF format suffix (unused).
Returns:
    Response:
        - 200 OK with updated subtask data.
        - 400 Bad Request with validation errors.
        - 404 Not Found if the subtask does not exist.
"""
# Docstring for method Subtask_View.delete
"""
Delete a Subtask by ID.
Parameters:
    request (Request): The incoming HTTP request.
    subtask_id (int): Primary key of the subtask to delete.
    format (str | None): Optional DRF format suffix (unused).
Returns:
    Response:
        - 204 No Content with {'deleted': True} in the body.
        - 404 Not Found if the subtask does not exist.
Side Effects:
    - Permanently removes the Subtask instance from the database.
"""


class Task_View(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [TaskThrottle]

    def post(self, request, format=None):
        serializer = TaskItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            tasks = Task.objects.all()
            all_tasks_serializer = TaskItemSerializer(tasks, many=True)
            return Response(all_tasks_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, task_id=None, format=None):
        if task_id:
            try:
                task = Task.objects.get(pk=task_id)
                serializer = TaskItemSerializer(task)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Task.DoesNotExist:
                return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            tasks = Task.objects.all()
            serializer = TaskItemSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, task_id, format=None):
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskItemSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            updated_task = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id, format=None):
        try:
            task = Task.objects.get(pk=task_id)
            task.delete()
            tasks = Task.objects.all()
            serializer = TaskItemSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


class Subtask_View(APIView):
    throttle_classes = [TaskThrottle]

    def post(self, request, format=None):
        task_id = request.data.get('task')
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubtaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, subtask_id=None, format=None):
        if subtask_id:
            try:
                subtask = Subtask.objects.get(pk=subtask_id)
                serializer = SubtaskSerializer(subtask)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Task.DoesNotExist:
                return Response({'error': 'Subtask not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            subtasks = Subtask.objects.all()
            serializer = SubtaskSerializer(subtasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, subtask_id, format=None):
        try:
            subtask = Subtask.objects.get(pk=subtask_id)
        except Subtask.DoesNotExist:
            return Response({'error': 'Subtask not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubtaskSerializer(
            subtask, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, subtask_id, format=None):
        try:
            subtask = Subtask.objects.get(pk=subtask_id)
            subtask.delete()
            return Response({'deleted': True}, status=status.HTTP_204_NO_CONTENT)
        except Subtask.DoesNotExist:
            return Response({'error': 'Subtask not found'}, status=status.HTTP_404_NOT_FOUND)
