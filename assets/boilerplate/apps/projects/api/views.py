from django.http import Http404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.projects.models import Project
from apps.projects.services import transition_project

from .serializers import ProjectQuerySerializer, ProjectSerializer

TRANSITION_RESPONSES = {
    200: ProjectSerializer,
    400: OpenApiResponse(OpenApiTypes.OBJECT, description="Perubahan status tidak valid."),
    403: OpenApiResponse(OpenApiTypes.OBJECT, description="Identity atau CSRF ditolak."),
    404: OpenApiResponse(OpenApiTypes.OBJECT, description="Proyek tidak ada pada scope actor."),
}


class ProjectViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Project.objects.none()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Project.objects.none()
        return Project.objects.visible_to(self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter("q", str, description="Pencarian nama, maksimal 120 karakter."),
            OpenApiParameter("status", str, enum=["draft", "active", "archived"]),
        ]
    )
    def list(self, request, *args, **kwargs):
        query = ProjectQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        queryset = self.get_queryset()
        if query.validated_data.get("q"):
            queryset = queryset.filter(name__icontains=query.validated_data["q"])
        if query.validated_data.get("status"):
            queryset = queryset.filter(status=query.validated_data["status"])
        page = self.paginate_queryset(queryset)
        return self.get_paginated_response(self.get_serializer(page, many=True).data)

    def _transition(self, request, target):
        project = self.get_object()
        try:
            updated = transition_project(actor=request.user, project_id=project.pk, target=target)
        except Project.DoesNotExist as error:
            raise Http404 from error
        return Response(self.get_serializer(updated).data)

    @extend_schema(request=None, responses=TRANSITION_RESPONSES)
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        return self._transition(request, Project.Status.ACTIVE)

    @extend_schema(request=None, responses=TRANSITION_RESPONSES)
    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        return self._transition(request, Project.Status.ARCHIVED)
