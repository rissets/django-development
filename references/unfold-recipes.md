# Feature selection recipes for Django Admin with Unfold

Use this guide when a request describes a product feature, CRUD workflow, detail page, filtering need, admin portal, or custom site. It maps user intent to the Unfold features that fit together. Treat examples as selection guidance: inspect the project's models, current admin patterns, permissions, and installed versions before applying them.

## How to select features

Start from the user workflow and data relationships; do not add every Unfold feature to every model admin. Choose only features that solve a real task, and combine them where they support the same workflow.

| User need | Usually use | Consider when useful | Avoid or watch for |
|---|---|---|---|
| Browse and find records | `ModelAdmin`, `list_display`, `search_fields`, `list_filter` | Unfold filter variants, `list_filter_submit`, tabs, `InfinitePaginator` | Huge related dropdown lists; unnecessary search over all fields |
| Edit a record | `fieldsets`, `fields`, form validation | fieldset tabs, conditional fields, field-specific widgets | Client-side hiding as a replacement for server validation |
| Manage related records | Unfold `StackedInline`/`TabularInline` | inline tabs, collapsible inlines, counts, sorting, pagination | N+1 queries, expensive inline counts, unsupported deep/M2M nesting |
| Run a bulk operation on selected records | Django `actions` | confirmation/form action pattern where supported | `actions_list` if the operation must use only selected IDs; it is model-level and receives no queryset |
| Run an operation on a particular row/object | `actions_row` or `actions_detail` | `@action`, permission hooks, dialog form | Row permission hook is not object-specific; re-check permissions and state in the handler |
| Add an operation to save | ordinary save handling or `actions_submit_line` | submit-line action if it must run after the edited instance is saved | It runs after save; plan for follow-up failure and repeat submissions |
| Add metrics/activity visualization | dashboard callback and Unfold components | Card, Chart, Table, Tracker, Cohort, Progress | Do not put complex analytics in templates; scope queries and data by user permissions |
| Add a workflow beyond normal CRUD | custom admin page/view | action with a form, tabs, components, messages | Unprotected custom URLs or assuming `/admin/` implies authorization |
| Separate admin surfaces | `UnfoldAdminSite` and URL namespaces | distinct staff roles, subsystems, branding, navigation | Replacing `AdminSite` changes registration and reverse URL namespaces |
| Change appearance or behavior | `UNFOLD` settings and existing template hooks | `STYLES`, `SCRIPTS`, components, template overrides | Global CSS/Tailwind changes for a local one-off, or uncollected static files |

## Admin home dashboard recipe

When the request is to build or redesign the admin home dashboard, plan a real information surface rather than an empty welcome page. The default dashboard deliverable should include these areas, populated from the project's real domain data:

1. **Summary:** a row of KPI cards for the most important totals/status counts. Give each metric a clear label, unit, time window or “as of” date, and an appropriate link/action when staff can follow up.
2. **Chart:** at least one time trend or comparison chart when the data supports it. The documented built-in charts are Chart.js **line** and **bar** components; use line for time progression and bar for category/status comparisons. Do not invent values or imply a trend from a single snapshot.
3. **Diagram / visual analysis:** choose the visualization that answers a real question. Use a **Tracker** for daily/weekly activity intensity, **Cohort** for retention by start period, or another chart for numeric comparisons. The current documented Unfold inventory does not document a general-purpose process/flow diagram component. If the request means a process or relationship diagram, implement a custom template/SVG or explicitly chosen JS visualization and add its assets through the project's existing pipeline.
4. **Operational table:** show a bounded list of recent, pending, low-stock, failed, or otherwise actionable records with useful columns and safe links into their admin change pages. State the sort/window and provide an empty state when there are no rows.
5. **Navigation / next action:** add a small set of links or buttons for the staff user's frequent tasks. Use Unfold's navigation/link/button components or existing sidebar entries; do not duplicate the full sidebar.

Treat summary + chart + visual analysis + table as the default composition for a requested home dashboard. If the domain has no meaningful data for one area yet, show a truthful empty state or report the missing data source instead of generating placeholder figures. Keep the dashboard focused: a section is included because it answers an operational question, not merely because a component exists.

### Data and template wiring

The documented pattern overrides `templates/admin/index.html`, extends `admin/base.html`, configures `UNFOLD["DASHBOARD_CALLBACK"]`, and adds the template directory to Django `TEMPLATES[...]["DIRS"]`. The callback receives `(request, context)` and returns the context. Compute or aggregate dashboard data in Python/querysets, scope every query to the current user's access, and avoid N+1 queries. Define metric periods and chart labels consistently (timezone, date range, units, and denominators).

Use [unfold-components.md](unfold-components.md) for shapes and renderer details:

- KPI cards: `unfold/components/card.html`, optionally nested `text` and `title` components.
- Numeric chart: `unfold/components/chart/line.html` or `unfold/components/chart/bar.html`; provide JSON-encoded labels/datasets as documented.
- Activity/retention visual: `unfold/components/tracker.html` or the cohort component after verifying its template path against the installed package.
- Operational rows: `unfold/components/table.html` with bounded `headers` and `rows` data.
- Navigation: `unfold/components/navigation.html`, link, or button components.

Dashboard-specific filter controls/date pickers are not described as a built-in dashboard feature in the docs catalog. Changelist `list_filter` does not automatically filter dashboard callback data. If interactive dashboard filters are required, design an explicit request/query-parameter flow, validate inputs, scope data permissions, and use a custom page or custom template behavior rather than assuming changelist filters apply.

### Dashboard template composition sketch

The example shows layout intent; replace context names and data with the project's models and permission rules. `DASHBOARD_CALLBACK` should provide `summary_cards`, serialized `trend_data`, `activity_items`, and `recent_table`.

```django
{% extends "admin/base.html" %}
{% load i18n unfold %}

{% block content %}
    <div class="flex flex-col gap-6">
        <section aria-label="Summary" class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            {% for item in summary_cards %}
                {% component "unfold/components/card.html" with title=item.label footer=item.period %}
                    {% component "unfold/components/title.html" %}
                        {{ item.value }}
                    {% endcomponent %}
                    {% if item.href %}
                        {% component "unfold/components/link.html" with href=item.href %}
                            {% trans "View records" %}
                        {% endcomponent %}
                    {% endif %}
                {% endcomponent %}
            {% endfor %}
        </section>

        <section aria-label="Trends" class="grid grid-cols-1 gap-4 xl:grid-cols-2">
            {% component "unfold/components/card.html" with title=trend_title %}
                {% component "unfold/components/chart/line.html" with data=trend_data %}{% endcomponent %}
            {% endcomponent %}
            {% component "unfold/components/card.html" with title=activity_title %}
                {% component "unfold/components/tracker.html" with data=activity_items %}{% endcomponent %}
            {% endcomponent %}
        </section>

        <section aria-label="Recent work">
            {% component "unfold/components/card.html" with title=recent_title %}
                {% component "unfold/components/table.html" with table=recent_table card_included=1 striped=1 %}
                {% endcomponent %}
            {% endcomponent %}
        </section>
    </div>
{% endblock %}
```

Confirm that the installed Unfold version accepts direct `data` arguments for each component; the docs also show preparing data in registered component classes. If a template fails to load or the chart expects a different serialization shape, follow the matching component page and the installed package. Custom utility classes in this project template are not automatically compiled by Unfold: use the existing CSS pipeline, load styles through `STYLES`, and collect static assets for deployment.

## Product CRUD feature recipe

For a product catalog or similar model, evaluate the feature set below against the actual requirements. Do not blindly add optional features that the workflow does not need.

### Product list / changelist

1. Use an Unfold `ModelAdmin` for a project already using Unfold. Select a compact `list_display` that answers the staff user's first questions (for example SKU, name, category, status, price, inventory state).
2. Add `search_fields` for identifiers and names. Add a filter for fields that staff actually use to narrow results.
3. Pick filters by model field and option count:
   - A small static `choices` field: choice dropdown, checkbox, or radio filter.
   - A related category/brand foreign key with a moderate option set: related dropdown; use autocomplete when the related admin supports `search_fields` and the relation is large.
   - Price/quantity: numeric range or slider filter where the installed version and usability fit.
   - Created/updated timestamps: date or datetime range filter.
   - Free-text filtering with custom semantics: subclass `TextFilter` and implement its queryset logic.
   - A filter with typed inputs: enable `list_filter_submit` so users can submit the values.
4. Keep the changelist queryset and filter options efficient. Add `select_related` for displayed foreign keys and `prefetch_related` for displayed many-to-many/reverse relations when measurements show it is needed. Reduce page size or use the documented `InfinitePaginator` when total counts are the bottleneck.
5. Use `@display` for status labels or a compact multi-line display where it improves scanning. Avoid making every column an icon, badge, or dropdown; preserve readable text and useful links.
6. Use tabs only when staff need stable, permission-aware list segments, such as All / Draft / Active. A tab changes navigation; it does not replace queryset authorization or filters.

### Product operations

Choose the action slot by target and selection semantics:

- Bulk archive selected products: Django's selected-queryset `actions` slot; verify every selected object is authorized and in an allowed state.
- Import/export or a general catalog operation: `actions_list` may fit when it works at model level. It does not receive the changelist selection; if the user needs selected rows, use a queryset action or a purpose-built page with explicit selection handling.
- One product's external preview or state transition from a list row: `actions_row`; remember the documented row permission callback is global.
- Object-specific action on the product changeform: `actions_detail` with object-aware permission checks.
- Save edited product then publish/sync it: consider `actions_submit_line`, whose handler runs after save. Make the external operation idempotent or report partial failure clearly.
- Confirmation or extra input: use the dialog action flow and `BaseDialogForm`, or a custom Unfold page when the interaction needs a larger workflow.

Use `@action` metadata for human-readable labels, icon, `url_path`, variant, attributes, and permission hooks. Keep all real authorization and state validation in the handler.

### Product change/detail form

1. Organize fields with `fieldsets`. Add named fieldsets with the `tab` CSS class only if the form is long enough to benefit from internal tabs.
2. Use `conditional_fields` for dependent UI (for example, show shipping dimensions only for shippable items), but keep model/form validation authoritative.
3. Add an Unfold inline for actual related rows such as variants, images, or supplier mappings when that relationship belongs in the product edit workflow. Use `tab = True` to group multiple inlines only when useful. For many rows, consider pagination; for manual ordering, add the indexed ordering field required for sortable inlines.
4. Choose widgets per field semantics: Unfold's `WysiwygWidget` for rich text fields, `ArrayWidget` for PostgreSQL arrays, JSON schema fields for validated structured configuration, or a custom autocomplete field for large remote choices. Do not globally replace every text field unless every one should behave as rich text.
5. Add `actions_detail` for object operations and Django change permissions for editing. Use a custom page instead when the workflow is multi-step, requires its own form, or spans several models.
6. Consider changeform tabs in `UNFOLD["TABS"]` when the object has coherent alternate admin views. Their item links and permission callbacks must use valid names and permissions. Changeform tabs are separate from fieldset tabs and inline tabs.

### Product overview / analytics

If the requirement is product KPIs or trends rather than CRUD, put aggregate data in a dashboard callback or an explicitly permissioned custom admin page. Follow the **Admin home dashboard recipe** above and compose cards, charts, tables, and Tracker from [unfold-components.md](unfold-components.md). A component only renders supplied data; it does not create model filters, data permissions, or aggregation automatically.

For object-specific history, keep the page scoped to the product and current user's permission. A `TableSection` can show related rows in an expandable changelist when that interaction is appropriate; prefetch related data to avoid query multiplication.

## Filter design guide

Read the matching page in [unfold-feature-map.md](unfold-feature-map.md#filters) and verify current import names. Choose by input semantics:

| Field / filter need | Unfold option family | Selection criteria |
|---|---|---|
| One string field using case-insensitive contains | `FieldTextFilter` | Simple field path |
| Custom text search or compound predicate | `TextFilter` | Define parameter name and queryset method |
| Date range | `RangeDateFilter` | Date field |
| Datetime range | `RangeDateTimeFilter` | Datetime field/time-zone expectations confirmed |
| Small static choices | `ChoicesDropdownFilter`, multiple choice, checkbox, or radio variants | Dropdown for compact UI; checkbox/radio when all options should be visible |
| Foreign key / many-to-many | `RelatedDropdownFilter`, `RelatedCheckboxFilter`, or autocomplete variants | Prefer autocomplete for larger relations; related admin needs `search_fields` |
| Numeric value/range | `SingleNumericFilter`, `RangeNumericFilter`, `RangeNumericListFilter`, or `SliderNumericFilter` | Confirm scale, decimals, sensible step, and exact installed API |
| Boolean | `BooleanRadioFilter` | Useful for explicit Yes/No/All selection |
| Distinct database values | `AllValuesCheckboxFilter` | Only when number of distinct values stays manageable |
| Horizontal choices | supported horizontal filter property or `list_filter_options` | Best for a small number of choices and wide screens |

Unfold's dropdown filters use Select2 but do not provide dropdown autocomplete in the docs. Do not use them for very large choice tables. Autocomplete filters are relation-specific and depend on the referenced model admin's `search_fields`. Remember to enable `unfold.contrib.filters` after `unfold` when required by the project version.

## Detail pages, tabs, and related data

Keep these patterns distinct:

- **Top-level tabs** under `UNFOLD["TABS"]`: navigate between changelists or admin views. Use a `detail: True` model entry for changeform tab navigation.
- **Fieldset tabs**: add `classes: ["tab"]` to a named fieldset. They appear inside the main changeform body, not as the global top navigation.
- **Inline tabs**: set `tab = True` on Unfold inline classes. These group inline sections independently of main model tabs.
- **Dynamic/custom-page tabs**: provide a request-aware `TABS` callback or render `tab_list` in a custom template; set active state where Unfold cannot infer it.
- **Expandable changelist sections**: `TableSection` or `TemplateSection` opens content per row; this is a changelist pattern, not the same as inlines or changeform tabs.
- **Datasets**: embed a changelist-like table on a changeform. The docs support search/pagination but not list filters/sorting; explicitly scope their queryset.

For standard model editing, prefer the standard changeform and inlines. Make a custom view when the user requests a task flow that cannot be represented clearly as a form, tabs, inlines, or action. Protect every custom URL with admin site wrapping and explicit permission checks.

## Custom site decision recipe

Use the standard Unfold admin site unless the request requires multiple distinct admin surfaces, different registration/URL namespaces, or an intentionally separate admin experience. For a custom site:

1. Subclass `unfold.sites.UnfoldAdminSite` and instantiate it with a unique namespace/name.
2. Mount `custom_admin_site.urls` at the chosen URL.
3. Register each model with `@admin.register(Model, site=custom_admin_site)` or `custom_admin_site.register(...)`.
4. Keep model admins on `unfold.admin.ModelAdmin`.
5. If replacing the default site via `AdminConfig.default_site`, use the documented `unfold.apps.BasicAppConfig` setup and inspect the project's `INSTALLED_APPS` ordering.
6. Check all admin URL reversals, custom views, login/logout paths, and sidebar links against the new namespace. The docs warn that plain Django `AdminSite` may not supply URL patterns Unfold expects.
7. Test only if requested; when runtime verification is requested, verify login, one changelist, one changeform, permissions, and custom routes using the actual URL namespace.

## All requested feature families

Before implementing a multi-feature admin request, use this checklist and only select relevant items:

- **Configuration:** `UNFOLD`, `ModelAdmin` options, site dropdown, custom site, dashboard, languages, branding, command palette.
- **Filters:** select by data type, volume, and input UX; configure submit behavior if needed.
- **Actions:** distinguish selected-queryset, model-level, row, detail, submit-line, and dialog/form flows.
- **Tabs:** distinguish changelist, changeform, fieldset, inline, and dynamic/custom tabs.
- **Widgets:** choose by field semantics and install the right Unfold form app.
- **Inlines:** relation, data volume, sortability, nesting limit, pagination, and query count.
- **Fields:** JSON display vs JSONSchema validation vs custom autocomplete.
- **Integrations:** package-specific app ordering, class inheritance, forms/widgets, and package versions.
- **Components:** use for dashboard/custom-page visualizations; consult `unfold-components.md` for every component and payload.
- **Decorators:** `@display` for changelist presentation; Unfold `@action` for action metadata and permissions.
- **Styles & scripts:** use `STYLES`/`SCRIPTS`, match the CSS build to Unfold version, and collect static files.
- **Development:** use the official Development page only when changing or contributing to the Unfold package itself; normal project feature work should follow the host repository's commands.

Find every official URL in the relevant category of [unfold-feature-map.md](unfold-feature-map.md). Exact page inventory and version caveats live there; this guide is the feature-selection layer.
