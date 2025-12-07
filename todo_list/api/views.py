from todo_list.models import Subtask, Task
from .serializers import TaskItemSerializer, SubtaskSerializer
from .throttling import TaskThrottle
from rest_framework.response import Response
from rest_framework import permissions, serializers, status, generics


class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/tasks/        -> list of tasks
    POST /api/tasks/        -> create new task (with members + subtasks)
    """
    queryset = Task.objects.all()

    serializer_class = TaskItemSerializer
    throttle_classes = [TaskThrottle]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/tasks/<id>/ -> retrieve single task
    PUT    /api/tasks/<id>/ -> partial update (title, status, members, subtasks, ...)
    PATCH  /api/tasks/<id>/ -> partial update
    DELETE /api/tasks/<id>/ -> delete task
    """
    queryset = Task.objects.all()
    serializer_class = TaskItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [TaskThrottle]

    def update(self, request, *args, **kwargs):
        """
        Правим всички обновявания partial (като стария ти код),
        за да не чупим frontend-а, който праща само част от полетата.
        """
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)


# ==========================
# SUBTASK VIEWS
# ==========================
class SubtaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/subtasks/     -> list of all subtasks (ако изобщо ти трябва)
    POST /api/subtasks/     -> create subtask for given task (payload-а съдържа task id)
    """
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [TaskThrottle]

    def perform_create(self, serializer):
        """
        В стария код:
            - task_id идваше от request.data["task"]
            - SubtaskSerializer НЯМА поле task => подаваме го ръчно
        Запазваме същото поведение тук.
        """
        task_id = self.request.data.get("task")
        if not task_id:
            raise serializers.ValidationError({"task": "Task ID is required."})

        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            raise serializers.ValidationError({"task": "Task not found."})

        serializer.save(task=task)


class SubtaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/subtasks/<id>/ -> retrieve single subtask
    PUT    /api/subtasks/<id>/ -> partial update
    PATCH  /api/subtasks/<id>/ -> partial update
    DELETE /api/subtasks/<id>/ -> delete subtask
    """
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [TaskThrottle]

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"deleted": True}, status=status.HTTP_200_OK)
