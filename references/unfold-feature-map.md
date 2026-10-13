# Peta lengkap fitur Django Unfold

Inventaris **80 halaman** (index + 79 topik) dari navigasi resmi, diperiksa ulang pada 13 Oktober 2026; semua URL inventory berhasil diambil. Panduan ini memetakan fungsi, prasyarat, dan batas fitur. Contoh implementasi lengkap ada pada [Unfold admin](unfold-admin.md), [recipes](unfold-recipes.md), dan [components](unfold-components.md). Website dapat berubah; cocokkan imports/signatures dengan release terpasang. Ini cakupan seluruh topik navigasi, bukan klaim setiap internal API Unfold tercakup atau seluruh fitur sudah diuji runtime.

Gunakan sebagai checklist desain admin: untuk tiap workflow, tentukan keluarga yang relevan, baca recipe, konfigurasi hanya fitur yang dipakai, dan verifikasi izin/query/form/asset nyata. Jangan mengaktifkan semuanya sekaligus.

## Documentation home

- [Unfold admin theme documentation](https://unfoldadmin.com/docs/) — FAQ and navigation index. Troubleshooting notes: missing styling can stem from static collection or incompatible custom Tailwind output; unstyled forms usually mean the registered class does not inherit from `unfold.admin.ModelAdmin`; built-in auth users/groups need styled re-registration; third-party packages may need package-specific integration work.

## Installation

- [Quickstart](https://unfoldadmin.com/docs/installation/quickstart/) — Install `django-unfold`, put `unfold` before `django.contrib.admin`, add optional `unfold.contrib.*` apps only for used features, keep the standard `admin.site.urls` route, and subclass `unfold.admin.ModelAdmin`.
- [User & group models](https://unfoldadmin.com/docs/installation/auth/) — Unregister/re-register built-in `User` and `Group` admins; use Unfold's user creation/change/password forms so auth pages receive the expected styling.

## Configuration

- [Settings options](https://unfoldadmin.com/docs/configuration/settings/) — Reference for the `UNFOLD` dictionary: branding, site links, sidebar, tabs, environment and dashboard callbacks, theme/colors, login, UI visibility, assets, and callback examples.
- [Site dropdown](https://unfoldadmin.com/docs/configuration/site-dropdown/) — Configure the clickable site-brand dropdown through `SITE_DROPDOWN`, with titles, icons, links, and optional anchor attributes.
- [ModelAdmin options](https://unfoldadmin.com/docs/configuration/modeladmin/) — Unfold `ModelAdmin`-specific changelist, filter, action-slot, changeform template, readonly preprocessing, add-link, unsaved-form, and widget options.
- [Conditional fields](https://unfoldadmin.com/docs/configuration/conditional-fields/) — Show/hide fields via `conditional_fields` Alpine expressions. Field visibility is client-side presentation; validate submitted data server-side.
- [Avatar](https://unfoldadmin.com/docs/configuration/avatar/) — Customize user avatar URL, badge variant/count, and badge link with model properties.
- [Command](https://unfoldadmin.com/docs/configuration/command/) — Cmd/Ctrl-K search; model search is opt-in and requires `search_fields`. Limit searchable models; custom search callbacks must enforce permissions. Search history uses browser `localStorage`.
- [Paginator](https://unfoldadmin.com/docs/configuration/paginator/) — `InfinitePaginator` removes the costly total count and simplifies navigation to previous/next; docs pair it with `show_full_result_count = False` for large datasets.
- [Crispy Forms](https://unfoldadmin.com/docs/configuration/crispy-forms/) — Use the `unfold_crispy` template pack, `FormHelper`, layout objects, Unfold view mixins, and admin templates; avoid imposing the Unfold pack globally if the frontend has a different pack.
- [Sections (expandable rows)](https://unfoldadmin.com/docs/configuration/sections/) — `list_sections` supports `TableSection` and `TemplateSection`; related tables can cause N+1 queries, so inspect and prefetch related data.
- [Custom pages](https://unfoldadmin.com/docs/configuration/custom-pages/) — Register a class-based view with `UnfoldModelAdminViewMixin`, `title`, `permission_required`, and `admin_site.admin_view`; pass `model_admin=self`. Add sidebar navigation separately. Breadcrumbs may be application-owned and are noted as changed from Unfold 0.64.
- [Sortable changelist](https://unfoldadmin.com/docs/configuration/sortable-changelist/) — Requires indexed `PositiveIntegerField`, configured `ordering_field`, and model/queryset ordering. Reordering only applies to the current page and must be saved before leaving it.
- [Dashboard](https://unfoldadmin.com/docs/configuration/dashboard/) — Override `templates/admin/index.html`, configure template directories, and use `DASHBOARD_CALLBACK(request, context)` for custom context; custom template styles need their own build pipeline. For a complete home-page composition using summaries, charts, diagrams/visuals, tables, and links, see [unfold-recipes.md](unfold-recipes.md#admin-home-dashboard-recipe).
- [Custom sites](https://unfoldadmin.com/docs/configuration/custom-sites/) — Use `UnfoldAdminSite` for a custom admin site. A regular Django `AdminSite` may lack the reverse URL names Unfold expects; `BasicAppConfig` is used for a default-site override pattern.
- [Multi-language](https://unfoldadmin.com/docs/configuration/multi-language/) — Configure `LocaleMiddleware`, `USE_I18N`, `LANGUAGE_CODE`, and `LANGUAGES`; add the `i18n/` URL outside `i18n_patterns`; enable `SHOW_LANGUAGES` and optionally override navigation languages.
- [Datasets](https://unfoldadmin.com/docs/configuration/datasets/) — Embed a changelist-like dataset on changeforms with fields, search, pagination, and custom queryset; list filters and sorting are not supported. Scope `get_queryset()` to user and parent-object permissions.

## Filters

- [Introduction to filters](https://unfoldadmin.com/docs/filters/introduction/) — Install `unfold.contrib.filters` after `unfold`; configure `list_filter_submit` for input-based filters and `list_filter_options` for labels/layout.
- [Text filter](https://unfoldadmin.com/docs/filters/text/) — `FieldTextFilter` provides a straightforward case-insensitive field search; subclass `TextFilter` for custom query logic and URL parameter names.
- [Datetime filter](https://unfoldadmin.com/docs/filters/datetime/) — Use `RangeDateFilter` for date values and `RangeDateTimeFilter` for datetime values; filters app must be enabled.
- [Dropdown filter](https://unfoldadmin.com/docs/filters/dropdown/) — Choice, related, multiple, and custom dropdown filters. No autocomplete dropdown is provided; avoid huge option sets. Dropdowns use Select2, not a native select.
- [Numeric filter](https://unfoldadmin.com/docs/filters/numeric/) — Numeric range, list-range, single-value, and slider filters; custom sliders can set decimal precision and step size.
- [Horizontal layout filter](https://unfoldadmin.com/docs/filters/horizontal/) — Set the supported horizontal filter property or option to lay out choices horizontally in changelists.
- [Autocomplete filter](https://unfoldadmin.com/docs/filters/autocomplete/) — Single/multiple autocomplete filters require FK/M2M fields and `search_fields` on the related model's admin.
- [Checkbox and radio filters](https://unfoldadmin.com/docs/filters/checkbox-radio/) — Choice radio/checkbox, boolean radio, related checkbox, all-values checkbox, and custom filter bases; best for a manageable number of options.

## Actions

- [Introduction to actions](https://unfoldadmin.com/docs/actions/introduction/) — Unfold actions extend Django actions. Covers `@action`, icons/variants, custom and Django permissions, action slots, action URLs/handlers, and hiding built-in actions.
- [Actions with dialog](https://unfoldadmin.com/docs/actions/dialog-actions/) — Confirmation dialogs and custom dialog forms must use `BaseDialogForm`; supports before/after templates and extra context.
- [Changelist actions](https://unfoldadmin.com/docs/actions/changelist/) — Top-of-list model-level actions; unlike selected-object actions, handlers do not receive a queryset or object IDs.
- [Changelist row actions](https://unfoldadmin.com/docs/actions/changelist-row/) — Per-row dropdown actions; their documented permission callback is global and does not receive an object ID.
- [Changeform actions](https://unfoldadmin.com/docs/actions/changeform/) — Object-specific actions at the top of a detail page; permission hooks can receive the object ID.
- [Changeform submitline actions](https://unfoldadmin.com/docs/actions/changeform-submitline/) — Run beside save; the form and instance are saved before the action logic runs.
- [Dropdown action](https://unfoldadmin.com/docs/actions/dropdown-actions/) — Group `actions_list` or `actions_detail` into titled menus. Dropdowns are not supported for row or submit-line actions.
- [Action with form example](https://unfoldadmin.com/docs/actions/action-form-example/) — Detail action that collects input with a custom Unfold-styled form and template before performing work.

## Tabs

- [Changelist tabs](https://unfoldadmin.com/docs/tabs/changelist/) — Configure top-level list tabs with `UNFOLD["TABS"]`, model selectors, links, and permissions.
- [Changeform tabs](https://unfoldadmin.com/docs/tabs/changeform/) — Reuse `TABS` configuration with `detail: True` on a model entry for changeform navigation.
- [Fieldsets tabs](https://unfoldadmin.com/docs/tabs/fieldsets/) — Add a `tab` class to named fieldsets; these render within the form body rather than as the top-page tabs.
- [Inlines tabs](https://unfoldadmin.com/docs/tabs/inline/) — Set `tab = True` on Unfold inline classes; this navigation is independent from the main tab system.
- [Dynamic tabs](https://unfoldadmin.com/docs/tabs/dynamic/) — Generate tab configurations through an importable callback receiving the request; render custom-page tabs with `tab_list` and mark active items as needed.

## Widgets

- [ArrayWidget](https://unfoldadmin.com/docs/widgets/array/) — Add `unfold.contrib.forms`; widget supports PostgreSQL `ArrayField`. Choices must be explicitly supplied, for example from `get_form()`.
- [WysiwygWidget](https://unfoldadmin.com/docs/widgets/wysiwyg/) — Add `unfold.contrib.forms`; uses Trix for rich text. Built-in file upload is not provided.

## Inlines

- [Introduction to inlines](https://unfoldadmin.com/docs/inlines/introduction/) — Unfold's `StackedInline` and `TabularInline` provide the intended styling and feature set.
- [Inline options](https://unfoldadmin.com/docs/inlines/options/) — Counts, count badges, custom inline titles, hidden title rows, and collapsible stacked inlines. Counts call `count()` per inline; hidden stacked-inline titles require deletion disabled.
- [Nonrelated inlines](https://unfoldadmin.com/docs/inlines/nonrelated/) — No-FK inline support from `unfold.contrib.inlines`; implement `get_form_queryset()` and save methods explicitly.
- [Sortable inlines](https://unfoldadmin.com/docs/inlines/sortable/) — Indexed `PositiveIntegerField` plus `ordering_field`; new records must be saved before sorting.
- [Paginated inlines](https://unfoldadmin.com/docs/inlines/paginated/) — Set `per_page`; each inline keeps separate URL pagination state. Navigation reloads the whole page; AJAX pagination is not supported.
- [Nested inlines](https://unfoldadmin.com/docs/inlines/nested/) — Hierarchical inlines support one nested level only and do not support M2M nesting.

## Fields

- [JSONField](https://unfoldadmin.com/docs/fields/json/) — Readonly JSON fields get basic formatting and optional Pygments syntax highlighting; editable JSON uses a textarea widget.
- [JSONSchemaField](https://unfoldadmin.com/docs/fields/jsonschemafield/) — Schema-backed JSON model field using a static schema dict or importable callback. The callback has no request/user context; `jsonschema` is recommended for backend validation.
- [Autocomplete fields](https://unfoldadmin.com/docs/fields/autocomplete/) — Custom autocomplete form fields use `BaseAutocompleteView`, registered admin URLs, and permission checks; avoid loading every choice on GET for large tables.

## Integrations

- [django-celery-beat](https://unfoldadmin.com/docs/integrations/django-celery-beat/) — Re-register default package admins on Unfold's `ModelAdmin` to keep changelists styled.
- [djangoql](https://unfoldadmin.com/docs/integrations/djangoql/) — Default djangoql search UI is styled; custom djangoql-generated pages are not.
- [django-money](https://unfoldadmin.com/docs/integrations/django-money/) — Built-in MoneyField widget styling; no additional Unfold app is required according to the page.
- [django-constance](https://unfoldadmin.com/docs/integrations/django-constance/) — Put `unfold.contrib.constance` before `constance`; configure provided widgets/extra fields.
- [django-json-widget](https://unfoldadmin.com/docs/integrations/django-json-widget/) — Automatic styling and dark-mode support after installing both packages; no extra Unfold app is described.
- [django-waffle](https://unfoldadmin.com/docs/integrations/django-waffle/) — Re-register admins with Unfold; use Unfold's custom `FlagAdmin` for the special users field.
- [django-import-export](https://unfoldadmin.com/docs/integrations/django-import-export/) — Add `unfold.contrib.import_export`; use Unfold import/export forms. The custom export action class is unnecessary for django-import-export 4.x+ per the page.
- [django-simple-history](https://unfoldadmin.com/docs/integrations/django-simple-history/) — Order `unfold.contrib.simple_history` between Unfold and `simple_history`; combine `SimpleHistoryAdmin` with Unfold `ModelAdmin`.
- [django-guardian](https://unfoldadmin.com/docs/integrations/django-guardian/) — Add `unfold.contrib.guardian` to override templates and expose object permissions on changeforms.
- [django-modeltranslation](https://unfoldadmin.com/docs/integrations/django-modeltranslation/) — Page includes translation admin/flag examples but also states this integration is deprecated in django-unfold 0.102.0; confirm the installed version before using it.
- [django-hijack](https://unfoldadmin.com/docs/integrations/django-hijack/) — Add `unfold.contrib.hijack` for styled impersonation notice/buttons; the notice may not style correctly outside admin.
- [django-location-field](https://unfoldadmin.com/docs/integrations/django-location-field/) — Put `unfold.contrib.location_field` before `location_field`; use Unfold's location widget in a custom form.

- [django-reversion](https://unfoldadmin.com/docs/integrations/django-reversion/) — Tambahkan `unfold.contrib.reversion` sebelum `reversion`; konfigurasi revision tracking dari paketnya tetap dibutuhkan. Periksa hak recovery, actor, dan efek rollback data.
- [django-reversion-compare](https://unfoldadmin.com/docs/integrations/django-reversion-compare/) — Membutuhkan django-reversion; tempatkan override `unfold.contrib.reversion_compare` sebelum paket compare. Gunakan untuk UI perbedaan revision, bukan menjamin semua perubahan eksternal tercatat.

## Components

- [Introduction to components](https://unfoldadmin.com/docs/components/introduction/) — Template components can nest and accept variables. The complete built-in inventory is button, card, bar/line chart, cohort, container, flex, icon, navigation, progress, separator, table, text, title, tracker, and layer. `unfold-components.md` documents their arguments and examples, including a ready-to-adapt Tracker.
- [Component class](https://unfoldadmin.com/docs/components/component-class/) — Optional data preparation classes use `BaseComponent`, `register_component`, and `get_context_data()`.
- [Cohort](https://unfoldadmin.com/docs/components/cohort/) — Cohort table visualization consumes headers, rows, and cell values, passed directly or through a component class.
- [Tracker](https://unfoldadmin.com/docs/components/tracker/) — Grid/heatmap component supports cell color, tooltip, link, custom class, and size.
- [Card](https://unfoldadmin.com/docs/components/card/) — Content container with title, label, action, icon, footer, link, border control, and CSS class parameters.
- [Table](https://unfoldadmin.com/docs/components/table/) — Responsive table accepts headers and rows, optional nested tables, stripes, card integration, and max-height scrolling.
- [Chart](https://unfoldadmin.com/docs/components/chart/) — Bar and line charts use Chart.js; configure dataset and options, with responsive/tooltip parameters and special axis tick/label options. JavaScript functions are not supported in the options payload.
- [Link](https://unfoldadmin.com/docs/components/link/) — Styled link with optional icon and external-link behavior.
- [Button](https://unfoldadmin.com/docs/components/button/) — Standardized admin button component with documented appearance/behavior parameters; confirm the live page for its full current parameter list.
- [Progress](https://unfoldadmin.com/docs/components/progress/) — Single or segmented progress bars with title, description, value, and per-segment styling.
- [Layer](https://unfoldadmin.com/docs/components/layer/) — Abstract component wrapper that supplies template variables from a registered component class.

## Decorators, styles, and development

- [Display decorator](https://unfoldadmin.com/docs/decorators/display/) — Unfold `@display` supports colored labels, two-line headers, dropdowns with list or custom HTML content, and price formatting.
- [Action decorator](https://unfoldadmin.com/docs/decorators/action/) — Unfold `@action` extends Django action options with URL path, HTML attrs, icon, description, variant, and permission hooks.
- [Loading styles and scripts](https://unfoldadmin.com/docs/styles-scripts/loading-files/) — Load project assets using `UNFOLD["STYLES"]` and `UNFOLD["SCRIPTS"]`; run `collectstatic` for deployment.
- [Customizing Tailwind stylesheet](https://unfoldadmin.com/docs/styles-scripts/customizing-tailwind/) — Version-specific CSS/Tailwind setup. The page recommends plain CSS for Unfold 0.56+ and separately documents Tailwind 4 for 0.57+ and Tailwind 3 for older versions; verify the project's exact version and avoid mixing generated CSS across major versions.
- [Development](https://unfoldadmin.com/docs/development/) — Unfold repository contributor workflow: test server, pytest, Tailwind compilation, and pre-commit. This page concerns development of Unfold itself, not routine use of the admin package.
