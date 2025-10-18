from rest_framework import serializers
from todo_list.models import Subtask, Task
from user_auth_app.models import UserProfile
from user_auth_app.api.serializers import UserProfileSerializer

"""
Serializers for task and subtask entities in the todo_list application.
This module provides nested serialization and custom create/update logic
for Task instances that include:
    - Many-to-many member (UserProfile) assignments
    - Inline creation, update, and deletion of related Subtask instances
    - Enriched output representation of members via UserProfileSerializer
"""


class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ['id', 'title', 'status']


class TaskItemSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(), many=True)
    subtasks = SubtaskSerializer(many=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'category', 'description', 'status',
            'color', 'priority', 'members', 'created_at', 'due_date',
            'checked', 'subtasks', 'subtasks_progress'
        ]

    def create(self, validated_data):
        subtasks_data = validated_data.pop('subtasks', [])
        members_data = validated_data.pop('members', [])

        member_ids = [member.id for member in members_data]

        for member_id in member_ids:
            if not UserProfile.objects.filter(id=member_id).exists():
                raise serializers.ValidationError(
                    f"UserProfile with ID {member_id} does not exist."
                )

        task = Task.objects.create(**validated_data)

        members = UserProfile.objects.filter(id__in=member_ids)
        task.members.set(members)

        for subtask_data in subtasks_data:
            Subtask.objects.create(task=task, **subtask_data)

        return task

    def update(self, instance, validated_data):
        subtasks_data = validated_data.pop('subtasks', [])
        members_data = validated_data.pop('members', [])

        self.update_task(instance, validated_data)
        self.update_members(instance, members_data)
        self.update_subtasks(instance, subtasks_data)

        return instance

    def update_task(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

    def update_members(self, instance, members_data):
        if members_data:
            member_ids = [member.id for member in members_data]
            for member_id in member_ids:
                if not UserProfile.objects.filter(id=member_id).exists():
                    raise serializers.ValidationError(
                        f"UserProfile with ID {member_id} does not exist."
                    )
            instance.members.set(UserProfile.objects.filter(id__in=member_ids))

    def update_subtasks(self, instance, subtasks_data):
        if subtasks_data:
            existing_subtasks = {
                subtask.id: subtask for subtask in instance.subtasks.all()}
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
            instance.members.all(), many=True).data
        return representation
