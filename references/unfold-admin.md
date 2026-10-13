# Django Unfold admin

Unfold is the user's required admin standard. Use `django-unfold-admin` when available for maintained detailed recipes. This reference keeps the new skill usable on its own. Do not assume admin is the public customer UI; use purpose-built views where the product workflow requires them.

Panduan lengkap dibagi menjadi [feature map](unfold-feature-map.md) untuk seluruh 80 halaman/topik navigasi, [recipes](unfold-recipes.md) untuk kombinasi workflow, dan [components](unfold-components.md) untuk payload/template visual. Berikut implementasi operasional yang melengkapi inventaris fitur.

Untuk semua 14 package integration families, baca [integrations](unfold-integrations.md): urutan apps, inheritance, domain scope, dan batas capture/recovery/impersonation.

## Setup and compatibility

Inspect installed Django/Unfold, app order, all registered model/inline bases, custom site, auth model, overrides, and static pipeline. `unfold` must precede `django.contrib.admin`. Add only required `unfold.contrib.*` integrations. Default `admin.site.urls` remains valid. Registered styled admins inherit `unfold.admin.ModelAdmin`; styled inlines use Unfold classes. [Quickstart](https://unfoldadmin.com/docs/installation/quickstart/)

Existing third-party admin classes need compatible mixin ordering or deliberate unregister/re-register; do not blindly replace behavior. User/group admin may need explicit re-registration with Unfold auth forms; adapt the documented recipe to `get_user_model()` and the existing custom fields. [Auth models](https://unfoldadmin.com/docs/installation/auth/)

For custom sites use the documented Unfold site/config pattern rather than an arbitrary `AdminSite` that lacks expected routes. Keep branding/settings callbacks compatible with the installed package, not just the current web docs.

## Features chosen by the workflow

| Workflow | Consider |
|---|---|
| Large operational list | Useful columns, select-related, scoped filters/search, bounded pagination |
| Complex edit | Fieldsets/tabs, documented widgets, appropriate inlines/autocomplete |
| Approve/reject/process | Permission-checked action, atomic state transition, meaningful feedback |
| Summary dashboard | Scoped aggregates, period/unit/source, KPI-to-list links, charts only where useful |
| Import/export | Integration recipe, explicit fields, tenant checks, dry-run/validation and audit |
| Audit/recovery | History/reversion integration selected by requirements |
| Custom workflow | Documented custom view with explicit permissions and navigation |

Use Unfold's display/action decorators and compatible filters/components rather than adding unrelated UI libraries. Scope FK/autocomplete choices and inline querysets. Prefer explicit relation lists, not unbounded dropdowns or broad search of every model.

## Permissions are server-side

Model permissions, queryset scope, object checks, actions, custom views, datasets, dashboard callbacks, and exports must agree. Sidebar permission callbacks control visibility only. A staff flag grants access to the admin shell, not automatic access to all domain data.

Custom pages use the documented Unfold view mixin, title, permission requirements, and `admin_site.admin_view` wrapping where appropriate. Named admin URLs use `reverse()`/`reverse_lazy()`; navigation entry is a separate step. Test a normal staff role and direct URL access, not only superuser navigation. [Custom pages](https://unfoldadmin.com/docs/configuration/custom-pages/)

Dashboard callback receives request/context. Aggregate the authorized scope before rendering, define date ranges, bound operational tables, and link KPI counts to matching filtered records. Do not create broad global metrics and merely hide the panel. [Dashboard](https://unfoldadmin.com/docs/configuration/dashboard/)

## Design and assets

Preserve existing product/admin design. Map branding to documented `UNFOLD` settings, semantic light/dark colors, navigation, and static assets. Settings shape/color syntax can change with Unfold versions. [Settings](https://unfoldadmin.com/docs/configuration/settings/)

Reuse documented cards, tables, charts, links, buttons, progress, Tracker/Cohort where their meaning fits. Verify required context/data shape against installed component templates; do not invent a component or reuse Tracker for an unrelated workflow diagram. [Components](https://unfoldadmin.com/docs/components/introduction/)

For Unfold 0.56+, official guidance recommends custom CSS for simple additions; the docs distinguish Tailwind 4 for 0.57+ from old Tailwind 3 setup. Do not paste old Tailwind configuration into a newer admin. Keep public frontend CSS scoped/separate to avoid global resets changing admin widgets. Build assets before `collectstatic` and verify with production-like static settings. [Tailwind guidance](https://unfoldadmin.com/docs/styles-scripts/customizing-tailwind/)

## Verification

Check registration and actual login/changelist/changeform paths, scoped role menus/direct URLs, form errors, action denial/success, related-object scope, theme/readability, and collected CSS/JS. Follow repository/user test requirements; the separate admin skill's default avoids adding/running tests unless requested. Browser or targeted runtime inspection still matters when admin functionality is the requested outcome.

## Recipe 1: custom User dan Group

Untuk custom User `AbstractUser` dari startup, definisikan form model yang tepat. Jangan unregister custom model yang belum terdaftar. `accounts/admin.py`:

```python
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

User = get_user_model()


class AccountChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class AccountCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User


for model in (User, Group):
    if admin.site.is_registered(model):
        admin.site.unregister(model)


@admin.register(User)
class AccountAdmin(DjangoUserAdmin, ModelAdmin):
    form = AccountChangeForm
    add_form = AccountCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ("username", "email", "is_active", "is_staff")
    search_fields = ("username", "email")


@admin.register(Group)
class GroupAdmin(DjangoGroupAdmin, ModelAdmin):
    pass
```

Fieldsets/add_fieldsets mengikuti DjangoUserAdmin untuk contoh AbstractUser. Bila username/email/custom fields berubah, sesuaikan forms dan fieldsets dengan model; jangan mengasumsikan recipe di atas berlaku untuk arbitrary AbstractBaseUser. Batasi pengelolaan superuser/staff/groups ke administrator yang memang berhak; jangan mengekspos privilege escalation kepada ordinary staff.

## Recipe 2: changelist dan bulk workflow

Melanjutkan contoh Project pada [vertical slice](vertical-slice.md), `projects/admin.py`:

```python
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import Project
from .services import activate_project


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ("name", "status_label", "owner", "created_at")
    search_fields = ("name",)
    list_filter = ("status",)
    list_select_related = ("owner",)
    list_per_page = 25
    readonly_fields = ("owner", "status", "created_at", "updated_at")
    warn_unsaved_form = True
    actions = ("activate_selected",)

    def get_queryset(self, request):
        return super().get_queryset(request).visible_to(request.user)

    def has_add_permission(self, request):
        return False  # contoh create melalui workflow HTML/API

    def has_change_permission(self, request, obj=None):
        allowed = super().has_change_permission(request, obj)
        return allowed and (obj is None or self.get_queryset(request).filter(pk=obj.pk).exists())

    @display(description="Status", label={"draft": "warning", "active": "success", "archived": "info"})
    def status_label(self, obj):
        return obj.status

    @admin.action(description="Aktifkan proyek terpilih", permissions=["change"])
    def activate_selected(self, request, queryset):
        succeeded = 0
        failed = 0
        for project in queryset:
            if not self.has_change_permission(request, project):
                failed += 1
                continue
            try:
                activate_project(actor=request.user, project_id=project.pk)
            except (ValidationError, Project.DoesNotExist):
                failed += 1
            else:
                succeeded += 1
        self.message_user(request, f"{succeeded} berhasil; {failed} tidak diproses.",
                          level=messages.WARNING if failed else messages.SUCCESS)
```

Ini partial-success example yang jelas: service atomic per row, bukan atomic seluruh batch. Besar batch harus dibatasi/queue bila diperlukan. Untuk add/edit yang mempunyai domain side effects, gunakan shared workflow; stock save_model/form path tidak otomatis memanggil service. Delete permission dan invariants harus mengikuti lifecycle nyata, bukan default permisif hanya karena admin tersedia.

## Recipe 3: advanced filters dan fieldsets

Untuk model yang memang mempunyai field terkait, enable filters app lalu pilih classes menurut tipe. Contoh penggantian `list_filter` Project:

```python
from unfold.contrib.filters.admin import FieldTextFilter, RangeDateTimeFilter

project_filters = (("name", FieldTextFilter), ("created_at", RangeDateTimeFilter), "status")
```

Assign `list_filter = project_filters`, `list_filter_submit = True`. Untuk FK/M2M besar gunakan autocomplete filter dan related admin `search_fields`, scoped suggestions, serta scoped validation. Untuk numbers tentukan unit/precision/range; untuk pilihan kecil gunakan dropdown/radio/checkbox. Semua kelas pilihan tersedia pada [feature map](unfold-feature-map.md#filters).

Fieldset tabs memakai named fieldsets `{"classes": ("tab",), "fields": (...)}`. Inline tabs memakai `tab = True`. Top navigation `UNFOLD["TABS"]` berbeda: list tabs menuju URL/filter, detail model selectors memakai bentuk `{"name": "projects.project", "detail": True}` sesuai versi. Jangan memasukkan field readonly yang tidak terdaftar dalam fieldsets atau mencampurkan named navigation tabs dengan inline tab mechanism.

## Recipe 4: sidebar dan branding

Pisahkan `config/unfold.py` bila settings panjang; module ini hanya konfigurasi/callback references, tidak query saat import. Basic navigation:

```python
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SITE_TITLE": "Operations",
    "SITE_HEADER": "Operations",
    "SIDEBAR": {
        "show_search": True,
        "navigation": [
            {
                "title": _("Projects"),
                "items": [
                    {
                        "title": _("Projects"),
                        "icon": "folder",
                        "link": reverse_lazy("admin:projects_project_changelist"),
                        "permission": lambda request: request.user.has_perm("projects.view_project"),
                    },
                ],
            },
        ],
    },
}
```

Tambahkan logo light/dark, environment label, login image, styles/scripts, dropdown, badge, colors, dan locale hanya sesuai produk. Callback badge/permission harus bounded dan tidak bocorkan count global. Untuk banyak admin sites, reverse namespace mengikuti site actual. Hiding link tetap bukan access enforcement.

## Recipe 5: custom page yang terlindungi

`projects/admin_views.py`:

```python
from django.views.generic import TemplateView
from unfold.views import UnfoldModelAdminViewMixin
from .models import Project


class ProjectSummaryView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Ringkasan proyek"
    permission_required = ("projects.view_project",)
    template_name = "admin/projects/summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_count"] = Project.objects.visible_to(self.request.user).count()
        return context
```

Override `ProjectAdmin.get_urls()` dan **prepend** custom routes sebelum default object catch-all. Berikut method untuk class tersebut:

```python
def get_urls(self):
    from django.urls import path
    from .admin_views import ProjectSummaryView

    view = self.admin_site.admin_view(ProjectSummaryView.as_view(model_admin=self))
    return [path("summary/", view, name="projects_project_summary")] + super().get_urls()
```

Template extends base Unfold/admin yang cocok dengan installed version, load `unfold`, render content/count/components dan breadcrumbs bila diperlukan. Tambahkan sidebar entry `admin:projects_project_summary` terpisah. Parameter/filter form divalidasi server; custom view tidak boleh menerima raw arbitrary filter expressions.

## Recipe 6: dashboard home

Override `templates/admin/index.html`, tambah directory pada TEMPLATES, set `DASHBOARD_CALLBACK` import path, dan return context. Callback menerima `(request, context)`; hitung authorized scope, time window, units/freshness, KPI count links, trend series, bounded recent table. Render dengan [components](unfold-components.md) dan [dashboard composition](unfold-recipes.md#admin-home-dashboard-recipe).

Dashboard filter bukan otomatis `list_filter`: buat validated query parameter form dan apply pada callback/custom view. Jangan mengada-ada trend tanpa multi-period data atau memakai synthetic numbers tanpa label. Cache by actor scope/tenant/time window dan tetapkan invalidation sesuai freshness.

## Recipe 7: actions dengan input/dialog

Pilih slot yang tepat: selected queryset `actions`; model-level `actions_list`; per row `actions_row`; object detail `actions_detail`; post-save `actions_submit_line`. Dialog handler menambahkan form argument; plain action handler memiliki signature berbeda. `BaseDialogForm` menerima request; validasi input dan scope di server. Detail/row handler memuat ulang object dari authorized queryset, memeriksa Django/business permission, method/CSRF, state, kemudian memanggil service.

Dialog memakai `dialog={"title": ..., "form_class": FormClass}` pada `@action`; documented completion menggunakan response `HX-Redirect`. Untuk workflows multi-step gunakan custom page, bukan memaksakan semua ke modal. Submitline menerima instance yang sudah disimpan: failure follow-up tidak berarti save awal dibatalkan. Dropdown group hanya untuk slots yang didukung. Signatures, callbacks, dan constraints seluruh family ada pada [feature map](unfold-feature-map.md#actions).

Custom dialog template harus merender hidden fields dari BaseDialogForm, termasuk submission marker release yang dipakai. Jangan hanya merender visible fields: form bisa terus invalid meski consent diisi. Bundled boilerplate memakai template bawaan dan regression test actual dialog payload.

## Recipe 8: related data dan integrations

Inlines: pilih Tabular untuk rows ringkas, Stacked untuk record kompleks; set `extra`, explicit fields, allowed add/change/delete, relation scope, tabs/collapse sesuai volume. Pagination reloads page sehingga unsaved edits perlu diperhatikan. Nested hanya satu tingkat dan bukan M2M. Nonrelated inline perlu queryset/save implementations, bukan mengganti FK yang sebenarnya diperlukan.

Sections membuka related table/template pada list; prefetch related data. Datasets menampilkan changelist di changeform; custom queryset wajib scope actor + parent dan none untuk parent baru. Search/pagination bukan jaminan row access, dan dataset tidak mendukung semua list features.

Untuk import/export, history, reversion, permissions, config/flags, money, scheduling, translations, impersonation, location: gunakan integration recipe/version spesifik pada [feature map](unfold-feature-map.md#integrations). Import Resource harus field explicit dan tenant-aware; history/reversion coverage diperiksa pada bulk/worker writes; impersonation memerlukan explicit grant, audit, dan exit state. Jangan memasang semua integrations sebagai default.

## Troubleshooting berurutan

| Gejala | Cek |
|---|---|
| Seluruh admin unstyled | static request/status, collectstatic, middleware/storage, app order |
| Hanya form unstyled | registered class/MRO, Unfold auth/inline forms |
| NoReverseMatch | actual admin site namespace, registered model/custom URL, UnfoldAdminSite |
| Menu ada tapi 403 | role/model permission/object policy; jangan melemahkan endpoint demi menu |
| Widget/third-party rusak | integration app order, forms, package compatibility, assets |
| Page lambat | counts, broad command search, related lists, template/serializer N+1 |
| Class utility tidak tampil | CSS output/compiler/version; runtime-generated classes |
| Custom page route tidak terjangkau | catch-all route precedence; prepend custom URLs |
| Dialog submit gagal | BaseDialogForm, signature, method/CSRF, validation, HX redirect |

Perbaiki root cause, kemudian cek path restricted staff yang sama. Untuk data sensitive periksa direct URLs dan suggestions, bukan screenshot menu saja.
