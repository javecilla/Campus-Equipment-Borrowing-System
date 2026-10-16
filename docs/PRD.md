# Product Requirements Document

## Status and authority

Planning baseline for the Campus Equipment Borrowing System. This document describes intended outcomes, not delivered features. [Project-Requirements.txt](Project-Requirements.txt) is the course requirements source; [Project-Members.txt](Project-Members.txt) is the source for people and the team schedule. Technical behavior belongs in [SRS.md](SRS.md).

## Problem and purpose

Campus equipment borrowing needs a consistent record of what is requested, which physical units are reserved or issued, who authorized each action, and whether units have been returned in usable condition. Without an enforced workflow, conflicting approvals and incomplete returns can make availability unreliable.

Provide one campus application that connects borrower requests to administrator operations and preserves the history of each physical unit.

## Goals and success measures

| Goal | Acceptance evidence |
| --- | --- |
| Keep physical availability accurate | Inventory totals reconcile across all five statuses after approval, cancellation, release, return, maintenance, and retirement |
| Prevent double allocation and issue | Two competing approvals for the last available unit produce exactly one successful reservation; repeated release creates no second loan |
| Make borrowing traceable | Borrower, asset codes, decisions, release, individual returns, and responsible admins can be traced through stored records and audit history |
| Enforce role and ownership boundaries | Basic users cannot access another user's records or perform admin actions, including direct HTTP requests |
| Support daily administration | Required dashboard cards, charts, reports, and CSV exports reflect changes to real transactions |
| Meet course learning outcomes | Working Django/ORM implementation, tests, ethical decisions, team contribution evidence, and individual demonstration segments |

## Users and stakeholders

The following personas are design assumptions derived from the brief; they are not research or interview findings.

| Persona or stakeholder | Need | Product access |
| --- | --- | --- |
| Campus borrower, such as a student | Find equipment, request a suitable quantity, and understand request/return status | `BASIC_USER` |
| Equipment administrator | Control availability, review requests, release units, handle returns and maintenance, and report on operations | `ADMIN` |
| Instructor or evaluator | Assess requirements, implementation, evidence, and individual understanding | Evaluation stakeholder; no additional application role |
| Six-member development team | Stable contracts, clear ownership, and reliable handoffs | Development responsibility; no additional application role |

## In-scope capabilities

| Area | Product capability | Source |
| --- | --- | --- |
| Accounts | Shared sign-in; registration and personal profile; admin activation/deactivation and account history | A1, U1 |
| Inventory | Categories, catalog items, physical units, archival, asset codes, and status counts | A2, A6 |
| Borrower portal | Search active equipment; submit one request containing one to three distinct items; track/cancel own eligible requests | U2–U4 |
| Approval | Review availability, record decisions and reasons, reserve specific units atomically | A3 |
| Release | Issue an approved request once and print a borrowing slip | A4 |
| Returns | Per-unit and partial returns, overdue labels, damaged-unit routing | A5 |
| Maintenance | Open/close maintenance, release repaired units, retain retired units as unavailable | A6 |
| Reporting | Four dashboard cards, two charts, date-filtered loan/overdue reports, CSV export | A7 |
| Governance | Searchable audit history and configurable quantity/duration limits | A8 |

The custom admin side receives approximately three quarters of development effort. Both roles need responsive navigation, understandable errors, empty states, and status text that does not rely on color.

## Main user journeys

1. A borrower signs in, searches active equipment, submits a valid request, and sees it as Pending. Submission does not reserve equipment.
2. An administrator reviews the request and either rejects it with a reason or approves it while reserving all required physical units.
3. Before issue, the borrower can cancel an eligible request. Approved cancellation releases every reservation.
4. An administrator releases an approved request, records its loan, and prints a slip identifying the borrower and issued asset codes.
5. An administrator records individual returns. Outstanding units keep the loan active; damaged units enter maintenance. The loan closes after its final return.
6. An administrator reviews live inventory, overdue loans, audit history, and reports and adjusts settings for new requests.

## Scope boundaries

No third account role, Django admin interface, generated admin package, payments, fines, procurement, or supplier portal. Public deployment, paid hosting, external APIs, email/SMS notifications, barcode hardware, mobile apps, and a separate REST backend are not required. They must not displace required work.

No production uptime, institutional adoption, or legal compliance certification is claimed. Professional judgment and policy evidence must be reviewed for the actual campus context before submission.

## Delivery and evidence

Use the priorities, owners, dependencies, demonstration dataset, and evidence deliverables in [tasks.md](tasks.md). The team target is October 24, 2026; the instructor controls the official submission date. Week 17 provides a 12-minute demonstration and 3-minute Q&A with an identifiable segment for every member.

Acceptance requires both role workflows, meaningful integration tests, the concurrency demonstration, and usable evidence. A screen mockup, static dashboard, or design document alone does not count as a completed feature.

## Risks and decisions still requiring evidence

| Risk or unresolved point | Planned response |
| --- | --- |
| The sequential schedule leaves little integration time | Stabilize schema and shared contracts first; track dependencies and handoffs in the backlog |
| Competing requests could reserve the same unit | Use the transaction and database constraint design in [architecture.md](architecture.md) |
| Borrower identities or maintenance notes could leak | Enforce server-side role/ownership checks and field-limited portal queries |
| Shared files can be overwritten by different agents | Maintain one current handoff; preserve other owners' entries and resolve conflicts before accepting updates |
| Campus privacy, retention, AI disclosure, and asset-use policies are not supplied | Assign evidence work rather than inventing policy text or claiming compliance |
| Library choices and performance have not been tested | Treat technical choices and SRS performance numbers as proposed targets until measured |
