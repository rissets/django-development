# Design system for Django applications

This is a reusable design specification workflow, not a fixed brand or CSS framework. Django's architecture philosophies concern code boundaries; visual design requires a separate UI system. Preserve existing design/PRD/reference images unless redesign is requested.

## Define two surfaces deliberately

Admin uses Unfold's components, settings, and layout. Public/product HTML may use project-native CSS, Tailwind, Bootstrap, or an established component stack. Share semantic brand decisions while keeping CSS bundles and implementation scoped. Do not impose the admin layout on customer journeys or load competing global resets into Unfold.

For a new UI, record decisions in the project's existing design source or a concise `DESIGN.md`: audience/tasks; information architecture; token names; typography/spacing; light/dark surfaces; component anatomy/states; responsive behavior; content/locale; and acceptance examples. Only create a new design file when a design task needs one; a backend fix should not generate a redesign artifact.

## Tokens and reusable components

| Token family | Specify |
|---|---|
| Color | Semantic surface/text/border/accent/success/warning/error and each theme |
| Typography | Body/label/title/metric roles, readable line-height, numeric alignment |
| Spacing | Small documented scale used in forms, groups, cards, tables |
| Shape | Consistent radius/borders/shadows based on the existing visual system |
| Interaction | Visible focus, hover/active/disabled/pending, reduced-motion behavior |
| Layout | Content width, density, breakpoints, table overflow, navigation |

Numbers are local design choices, not Django requirements. Reuse template includes/tags/components for buttons, fields, error summary, pagination, badge, empty state, table, and metric card. Separate data calculation from display. A UI component API should define required inputs and states rather than proliferating nearly identical templates.

The GOV.UK Design System provides task-focused patterns for fields, errors, tables, pagination, breadcrumbs, and accessible navigation. Use the behavior/anatomy as research; do not copy its government brand into another product. [Component catalog](https://design-system.service.gov.uk/components/)

## Accessibility acceptance

Aim for WCAG 2.2 AA when applicable: semantic landmarks/headings, visible labels, keyboard operation, visible focus, sufficient contrast, understandable errors, and responsive reflow. Normal text contrast is at least 4.5:1; large text 3:1; relevant non-text controls/focus indicators need appropriate contrast. Minimum target size is 24 by 24 CSS pixels subject to documented exceptions; larger practical controls often help. Do not treat these numbers as a complete compliance audit. [WCAG quick reference](https://www.w3.org/WAI/WCAG22/quickref/)

Check errors beyond red borders: associate inline messages with fields and expose a useful summary for multi-field failures. Use labels/instructions for units and formats; preserve submitted values. Do not signal status through color alone. Icon-only controls need accessible names; dialogs need focus management and keyboard dismissal. Announce async status appropriately without repeatedly overwhelming screen readers.

At narrow viewport widths, forms remain usable and actions reachable. Tables may use labeled horizontal scrolling or a deliberate alternate layout; charts need readable labels and an accessible data summary. Check long translated text, large text/zoom, theme contrast, and reduced motion. Automated checks complement manual keyboard/browser inspection.

## Workflow design

- Lists: search/filter/order/pagination and persistent URL state; meaningful primary columns and explicit actions.
- Details: identity/status/context then primary action and supporting history; link every actionable record to a real destination.
- Forms: group by user decisions, distinguish optional/required, retain errors/input, make successful result evident.
- Dashboard: define metric period/unit/source/freshness; match drill-down filters to displayed counts; show missing data truthfully.
- Destructive transitions: use existing confirmation pattern and explain consequences; server rechecks current authorization/state.
- Permission-denied state: do not leak private object details; show an appropriate next action when one exists.

Every relevant component must support populated, empty, pending, invalid, success, forbidden, and failed states. Synthetic fixtures are labeled. Align content language/date/currency with requirements; store aware timestamps and render the user's/project timezone.

## Implementation-specific choices

Use the actual frontend's build pipeline. CSS utility names composed dynamically may require explicit source/safelist handling; verify compiled output. HTMX swaps should preserve/restore focus and compatible error rendering. Crispy forms is optional and requires a compatible separately installed template pack. Unfold has its own version-specific styling rules; [admin guidance](unfold-admin.md) applies there.

Before declaring UI acceptance, open the actual authenticated path at representative viewport widths, check keyboard/error/pending states and browser console, and confirm actions persist correct state. Screenshots alone do not prove interactive behavior.

## Proses membangun design system

1. Inventaris screenshot/reference/komponen existing dan constraints produk. Catat audience, tugas yang paling sering, data density, perangkat, brand, bahasa, dan role.
2. Tentukan page archetypes: dashboard, list/search, detail, form, settings, login, empty/error. Petakan navigation dan primary action tiap halaman.
3. Tetapkan semantic tokens dan component contracts. Pilih satu typography/spacing/density baseline dari design existing; jangan menghasilkan palet/komponen generik yang bertentangan dengan reference.
4. Bangun satu halaman nyata dengan populated/empty/error states, lalu validasi browser/responsive/keyboard sebelum memperbanyak halaman.
5. Extract markup dan data interface yang benar-benar berulang. Dokumentasikan variants, states, permitted composition, dan ownership CSS.
6. Terapkan Unfold settings/components untuk admin; public UI memakai stack yang dipilih. Sinkronkan semantic brand, bukan seluruh global stylesheet.

## Contoh token publik yang scoped

Contoh berikut untuk aplikasi baru tanpa brand existing. Nilai adalah starter keputusan visual, bukan keharusan. Uji contrast pada warna final/state final, termasuk hover/dark mode/disabled.

```css
[data-app-shell] {
  --surface: #ffffff;
  --surface-muted: #f8fafc;
  --text: #0f172a;
  --text-muted: #475569;
  --border: #cbd5e1;
  --accent: #1d4ed8;
  --on-accent: #ffffff;
  --danger: #b91c1c;
  --focus: #1d4ed8;
  --space-1: .25rem;
  --space-2: .5rem;
  --space-3: .75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --radius: .5rem;
  color: var(--text);
  background: var(--surface);
  font: 1rem/1.5 system-ui, sans-serif;
}
[data-app-shell][data-theme="dark"] {
  --surface: #0f172a;
  --surface-muted: #1e293b;
  --text: #f8fafc;
  --text-muted: #cbd5e1;
  --border: #64748b;
  --accent: #93c5fd;
  --on-accent: #0f172a;
  --danger: #fca5a5;
  --focus: #93c5fd;
}
[data-app-shell] .button-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.75rem;
  padding: var(--space-2) var(--space-4);
  border: 1px solid transparent;
  border-radius: var(--radius);
  color: var(--on-accent);
  background: var(--accent);
  font: inherit;
}
[data-app-shell] :focus-visible {
  outline: 3px solid var(--focus);
  outline-offset: 3px;
}
[data-app-shell] .content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 20rem), 1fr));
  gap: var(--space-6);
}
@media (prefers-reduced-motion: reduce) {
  [data-app-shell] * { animation: none; transition: none; scroll-behavior: auto; }
}
```

Scoping mencegah CSS product menimpa widgets Unfold. Tambahkan state hover/active/loading/disabled dengan contrast/semantics yang benar; opacity bukan satu-satunya penanda disabled. Dark preference bisa mengikuti user/system, dengan toggle yang persist dan label accessible bila produk memerlukannya.

## Contract komponen

| Komponen | Data/interface | State dan acceptance |
|---|---|---|
| Button/link | Label, action/href, variant, pending | Link untuk navigasi; button untuk aksi; disable hanya sesuai state |
| Field | ID/name, label, value, required, hint, errors | Bound value dipertahankan; label/error association; no placeholder-only label |
| Error summary | Field links dan non-field errors | Fokus/announcement yang tepat; tidak mengulang noise pada setiap ketikan |
| Badge/status | Text, semantic status | Warna bukan satu-satunya informasi; state domain konsisten |
| Table | Headers, rows, links, order, page | Header semantic; numeric units; bounded result; responsive overflow |
| Pagination | Current page, next/prev URLs | URL filter tetap; current item jelas; no broken links |
| Metric card | Value/unit/period/freshness/source/link | Unknown bukan zero; drill-down konsisten |
| Chart | Series/axes/units + data summary | Tidak memotong misleading axis; color readable; accessible alternative |
| Modal/dialog | Title/content/actions | Focus trap/return, keyboard dismissal, server validation |
| Empty/error panel | Explanation dan available next action | Role-aware, truthful, tidak membuat data palsu |

Component context dijelaskan dalam templates/tags atau reference proyek; jangan menciptakan parameter arbitrary yang tidak digunakan. `include ... only` dapat membantu membatasi context leakage bila sesuai template. Untuk markup trusted/generated gunakan pendekatan Django escaping; tetap hindari untrusted HTML dalam attrs.

## Form yang dapat dipakai

Urutkan menurut cara pengguna mengambil keputusan, bukan database column order. Beri label bahasa pengguna, optional markers konsisten, format/unit examples, dan autofill sesuai field. Required business rule tetap server-side. Field conditional tidak menghapus validation atau permission. Untuk long forms pilih grouping/tabs/steps hanya jika membantu; error harus membawa user ke lokasi field yang benar.

Maintain current values saat validation failure, generic failure, dan session expiry bila memungkinkan secara aman. Preview destructive transitions dan hasil sebenarnya; jangan memakai toast sebagai satu-satunya error untuk form panjang. Sensitive fields tidak diprefill dari logs/URL.

## Dashboard dan data visualization

Definisikan pertanyaan operasional untuk setiap chart/metric. Periode/timezone, denominator, comparison baseline, zero vs missing, freshness, dan source harus konsisten. Tampilkan authorized data; aggregasi global tidak boleh bocor ke role terbatas. Kombinasikan KPI, trend/comparison bila data mendukung, table actionable, dan real navigation. Pengelompokan cards mengikuti meaning, bukan kebutuhan mengisi grid.

Gunakan Tracker untuk intensity/activity dan Cohort untuk group-over-time; flow/process diagram memerlukan diagram yang sesuai. Tidak semua dashboard membutuhkan semua visual. Dummy values hanya untuk demonstrasi yang eksplisit synthetic; release production menampilkan failure/empty state bila backend tidak tersedia.

## Responsive dan performance

Pilih breakpoint dari layout/data, bukan nama perangkat. Pada viewport sempit, side navigation memiliki mekanisme yang dapat dioperasikan keyboard, actions tidak hilang, label/error tidak terpotong, dan tabel memiliki scroll region yang diketahui pengguna. Mobile tidak harus menampilkan semua desktop columns sekaligus; pilih informasi utama dan akses detail.

Batasi payload dan rows; hindari giant dropdown, chart ribuan points tanpa agregasi, dan request per card/row jika satu scoped aggregate cukup. Static production memakai compiled assets/hash/cache policy. Optimize setelah ukur relevant page/user path; jangan mengganti seluruh styling untuk memperbaiki satu request lambat.

## Mapping ke Django/Unfold

Public: `base.html` + includes/tag component + native Form widgets/custom render sesuai stack. API frontend: component system di frontend dengan error/schema contract backend. Admin: `UNFOLD` branding/colors, documented display labels, components, fieldsets/tabs, action/dialog dan integration widgets. Jangan menyalin warna format lama ke Unfold version dengan token syntax berbeda.

Catat untuk setiap UI change: design source, component/state changed, actor/path, before/after evidence bila perlu, viewport/theme/keyboard checks, console/network failure, serta persisted outcome. Full WCAG audit berbeda dari focused checks; laporkan cakupan dengan tepat.
