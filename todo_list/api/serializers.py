from django.db import transaction
from rest_framework import serializers

from todo_list.models import Task, Subtask
from user_auth_app.models import UserProfile
from user_auth_app.api.serializers import UserProfileSerializer


class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ['id', 'title', 'status']


class TaskItemSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(),
        many=True,
    )
    subtasks = SubtaskSerializer(many=True)
    subtasks_progress = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'category', 'description', 'status',
            'color', 'priority', 'members', 'created_at', 'due_date',
            'checked', 'subtasks', 'subtasks_progress',
        ]

    def create(self, validated_data):
        subtasks_data = validated_data.pop('subtasks', [])
        members = validated_data.pop('members', [])

        with transaction.atomic():
            task = Task.objects.create(**validated_data)
            task.members.set(members)

            for subtask_data in subtasks_data:
                Subtask.objects.create(task=task, **subtask_data)

        return task

    def update(self, instance, validated_data):
        subtasks_data = validated_data.pop('subtasks', None)
        members_data = validated_data.pop('members', None)

        self.update_task(instance, validated_data)

        if members_data is not None:
            self.update_members(instance, members_data)

        if subtasks_data is not None:
            self.update_subtasks(instance, subtasks_data)

        return instance

    def update_task(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

    def update_members(self, instance, members_data):
        instance.members.set(members_data)

    def update_subtasks(self, instance, subtasks_data):
        existing_subtasks = {
            subtask.id: subtask for subtask in instance.subtasks.all()
        }

        for subtask_data in subtasks_data:
            subtask_id = subtask_data.get('id')

            if subtask_id and subtask_id in existing_subtasks:
                subtask = existing_subtasks.pop(subtask_id)
                for attr, value in subtask_data.items():
                    setattr(subtask, attr, value)
                subtask.save()
            else:
                Subtask.objects.create(task=instance, **subtask_data)

        for subtask in existing_subtasks.values():
            subtask.delete()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['members'] = UserProfileSerializer(
            instance.members.all(), many=True
        ).data
        return representation
