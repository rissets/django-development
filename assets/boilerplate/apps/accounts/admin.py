from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import User


class AccountChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class AccountCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User


class SuperuserOnlyAdmin:
    # Pengelolaan identity/roles terpisah dari operator data proyek.
    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)


if admin.site.is_registered(Group):
    admin.site.unregister(Group)


@admin.register(User)
class AccountAdmin(SuperuserOnlyAdmin, DjangoUserAdmin, ModelAdmin):
    form = AccountChangeForm
    add_form = AccountCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ("username", "email", "is_active", "is_staff")


@admin.register(Group)
class GroupAdmin(SuperuserOnlyAdmin, DjangoGroupAdmin, ModelAdmin):
    pass
