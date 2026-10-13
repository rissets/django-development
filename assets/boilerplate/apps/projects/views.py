from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import ProjectFilterForm, ProjectForm
from .models import Project
from .services import create_project, transition_project, update_project


@login_required
@require_GET
def project_list(request):
    filters = ProjectFilterForm(request.GET)
    queryset = Project.objects.visible_to(request.user)
    if filters.is_valid():
        if filters.cleaned_data["q"]:
            queryset = queryset.filter(name__icontains=filters.cleaned_data["q"])
        if filters.cleaned_data["status"]:
            queryset = queryset.filter(status=filters.cleaned_data["status"])
    else:
        queryset = queryset.none()
    page = Paginator(queryset, 25).get_page(request.GET.get("page"))
    query = request.GET.copy()
    query.pop("page", None)
    return render(
        request,
        "projects/list.html",
        {"page_obj": page, "filters": filters, "filter_query": urlencode(query)},
    )


@login_required
@require_GET
def project_detail(request, pk):
    project = get_object_or_404(Project.objects.visible_to(request.user), pk=pk)
    return render(request, "projects/detail.html", {"project": project})


@login_required
@require_http_methods(["GET", "POST"])
def project_form(request, pk=None):
    project = get_object_or_404(Project.objects.visible_to(request.user), pk=pk) if pk else None
    form = ProjectForm(request.POST if request.method == "POST" else None, instance=project)
    if request.method == "POST" and form.is_valid():
        try:
            if project:
                saved = update_project(
                    actor=request.user, project_id=project.pk, name=form.cleaned_data["name"]
                )
            else:
                saved = create_project(actor=request.user, name=form.cleaned_data["name"])
        except Project.DoesNotExist as error:
            raise Http404 from error
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Proyek berhasil disimpan.")
            return redirect("projects:detail", pk=saved.pk)
    return render(request, "projects/form.html", {"form": form, "project": project})


@login_required
@require_POST
def project_transition(request, pk, target):
    try:
        transition_project(actor=request.user, project_id=pk, target=target)
    except Project.DoesNotExist as error:
        raise Http404 from error
    except ValidationError as error:
        messages.error(request, " ".join(error.messages))
    else:
        messages.success(request, "Status proyek berhasil diperbarui.")
    return redirect("projects:detail", pk=pk)
