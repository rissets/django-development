# Contoh struktur kode yang terhubung

Contoh ini melanjutkan startup `apps.projects` dan custom user pada [getting started](getting-started.md). Workflow: actor login membuat proyek miliknya, melihat daftar/detail JSON, dan mengaktifkannya melalui use case yang sama dengan action staf. Ini single-owner example, bukan implementasi multi-tenant. Superuser memiliki global grant eksplisit untuk contoh; production menggantinya dengan policy yang disepakati.

## Model dan scope

`apps/projects/models.py`:

```python
from django.conf import settings
from django.db import models


class ProjectQuerySet(models.QuerySet):
    def visible_to(self, actor):
        if not actor.is_authenticated or not actor.is_active:
            return self.none()
        if actor.is_superuser:
            return self
        return self.filter(owner=actor)


class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=120)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ProjectQuerySet.as_manager()

    class Meta:
        ordering = ("-created_at", "-pk")
        constraints = [
            models.CheckConstraint(condition=~models.Q(name=""), name="project_name_present"),
            models.CheckConstraint(
                condition=models.Q(status__in=["draft", "active", "archived"]),
                name="project_status_valid",
            ),
        ]

    def __str__(self):
        return self.name
```

Timestamps/order/constraint dibuat karena berguna pada workflow. Tambahkan tenant, business uniqueness, audit event, dan index hanya sesuai requirements. UUID/public identifier tidak menggantikan scoping.

## Workflow shared

`apps/projects/services.py`:

```python
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from .models import Project


def create_project(*, actor, name: str) -> Project:
    if not actor.is_authenticated or not actor.is_active:
        raise PermissionDenied
    project = Project(owner=actor, name=name.strip())
    project.full_clean()
    project.save()
    return project


@transaction.atomic
def activate_project(*, actor, project_id: int) -> Project:
    if not actor.is_authenticated or not actor.is_active:
        raise PermissionDenied
    project = Project.objects.visible_to(actor).select_for_update().get(pk=project_id)
    if project.status == Project.Status.ACTIVE:
        return project
    if project.status != Project.Status.DRAFT:
        raise ValidationError("Hanya proyek draft yang dapat diaktifkan.")
    project.status = Project.Status.ACTIVE
    project.full_clean()
    project.save(update_fields=["status", "updated_at"])
    return project
```

Service independen dari request/template/serializer/admin. Caller memetakan `Project.DoesNotExist` ke 404/denial sesuai kontraknya. Lock row melindungi transition; SQLite tidak membuktikan lock PostgreSQL. Jika aktivasi memerlukan email/job, dispatch setelah commit dengan mekanisme delivery sesuai kebutuhan. Jangan menambahkan dummy queue/email ke contoh tanpa requirement.

## HTML adapter

`apps/projects/forms.py`:

```python
from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name",)
```

`apps/projects/views.py`:

```python
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import ProjectForm
from .models import Project
from .services import create_project


@login_required
def project_list(request):
    projects = Project.objects.visible_to(request.user).select_related("owner")[:50]
    return render(request, "projects/list.html", {"projects": projects})


@login_required
@require_http_methods(["GET", "POST"])
def project_create(request):
    form = ProjectForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            create_project(actor=request.user, name=form.cleaned_data["name"])
        except ValidationError as error:
            form.add_error(None, error)
        else:
            return redirect("projects:list")
    return render(request, "projects/form.html", {"form": form})
```

List dibatasi untuk contoh; product list gunakan paginator/URL state pada [fullstack](fullstack.md). HTML `form.save()` tidak digunakan karena contoh menempatkan create pada shared service. ModelForm tetap memberi parsing/error feedback dan service menjaga invariant untuk caller lain.

`apps/projects/urls.py`:

```python
from django.urls import path
from . import views

app_name = "projects"
urlpatterns = [
    path("", views.project_list, name="list"),
    path("new/", views.project_create, name="create"),
]
```

`apps/projects/templates/projects/form.html`:

```django
{% extends "base.html" %}
{% block content %}
<h1>Buat proyek</h1>
<form method="post">
  {% csrf_token %}
  {{ form.non_field_errors }}
  {{ form.as_div }}
  <button type="submit">Simpan proyek</button>
</form>
{% endblock %}
```

`list.html` menggunakan loop projects, nama yang autoescaped, empty message, dan link `{% url "projects:create" %}`. `base.html` menyediakan block content dan CSS sesuai design system. Login template dan auth URLs harus disediakan dari startup sebelum menguji user flow.

## API adapter tanpa jalur edit status bebas

`apps/projects/api/serializers.py`:

```python
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from apps.projects.models import Project
from apps.projects.services import create_project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "name", "status", "created_at")
        read_only_fields = ("id", "status", "created_at")

    def create(self, validated_data):
        try:
            return create_project(actor=self.context["request"].user, **validated_data)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages) from error
```

`apps/projects/api/views.py`:

```python
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema

from apps.projects.models import Project
from apps.projects.services import activate_project
from .serializers import ProjectSerializer


class ProjectViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectSerializer
    queryset = Project.objects.none()

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Project.objects.none()
        return Project.objects.visible_to(self.request.user)

    @extend_schema(request=None, responses={200: ProjectSerializer})
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        project = self.get_object()
        try:
            project = activate_project(actor=request.user, project_id=project.pk)
        except Project.DoesNotExist as error:
            raise NotFound from error
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages) from error
        return Response(self.get_serializer(project).data)
```

Konfigurasi DRF membatasi pagination; router register memakai `basename="project"`. `config/urls.py` mount HTML dengan `include("apps.projects.urls")`, API dengan router URLs, account URLs sesuai mode, dan admin. Annotate activation request empty/response/errors pada spectacular sesuai kontrak; serializer status read-only tidak berarti arbitrary mutation action otomatis aman.

## Unfold adapter

Model admin menggunakan `unfold.admin.ModelAdmin`, scoped `get_queryset()`, readonly owner/status/timestamps, search/filter yang diperlukan, dan object checks. Pada add, owner ditetapkan server sebelum validasi/save. Untuk create yang perlu side effects, buat form/view yang memanggil shared create workflow; jangan berasumsi `save_model()` sama dengan create service.

Selected bulk activation: action mengecek Django change permission per object, kemudian memanggil `activate_project` untuk setiap ID dari queryset authorized. Tentukan atomic-all atau partial success secara eksplisit; partial mode menampilkan sukses/kegagalan per jumlah, atomic mode rollback seluruh batch. Row/detail actions melakukan recheck yang sama. **Jangan mengubah status lewat `queryset.update()`** jika service transition/audit wajib berjalan.

Admin user dengan global Django model permission tetapi bukan owner tetap tidak dapat mengakses object bila policy contoh membatasinya. Jika operator memerlukan grant lebih luas, ubah policy secara sadar dan uji semua adapters, bukan hanya sidebar.

## Verification yang bermakna

1. Anonymous HTML diarahkan ke login; API ditolak sesuai auth scheme.
2. Actor A create valid/invalid; owner server-assigned dan status draft.
3. Actor B tidak menemukan project A di list/detail/action.
4. Aktivasi draft menjadi active; ulang active menjadi no-op; archived ditolak.
5. Concurrent activation diuji pada engine produksi jika concurrency requirement penting.
6. Admin ordinary staff mengikuti policy; object/state tidak dapat diubah lewat field/action yang tidak berhak.
7. Schema mengungkap kontrak sebenarnya dan UI menunjukkan persisted result.

Contoh ini melatih boundary dan flow; tidak menyediakan semua template/route/provider untuk produk jadi. Ikuti acceptance aplikasi dan tambahkan edit/delete/tenant/audit hanya bila diminta.
