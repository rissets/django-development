from rest_framework import serializers

from apps.projects.models import Project
from apps.projects.services import create_project, update_project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "name", "status", "created_at", "updated_at")
        read_only_fields = ("id", "status", "created_at", "updated_at")

    def create(self, validated_data):
        return create_project(actor=self.context["request"].user, **validated_data)

    def update(self, instance, validated_data):
        return update_project(
            actor=self.context["request"].user,
            project_id=instance.pk,
            name=validated_data.get("name", instance.name),
        )


class ProjectQuerySerializer(serializers.Serializer):
    q = serializers.CharField(required=False, max_length=120)
    status = serializers.ChoiceField(required=False, choices=Project.Status.choices)
