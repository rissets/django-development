# Unfold component catalog and implementation patterns

Use this reference when adding dashboard or custom-admin UI with Unfold components. It documents the component inventory and implementation patterns from the linked official pages. These APIs can change with `django-unfold`; inspect the installed version and the relevant page before relying on an option that matters to the implementation.

## Render and compose components

Unfold components are Django template components. Load the tag library and call the component by template path. Child markup is exposed to the parent as `children`; arguments follow Django template `with` conventions. Components can be nested to compose dashboards without replacing Unfold's layout system.

```django
{% load i18n unfold %}

{% component "unfold/components/card.html" with title=card_title %}
    {% component "unfold/components/title.html" %}
        {{ metric }}
    {% endcomponent %}
{% endcomponent %}
```

You can provide data directly in template context (for example, from `DASHBOARD_CALLBACK`) or use a registered component class when the data preparation belongs in Python. Custom classes use `BaseComponent`, `@register_component`, and `get_context_data()`:

```python
from unfold.components import BaseComponent, register_component


@register_component
class ExampleComponent(BaseComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"data": []})
        return context
```

```django
{% load unfold %}
{% component "unfold/components/tracker.html" with component_class="ExampleComponent" %}
{% endcomponent %}
```

Keep database queries out of template loops. If a component is visible only to certain admins, enforce that at the view/callback/query layer; UI composition itself is not access control.

## Built-in component catalog

The main components page lists these built-in templates and their documented arguments. Detailed pages exist for card, chart, cohort, tracker, table, link, button, progress, and layer. Container, flex, icon, navigation, separator, text, and title are listed on the introduction page without separate deep-dive pages.

| Component | Template | Purpose and documented arguments |
|---|---|---|
| Button | `unfold/components/button.html` | Button or link. Catalog: `class`, `name`, `href`, `submit`. Detailed options: `variant` (`default`, `secondary`, `danger`, `ghost`), `size` (`sm`, `md`), `form`, `value`, `title`, `extra_attrs`, `attrs`. |
| Card | `unfold/components/card.html` | Content container. `class`, `title`, `footer`, `label`, `icon`; detailed page also documents `action`, `href`, and `disable_border`. |
| Bar chart | `unfold/components/chart/bar.html` | Chart.js bar chart. `class`, `data`, `height`, `width`; chart options are described below. |
| Line chart | `unfold/components/chart/line.html` | Chart.js line chart. `class`, `data`, `height`, `width`; chart options are described below. |
| Cohort | See path note below | Cohort/retention table. `data` with headers and row/cell values. |
| Container | `unfold/components/container.html` | Wrapper that sets a maximum content width. `class`. |
| Flex | `unfold/components/flex.html` | Flex layout for items. `class`, `col`. |
| Icon | `unfold/components/icon.html` | Icon element. `class`. |
| Navigation | `unfold/components/navigation.html` | List of navigation links. `class`, `items`. |
| Progress | `unfold/components/progress.html` | Progress bar. `class`, `value`, `title`, `description`; data can also supply segmented `items`. |
| Separator | `unfold/components/separator.html` | Horizontal separator. `class`. |
| Table | `unfold/components/table.html` | Table. `table`, `card_included`, `striped`; detail also documents `title` and `height`. |
| Text | `unfold/components/text.html` | Paragraph/text element. `class`. |
| Title | `unfold/components/title.html` | Heading element. `class`. |
| Tracker | `unfold/components/tracker.html` | Grid/heatmap/activity tracker. Catalog: `class`, `data`; page documents optional size `md` or `sm` via component context. |
| Layer | `unfold/components/layer.html` | Abstract wrapper for variables prepared by a component class. |

### Cohort path discrepancy

The introduction's component inventory lists `unfold/components/cohort.html`, while the dedicated [Cohort page](https://unfoldadmin.com/docs/components/cohort/) demonstrates `unfold/components/chart/cohort.html`. This is inconsistent in the official documentation. Check the installed package's template paths before choosing one; do not infer the correct path from the page title alone.

## Tracker: implementation implementation

The [Tracker page](https://unfoldadmin.com/docs/components/tracker/) describes a grid of data points useful for activity histories, heatmaps, and contribution-style summaries. It supports a list of item dictionaries. Each item can optionally define a color, tooltip, link, and extra CSS class. The component size can be `"md"` or `"sm"`.

### 1. Prepare tracker data

Example component class, ready to adapt to the project's model and permissions:

```python
# your_app/admin_components.py
from unfold.components import BaseComponent, register_component


@register_component
class TicketActivityTracker(BaseComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "data": [
                    {
                        "color": "bg-base-200 dark:bg-base-700",
                        "tooltip": "Monday: no activity",
                    },
                    {
                        "color": "bg-primary-400 dark:bg-primary-700",
                        "tooltip": "Tuesday: 4 updates",
                    },
                    {
                        "color": "bg-primary-600 dark:bg-primary-400",
                        "tooltip": "Wednesday: 11 updates",
                        "class": "ring-1 ring-base-300 dark:ring-base-600",
                    },
                ],
                "size": "md",
            }
        )
        return context
```

`color`, `tooltip`, `href`, and `class` are optional per the page examples. Use a Django-supported color utility class already present in the site's stylesheet; if the project compiles its own Tailwind CSS, ensure runtime-selected classes are retained in the output. `size` is passed through the component class context in the official example.

When deriving cells from records, limit the query to the period and data the admin is allowed to see. Aggregate in Python/database code before rendering; do not issue one query per cell. Keep tooltip text concise. Set `href` only to a safe, permission-checked destination; a link in the tracker does not grant access to its target.

### 2. Render it in a dashboard or custom admin template

```django
{% load i18n unfold %}

{% component "unfold/components/card.html" with title="Recent ticket activity" %}
    {% component "unfold/components/tracker.html" with component_class="TicketActivityTracker" %}
    {% endcomponent %}
{% endcomponent %}
```

The component class must be imported during Django startup so `@register_component` runs. A common location is an admin module already imported by the project; check its import/registration pattern rather than adding an unreferenced module. Alternatively, prepare the list in `DASHBOARD_CALLBACK` and pass it directly as `data=my_tracker_data` to the tracker component, as documented.

### Tracker data shape

```python
tracker_items = [
    {
        "color": "bg-primary-400 dark:bg-primary-700",  # optional cell color
        "tooltip": "Custom value 1",                     # optional hover text
        "href": "/admin/app/model/1/change/",             # optional link
        "class": "custom-class",                         # optional CSS class
    },
    {"color": "bg-base-200 dark:bg-base-700", "tooltip": "No activity"},
]
```

The docs show an ordered Python list of cells. Each cell can use a different style and tooltip to communicate intensity or state. They do not define a built-in numeric-to-color scale, date axis, or automatic data aggregation; calculate those in application code if needed.

## Other data-bearing components

### Cohort

The cohort component represents groups over time (for example, retention). The documented data shape is:

```python
cohort_data = {
    "headers": [
        {"title": "Week 0", "subtitle": "Optional"},
        {"title": "Week 1"},
    ],
    "rows": [
        {
            "header": {"title": "June cohort", "subtitle": "Optional"},
            "cols": [
                {"value": "100%", "subtitle": "Optional"},
                {"value": "72%"},
            ],
        },
    ],
}
```

Pass `data=cohort_data` directly or return it from a registered component class. Verify the actual template path using the note above.

### Table

The basic `table` argument is a dictionary with `headers` (column labels) and `rows` (a list of rows, each a list of cell values). Optional behavior includes stripes, wrapping it in a card, and a maximum height with scrolling. The docs also show nested rows using a row dictionary with `cols`, nested `table`, and optional `attrs`; nested header/cell objects may include `content` and `class`.

```python
table_data = {
    "headers": ["Name", "Status"],
    "rows": [["Example", "Active"], ["Another", "Pending"]],
}
```

```django
{% load unfold %}
{% component "unfold/components/card.html" with title="Records" %}
    {% component "unfold/components/table.html" with table=table_data card_included=1 striped=1 %}
    {% endcomponent %}
{% endcomponent %}
```

### Charts

Bar and line components use Chart.js. Supply a JSON-serializable Chart.js data object with `labels` and `datasets`; the docs examples serialize it with `json.dumps` in the component class. `height` is accepted by examples. The documented component parameters include `responsive` and `tooltip`, both defaulting to true. Dataset special keys include `displayYAxis`, `displayXAxis`, `maxTicksXLimit`, and `suffixYAxis`. Custom Chart.js `options` may be provided as JSON, but JavaScript functions are not supported in that payload.

## Remaining component details

- **Card:** `title`, `label`, `action`, `icon`, `footer`, `href`, `disable_border`, and `class`. It accepts nested child components; `action` can hold button markup captured in a template.
- **Button:** Renders as a button by default or as a link when `href` is supplied. Supports `variant` (`default`, `secondary`, `danger`, `ghost`), `size` (`sm`, `md`), `form`, `value`, `title`, `name`, `submit`, `extra_attrs`, and an `attrs` dictionary. Use semantic button/link behavior and avoid interpolating untrusted HTML into labels.
- **Link:** `href`, `icon`, `external`, and `class`. `external` opens a new tab and adds an external-link indicator. The URL may be omitted to show non-link content.
- **Progress:** Basic values include `value`, `title`, `description`, and `progress_class`. Segmented progress uses `items`, where each segment carries a title, numeric value, and styling class. Calculate and bound percentages in application code.
- **Layer:** Use with a registered component class to expose prepared variables to template code inside the layer block; useful when a page needs a custom composition rather than a single predefined visualization.
- **Container, flex, icon, navigation, separator, text, title:** These are utility/layout primitives listed on the introduction page. Use their tabled arguments above and inspect the rendered page for the desired nesting/layout; no dedicated deep-dive page was found in the documentation navigation.

## Official component pages

- [Components introduction and inventory](https://unfoldadmin.com/docs/components/introduction/)
- [Component classes](https://unfoldadmin.com/docs/components/component-class/)
- [Cohort](https://unfoldadmin.com/docs/components/cohort/)
- [Tracker](https://unfoldadmin.com/docs/components/tracker/)
- [Card](https://unfoldadmin.com/docs/components/card/)
- [Table](https://unfoldadmin.com/docs/components/table/)
- [Chart](https://unfoldadmin.com/docs/components/chart/)
- [Link](https://unfoldadmin.com/docs/components/link/)
- [Button](https://unfoldadmin.com/docs/components/button/)
- [Progress](https://unfoldadmin.com/docs/components/progress/)
- [Layer](https://unfoldadmin.com/docs/components/layer/)
