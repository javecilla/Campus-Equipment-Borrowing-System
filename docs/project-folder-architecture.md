# Project Folder Architecture

Use this guide to find the files involved in a page and decide where a new feature belongs. It describes file placement; [architecture.md](architecture.md) owns system design, [coding-standards.md](coding-standards.md#what-mtv-means) owns MTV responsibilities, and [api_spec.md](api_spec.md) owns route names and form contracts.

**Existing** means the path is present in this checkout. **Planned** means a proposed location to create when the assigned feature needs it. **Generated** means local build output, excluded from Git. The planned files below have not been scaffolded. Check [HANDOFF.md](../HANDOFF.md) and [the backlog](tasks.md) for implementation and main-integration readiness.

## Folder map

The same small app structure applies to accounts, inventory, borrowing, and operations. Keep Python code in its feature app and shared page templates under the root `templates/` directory.

```text
Campus-Equipment-Borrowing-System/
├── config/                                      [existing]
│   ├── environment.py                           [existing] private configuration reader
│   ├── settings.py                              [existing] installed apps, DB, templates, assets
│   ├── urls.py                                  [existing] app route mounting and debug preview /test
│   ├── views.py                                 [existing] debug-only frontend preview
│   ├── tests.py                                 [existing] configuration/bootstrap checks
│   ├── asgi.py                                  [existing]
│   └── wsgi.py                                  [existing]
│
├── accounts/                                    [existing]
│   ├── models.py                                [existing] User and Profile
│   ├── migrations/                              [existing]
│   ├── views.py                                 [existing] login/logout/home, registration and T05 account handlers
│   ├── portal_views.py                          [existing] borrower profile editing and pending portal modules
│   ├── forms.py                                 [existing] login, registration/profile, account search and status confirmation
│   ├── urls.py, portal_urls.py                  [existing] account/portal auth routes
│   ├── access.py, middleware.py                 [existing] active/role/owner checks
│   ├── services.py                              [existing] admin bootstrap, registration and audited profile/status writes
│   ├── seeding.py                               [existing] atomic two-account auth test setup
│   ├── queries.py                               [existing] account/history reads
│   ├── tests/                                   [existing] authentication, registration/profile and access checks
│   └── management/commands/                     [existing] admin setup and auth test seed commands
│
├── inventory/                                   [existing]
│   ├── models.py                                [existing] catalog, units, maintenance
│   ├── migrations/                              [existing]
│   ├── views.py                                 [existing] category/catalog/unit and maintenance list/detail/open/close handlers
│   ├── portal_views.py                          [existing] borrower catalog list/detail and protected photos
│   ├── forms.py                                 [existing] catalog/unit/maintenance forms and portal search
│   ├── manage_urls.py                           [existing] catalog/unit and maintenance list/detail/open/close routes
│   ├── services.py                              [existing] audited catalog/unit writes and maintenance open/close
│   ├── queries.py                               [existing] catalog/unit/maintenance selection, history and derived counts
│   ├── photo_views.py / restore_views.py            [existing] protected photo and restoration handlers
│   ├── photo_services.py / photos.py                [existing] audited storage and image validation
│   ├── photo_forms.py                              [existing] upload field validation
│   └── tests/                                   [existing] catalog/restore/photo/unit/portal/maintenance integration checks
│
├── borrowing/                                   [existing]
│   ├── models.py                                [existing] requests, allocations, loans, returns
│   ├── migrations/                              [existing]
│   ├── views.py                                 [existing] borrower submission/history/cancellation; admin workflows remain planned
│   ├── forms.py                                 [existing] request submission/filter/confirmation; return forms planned
│   ├── manage_urls.py                           [existing] protected administrator request/loan placeholders
│   ├── services.py                              [existing] atomic submission/cancellation; approval/issue/return planned
│   ├── queries.py                               [existing] owner-scoped request/loan history reads
│   ├── tests/                                   [existing] request submission/tracking; remaining workflows planned
│   └── management/commands/                     [planned] controlled demonstration seed
│
├── operations/                                  [existing]
│   ├── models.py                                [existing] SystemSetting and AuditLog
│   ├── migrations/                              [existing]
│   ├── audit.py                                 [existing] shared transactional audit writer
│   ├── locking.py                               [existing] shared lock helpers and order
│   ├── validation.py                            [existing] pure item/limit/date validation
│   ├── services.py                              [existing] audited settings update
│   ├── queries.py                               [existing] loan-limit and audit reads; reporting comes later
│   ├── tests/                                   [existing] foundation integration checks
│   ├── views.py                                 [existing] settings/audit/profile handlers and dashboard placeholder
│   ├── workspace_views.py                       [existing] pending report presentation
│   ├── forms.py                                 [existing] settings and audit filter inputs
│   ├── templatetags/assets.py                      [existing] content-versioned compiled asset URLs
│   └── urls.py                                  [existing] settings/audit/profile and protected dashboard/report routes
│
├── templates/                                   [existing] shared root template directory
│   ├── base.html                                [existing] document shell and compiled CSS
│   ├── dev/frontend-test.html                    [existing] Tailwind/font preview
│   ├── dev/index.html                            [existing] historical development navigation
│   ├── operations/manage/base.html              [existing] custom administrator navigation layout
│   ├── accounts/portal/base.html                [existing] basic-user navigation layout
│   ├── components/                              [existing] workspace/navigation/messages/brand/logout
│   ├── accounts/                                [existing] login and account feature pages
│   │   ├── login.html                           [existing]
│   │   ├── manage/                              [existing] T05 account management pages
│   │   ├── register.html                        [existing] T09 public borrower registration
│   │   └── portal/                              [existing] protected home/profile and T12 request/loan history
│   ├── inventory/                               [existing] catalog/unit/portal and maintenance pages
│   │   ├── manage/                              [existing] catalog/photo/restore/unit and maintenance pages
│   │   └── portal/                              [existing] equipment browsing list/detail pages
│   ├── borrowing/                               [existing/planned] submission/history/cancellation present; admin workflows planned
│   │   ├── manage/                              [planned] review, release, returns, slips
│   │   └── portal/                              [existing] borrower request/loan history and cancellation
│   └── operations/manage/                       [existing/planned] settings/audit pages; live dashboard/reports planned
│
├── static/                                      [existing] shared source static files
│   ├── css/fonts.css                            [existing] local font declarations and typography
│   ├── css/app.css                              [existing] Tailwind entry point/theme/source scan
│   ├── fonts/                                   [existing] DM Sans/Poppins and license notices
│   ├── images/                                  [existing] branding, default equipment photo and setup screenshots
│   ├── js/frontend-test.js                       [existing] preview font-load check
│   ├── js/account-menu.js                        [existing] account disclosure dismissal behavior
│   ├── js/equipment-photo.js                     [existing] local image preview and selection removal
│   └── build/                                   [generated] ignored CSS/browser modules/chunks
├── package.json                                 [existing] npm dependencies/build/watch commands
├── package-lock.json                            [existing] exact npm dependency graph
├── docs/                                        [existing] canonical requirements/design guides
├── handoffs/                                    [existing] dated work evidence
└── manage.py                                    [existing] Django management entry point
```

The root also contains the setup/review documents, dependency files, and private local environment described in [DEV.md](../DEV.md#first-time-setup). Python package `__init__.py` files are omitted from this map. Local `media/equipment/` contains optional uploads and is ignored by Git, along with `.idea/` IDE settings. `staticfiles/` is generated collection output, while `.venv/` and `.env.local` are private local setup; none is a place to add application pages.

## Where views and page HTML go

A **view** is a Python request handler in the relevant app's `views.py`. The page's **HTML** is a template. For example, an inventory management page uses `inventory/views.py` and a template under `templates/inventory/manage/`.

The role prefix selects the audience; the feature app selects the Python module. Real basic-user equipment handlers belong in `inventory/`, and borrowing handlers in `borrowing/`. T10 equipment handlers are in `inventory/portal_views.py`, mounted through `accounts/portal_urls.py`. T11 request creation and T12 borrower request/loan history, detail and cancellation handlers live in `borrowing/views.py`; owner-scoped read helpers live in `borrowing/queries.py` and the atomic cancellation workflow in `borrowing/services.py`. The portal URLs are mounted through `accounts/portal_urls.py`. Feature pages extend the existing `operations/manage/base.html` or `accounts/portal/base.html` and fill `workspace_content`; both inherit `components/workspace.html` and the `base.html` document/asset shell. The [coding guide](coding-standards.md#tailwind-styling-pattern) defines the shared layout pattern.

T16's maintenance files are present and integrated, with review fixes outstanding; see [current evidence](tasks.md#verified-task-evidence). These page placements include existing account/settings/audit/inventory pages and planned borrowing examples; route names come from the HTTP contract:

| Page | Python view location | Template location | Contracted URL name |
| --- | --- | --- | --- |
| Sign in | `accounts/views.py` | `templates/accounts/login.html` | `accounts:login` |
| Register a borrower | `accounts/views.py` | `templates/accounts/register.html` | `accounts:register` |
| Edit own profile | `accounts/portal_views.py` | `templates/accounts/portal/profile.html` | `portal:profile` |
| Manage physical units | `inventory/views.py` | `templates/inventory/manage/unit_list.html` | `inventory_manage:unit-list` |
| Manage maintenance | `inventory/views.py` | `templates/inventory/manage/maintenance_list.html`, `maintenance_detail.html`, `maintenance_form.html`, `maintenance_close.html` | `inventory_manage:maintenance-list`, `maintenance-detail`, `maintenance-create`, `maintenance-close` |
| Browse equipment | `inventory/portal_views.py` | `templates/inventory/portal/equipment_list.html` | `portal:equipment-list` |
| Submit a request | `borrowing/views.py` | `templates/borrowing/portal/request_form.html` | `portal:request-create` |
| View/cancel own requests | `borrowing/views.py` | `templates/accounts/portal/request_list.html` | `portal:request-list` |
| Track own request/loan | `borrowing/views.py` | `templates/accounts/portal/request_detail.html` and `loan_detail.html` | `portal:request-detail`, `portal:loan-detail` |
| Approve a request | `borrowing/views.py` | `templates/borrowing/manage/request_approve.html` | `borrowing_manage:request-approve` |
| Record returns | `borrowing/views.py` | `templates/borrowing/manage/return_form.html` | `borrowing_manage:return-create` |
| Edit operational settings | `operations/views.py` | `templates/operations/manage/settings_form.html` | `operations:settings` |
| View audit history | `operations/views.py` | `templates/operations/manage/audit_list.html` | `operations:audit-list` |
| View the admin dashboard | `operations/views.py` | `templates/operations/manage/dashboard.html` | `operations:dashboard` |

When rendering the unit list, the template name passed to Django would be `inventory/manage/unit_list.html`, without the leading `templates/`. [config/settings.py](../config/settings.py) already searches the root `templates/` directory. Its `APP_DIRS=True` also supports app-local templates, but this shared map uses one root layout to keep team page locations consistent.

## How a page connects

For the implemented physical-unit list, the file flow is:

```text
Browser: GET /manage/units/
    -> config/urls.py                 root URL mounting
    -> inventory/manage_urls.py       named unit-list route
    -> inventory/views.py             method/access checks and HTTP response
    -> inventory/queries.py           read related inventory models
    -> inventory/models.py            ORM data and constraints
    -> inventory/manage/unit_list.html
         extends operations/manage/base.html
    -> HTML response to the browser
```

For a form that changes data, the view binds the app's `forms.py` and calls the relevant action in `services.py`. Borrowing services reuse the existing [lock helpers](../operations/locking.py), [audit writer](../operations/audit.py), and [pure validation](../operations/validation.py). The full responsibility split and transaction rules remain in [the coding guide](coding-standards.md#how-a-workflow-crosses-mtv) and [system architecture](architecture.md#transaction-boundaries-and-lock-order).

## Adding a page

1. Find the assigned task and accepted prerequisites in [tasks.md](tasks.md) and [PLAN.md](../PLAN.md). Use [api_spec.md](api_spec.md) for its route, namespace, access, form inputs, and response behavior.
2. Choose the feature app from the page table. Add its request handler in `views.py`. Put allowed form fields in `forms.py`, reads in `queries.py`, and the complete write action in `services.py` as needed. Create only the layers this feature uses.
3. Add the named route and mount it through `config/urls.py`. Management namespaces such as `inventory_manage` and `borrowing_manage` are separate from their `/manage/` path prefix. The `portal:*` names span accounts, inventory, and borrowing: coordinate one shared `portal` namespace in the root routing, referring to those feature views. Do not independently mount several competing `portal` namespaces.
4. Create the feature HTML under the matching `templates/<app>/manage/` or `templates/<app>/portal/` path, extending its role base. Add reusable fragments under `templates/components/`. The base-template owners establish shared block names and navigation as their tasks are implemented.
5. Add CSS/images/scripts under `static/` when needed. Custom base templates load the existing `css/fonts.css` through Django's static tag; the exact include and font paths are in [DEV.md](../DEV.md#fonts-and-static-assets).
6. Add meaningful checks beside the feature in its `tests/` directory, run [the configured commands](../DEV.md#before-handing-over-work), then follow the [handoff workflow](../.agents/skills/project-handoff/SKILL.md). A new persistent field or constraint also needs an app migration.

The shared Django authentication/access contract is integrated through T04 (PR #9, `cb96319`) in `accounts/access.py` and `accounts/middleware.py`. Views for later tasks reuse that interface after their owners sync main and verify the remaining task prerequisites; this folder guide does not authorize implementation.

## Which file should I edit?

| Change needed | Start here |
| --- | --- |
| Add page markup, labels, or an empty state | The feature template under `templates/<app>/<audience>/` |
| Add a URL or choose its handler | App `urls.py` and the root mount in `config/urls.py`; coordinate shared portal routing |
| Handle GET/POST and return HTML/redirect/download | App `views.py` |
| Parse and validate submitted fields | App `forms.py`, reusing existing pure helpers where applicable |
| Read/filter/search/paginate related data | App `queries.py` |
| Perform one business action and audit it atomically | App `services.py` |
| Change stored fields, indexes, or row constraints | App `models.py` plus a new migration |
| Change shared typography or static styling | `static/css/`; font usage is documented in DEV.md |
| Verify a feature's observable behavior | App `tests/`; existing foundation tests are in `operations/tests/` |

Use [coding-standards.md](coding-standards.md) for the detailed rules and [Project-Members.txt](Project-Members.txt) for ownership. This map adds no new app, role, endpoint, or feature implementation.
