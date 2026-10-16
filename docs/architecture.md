# System Architecture Design

## Status and proposed stack

This is the proposed architecture for future implementation. No modules shown here have been scaffolded. Behavioral authority is [SRS.md](SRS.md); persistence is specified in [db_design.md](db_design.md). The canonical [coding standards](coding-standards.md) define MTV responsibility boundaries and implementation/review rules.

Use a single server-rendered Django application with Python 3.13, Django 5.2 LTS, PostgreSQL 17, and Psycopg 3. Pin tested patch versions during implementation. Django 5.2 supports the proposed Python series and database; consult the [release notes](https://docs.djangoproject.com/en/5.2/releases/5.2/) and [database documentation](https://docs.djangoproject.com/en/5.2/ref/databases/).

HTML/CSS and minimal JavaScript serve both roles. Bootstrap and a chart library are permitted by the brief but have not been selected. Any library must be declared, justified, and licensed appropriately. There are no required external APIs, background workers, message brokers, or separate frontend services.

## Options comparison

| Option | Benefits | Limitations | Recommendation |
| --- | --- | --- | --- |
| Django monolith with SQLite | Simple local demonstration and few infrastructure dependencies | Django's `select_for_update()` does not lock SQLite rows; this design's concurrency proof cannot be assumed to work there | Allowed by the brief, but not the baseline for this locking design |
| Django monolith with PostgreSQL | Row locking and conditional uniqueness support fit per-unit reservations; shared transactional storage | Requires a database service and documented database configuration | Proposed baseline; verify competing approvals using the actual database |

A separate SPA/backend would add endpoint and client-state work without meeting an additional required capability. Keep Django templates and forms. Django documents row locking, SQLite limitations, and the need for `TransactionTestCase` in its [QuerySet reference](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-for-update).

## Model-template-view structure

```mermaid
flowchart LR
    Browser[Browser: basic user or admin] --> Router[Named Django URL routes]
    Router --> Checks[Session, active account, role and ownership checks]
    Checks --> Views[Custom function-based views]
    Views --> Forms[Django forms and formsets]
    Forms --> Services[Workflow service functions]
    Services --> Models[Django models and ORM]
    Models --> Database[(PostgreSQL)]
    Services --> Audit[Audit records in the same transaction]
    Audit --> Models
    Views --> Queries[Read-only ORM query functions]
    Queries --> Models
    Views --> Templates[Role base templates and shared components]
    Templates --> Browser
```

Views enforce HTTP/access rules and orchestrate forms, services, and rendering. Forms validate submitted shape and field-level values. Services own complete business transitions and database writes. Query functions own list, availability, dashboard, and reporting reads. Models/migrations enforce relational and row-level constraints. Templates render allowed data and named URLs; they do not enforce authorization.

The browser receives HTML, printable HTML, and CSV exports. Small JavaScript enhancements do not replace server validation. Authentication uses Django sessions and CSRF protection.

## Proposed modules and ownership

The following directory names are design contracts, not existing files.

| Module | Responsibility | Primary owner |
| --- | --- | --- |
| `config/` | Settings, root URL configuration, application entry points | Jerome with Alex for security settings |
| `accounts/` | Custom auth user/profile, login, role/active checks, account management, registration/profile | Alex; Ellyssa owns portal-facing registration/profile pages |
| `inventory/` | Categories, items, units, maintenance, availability queries | Kenneth |
| `borrowing/` | Requests/items, allocations, loans/loan units, returns, workflow services | Jerome defines shared models; Ralph owns submission/tracking; Margareth owns approval/release/return |
| `operations/` | Audit logs, settings, dashboard/report queries, exports | Jerome for audit/settings; Alex for dashboard/reports |
| `templates/` | `manage/base.html`, `portal/base.html`, shared components, feature templates | Feature owners; Ellyssa and Ralph coordinate integration |
| `static/` | CSS and small browser scripts | Feature owners |

Each Django app keeps models, forms, function-based views, URLs, service/query functions, migrations, and tests close to its feature. Split further only when actual file size or responsibility warrants it. Avoid a generic CRUD framework or unnecessary repository abstraction over Django ORM.

Define the custom user model before the first migration. All foreign keys reference the configured authentication model. Roles come from one field, never from Django admin flags or separate authentication systems. No `admin.site.urls`, built-in admin pages, or admin-generation packages.

## Transaction boundaries and lock order

Every state transition re-reads authoritative database state inside `transaction.atomic()`. Do not rely on availability previously rendered in a page.

For borrowing operations, use the shared order: borrower User row, BorrowRequest row, existing Loan row where applicable, CatalogItem rows in ascending ID order where catalog eligibility is checked, then EquipmentUnit rows in ascending ID order. Lock and re-read related allocation/loan-unit records as needed after their parent and unit locks. Do not acquire the same shared locks in a reverse order in another service. Catalog archival uses category/item locks consistently; account deactivation uses the User lock, so a concurrent transaction cannot pass a stale active-account check.

1. **Submit:** validate the entire formset, lock/recheck borrower and eligible catalog records, capture settings, and create the request/items atomically. No allocations are created.
2. **Approve:** lock borrower, request, eligible category/item records in a consistent parent-before-child order, and candidate units. Recheck Pending state and availability after acquiring locks. Select exactly the requested quantity per item. Insert allocations, set unit statuses and decision fields, and append audit data in one transaction. Any shortage rolls everything back.
3. **Cancel:** lock the owner, request, and reserved units. Recheck owner/state, end reservations, set units Available, set Cancelled, and append audit data together.
4. **Release:** lock borrower, approved request, and assigned units. Validate date and complete allocation sets. Create the one Loan and all LoanUnits, record allocation release timestamps, set units Issued/request Issued, and audit. Allocations remain active until return.
5. **Return:** lock borrower, request, loan, and returning units. Check membership and absent return records; create returns, end allocations, and update unit/request/loan states. Damaged returns open maintenance within this same transaction. Close the loan only if no outstanding unit remains.
6. **Maintenance:** lock the unit and its open maintenance record. Enforce its current inventory state and record opening/repair/retirement plus audit atomically. This service must not subsequently acquire borrowing-parent locks.
7. **Settings/account/catalog changes:** validate allowlisted fields and record the business change and audit together. Request submission reads a single consistent settings row; settings edits do not rewrite existing requests.

When approval needs both category and catalog locks, lock categories in ascending ID order before catalog items; submission uses the same order. Archiving a category checks its child records under that order. This refines the general lock sequence above. Implement one shared lock convention and verify it in review rather than adding independent locking code per view.

A partial unique constraint on `UnitAllocation.unit_id` while `ended_at IS NULL` protects exclusivity in addition to locks. A unique Loan request reference and unique ReturnRecord loan-unit reference prevent duplicate issue/return. Cross-table invariants remain service responsibilities; see [db_design.md](db_design.md).

Never silently skip an unavailable requested quantity or convert an operational conflict into success. Translate recognized validation/state conflicts into explicit errors. Unexpected database errors remain failures. Retrying a mutating transaction after an ambiguous commit is unsafe without a verified idempotency strategy and is not part of this baseline.

## Workflow view

```mermaid
stateDiagram-v2
    [*] --> Pending
    Pending --> Approved: Reserve all units
    Pending --> Rejected: Record reason
    Pending --> Cancelled: Owner cancels
    Approved --> Cancelled: Free reservations
    Approved --> Issued: Release once
    Issued --> PartiallyReturned: Some units returned
    Issued --> Returned: All units returned
    PartiallyReturned --> Returned: Remaining units returned
    Rejected --> [*]
    Cancelled --> [*]
    Returned --> [*]
```

Overdue is calculated from outstanding loan units and the local date, so it is not a node in the persisted request workflow. Unit maintenance/retirement transitions are separate from request status.

## Reads, reporting, and privacy

Query ORM data directly for the required live cards/charts/reports. Use `select_related`, `prefetch_related`, filtering, ordering, pagination, and aggregate/annotate queries where appropriate. Avoid cached counters initially. Query counts independently or aggregate carefully so joining returns does not multiply issued quantities.

Portal query functions take the signed-in owner explicitly and return only allowed fields. Management query functions require admin authorization at the view boundary. CSV and printable slips receive the same access checks as their corresponding pages. Operational notes are never placed into portal template context.

## Configuration and technical limits

[.env.example](../.env.example) is the canonical environment-key inventory. [DEV.md](../DEV.md) explains the private `.env.local` and shared local MCP setup. The MCP launch command explicitly loads that file through Node; its `MCP_DATABASE_URL` is separate from the future application's DB_* settings. No Django configuration loader or application settings code exists yet; placing values in `.env.local` alone does not configure Django.

Use timezone-aware timestamps and Asia/Manila calendar dates for due dates. Quantity/duration limits are persisted SystemSetting values, not duplicated environment variables. A single local database-backed demonstration is sufficient; high availability and hosting are outside this design.

PostgreSQL is required to validate the selected locking strategy. SQLite-only tests cannot establish row-lock correctness. Use separate database connections and `TransactionTestCase` for competing approvals. Workflows, migrations, schema constraints, performance, and backup/restore remain unverified until implementation and execution.
