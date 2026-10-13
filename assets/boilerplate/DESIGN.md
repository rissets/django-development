# Design

Operate-mode interface inherited from the skill's design-system guide. This starter does not introduce a new brand direction. Public UI uses a quiet, readable list/form/detail layout; staff UI preserves Unfold's native components and light/dark themes.

Semantic light tokens: surface white, text #0f172a, muted #475569, border #cbd5e1, action/focus #1d4ed8. Dark tokens: surface #0f172a, text #f8fafc, muted #cbd5e1, action #93c5fd. Public styles are scoped by data-app-shell; no shared reset overrides admin.

Body system UI 16px, line-height 1.5; headings vary 1.8–2.4rem. Controls minimum 44px tall; fields have visible labels, bound values, inline/non-field errors, and focus rings. Status always has text. No decorative photos/assets are needed for an operational starter.

List: search/status filter, stable pagination, record links, truthful empty/no-match states. Detail: name/status, dates/timezone, edit and POST-only lifecycle actions. Forms: server validation, clear submit/cancel, pending state reset on browser back. Nav contains only active mode/role destinations.

Responsive: header wraps, filter fields stack, timestamps move off list at narrow width while detail retains them, table region is keyboard reachable. Reduced-motion respected. Theme toggle persists optional preference and works without external services.

Unfold: permission-scoped metrics/trend/table, model filters/display labels, confirmation action/custom page, real drill-down links. No charts use invented data. Keyboard, console, desktop/mobile overflow and authenticated outcomes must be checked after each product extension.
