# Student OS Complete Remake Prompt Pack

**Prepared by Manus AI**

This document is a prompt system for rebuilding the existing Student OS application into a calm, intelligent, focused, trustworthy, premium academic command center. It is intentionally written as a sequence of prompts rather than one vague “make it modern” instruction. The structure follows the referenced video’s core method: define the product world, specify typography and whitespace, establish a color system, describe the primary task surface, add concrete constraints, and iterate through focused refinement passes [1].

> **Working principle:** Do not ask an AI coding agent to “make Student OS look better.” Give it a product role, an observed source-of-truth codebase, a visual world, measurable UX goals, explicit technical constraints, and verification criteria.

---

## How to use this pack

Use the prompts in order. Start with the **Master Remake Prompt**, then run the **Forensic Audit Prompt** if the agent has not already inspected the repository. After that, use the **Product and UX Prompt**, **Visual Design Prompt**, **Information Architecture Prompt**, and the feature-specific prompts. Finish each implementation phase with the **QA and Truthfulness Prompt** and use the refinement prompts when the result feels generic, crowded, or visually inconsistent.

Do not paste every prompt into one conversation at once. The prompts are deliberately separated so that the coding agent must reason about the existing application before changing it, and so that each change remains reviewable.

| Prompt | Purpose | Best time to use |
|---|---|---|
| Master Remake Prompt | Establishes the overall role, outcome, constraints, and product direction | First message to the coding agent |
| Forensic Audit Prompt | Forces a complete inspection of the existing repository | Before any implementation |
| Product and UX Prompt | Converts Student OS from a broad portal into a focused academic command center | After the audit |
| Visual Design Prompt | Defines the product world, typography, color, whitespace, component language, and motion | Before styling work |
| Information Architecture Prompt | Reorganizes navigation around student intent and next actions | Before route/layout work |
| Student Dashboard Prompt | Remakes the core student experience | First major feature pass |
| Academic Work Prompt | Remakes courses, assignments, submissions, grades, and attendance | Second feature pass |
| Staff and Admin Prompt | Preserves and clarifies operational workflows without letting them dominate student UX | Staff/admin pass |
| AI Predictor Prompt | Makes the existing predictor useful, honest, and state-aware | Predictor pass |
| Mobile and Accessibility Prompt | Ensures the experience works on small screens and with assistive technology | Before release candidate |
| Engineering Integrity Prompt | Prevents fabricated data, fake integrations, and client-side secrets | Apply to every implementation pass |
| QA and Verification Prompt | Tests routes, permissions, persistence, error states, and visual regressions | After every major phase |
| Refinement Prompts | Diagnose and fix specific quality problems | During iteration |

---

# 1. Master Remake Prompt

Copy and paste the following as the first prompt to the coding agent.

```text
You are the lead product architect, senior full-stack engineer, UX designer, visual designer, accessibility specialist, and QA engineer responsible for completely remaking the existing Student OS application.

Student OS is an academic command center for serious students. Its purpose is to turn scattered academic responsibilities into one clear next action. The product should feel calm, intelligent, focused, trustworthy, and premium. It must not look like a generic AI-generated dashboard, a school ERP, a marketing template, or a collection of unrelated admin screens.

SOURCE OF TRUTH

The existing repository is the source of truth for the current implementation. Inspect the actual repository before changing anything. Do not assume that the current implementation matches the intended product. Do not discard working functionality merely because the current UI is weak. Preserve valuable backend behavior and rebuild weak, confusing, duplicated, or incomplete parts deliberately.

The audited repository is a Flask/Jinja application with:
- Flask and Flask-Login authentication.
- SQLite for local persistence with optional PostgreSQL support.
- Hand-written SQL through db.py and schema.sql.
- Jinja templates and static CSS in static/css/style.css.
- Blueprint routes under routes/.
- Role-based experiences for student, teacher, principal, admin, and additional operational roles.
- Existing areas for dashboard, classrooms, admissions, staff management, courses, assignments, submissions, grades, attendance, messages, settings/profile, school configuration, exam predictor, webhooks, and file uploads.
- Database entities including schools, users, classrooms, courses, enrollments, grades, attendance, assignments, submissions, notifications, messages, remarks, student_details, teacher_details, exam_assets, predicted_topics, predicted_questions, and revision_plans.

The current implementation is more like a broad school-management portal than a focused student operating system. The remake must correct that product direction while preserving the underlying academic and administrative workflows that are real and useful.

NON-NEGOTIABLE ENGINEERING RULES

1. Inspect the complete application before implementation: files, routes, templates, models, SQL, helpers, environment variables, upload behavior, authentication, integrations, and tests.
2. Never fabricate backend functionality, database records, integrations, AI responses, notifications, or deployment success.
3. Never expose secrets, API keys, SMTP credentials, database URLs, webhook credentials, or privileged configuration in client-side code.
4. Use persistent database data. Do not replace real queries with hardcoded dashboard values or fake arrays.
5. Preserve authentication and enforce authorization on the server, not only in templates.
6. Apply school_id and user ownership scoping consistently to every query.
7. Do not silently change the database engine or framework unless a migration plan is explicitly justified and verified.
8. Do not introduce a new frontend stack only for visual reasons. Work with the existing Flask/Jinja architecture unless the repository audit proves a migration is necessary.
9. Repair missing imports, missing templates, broken routes, unsafe query assumptions, and inconsistent forms discovered during the audit.
10. Keep changes small, reviewable, and phase-based. At the end of each phase, list changed files, behavior preserved, behavior changed, tests run, and known risks.
11. Use clear loading, empty, success, validation, permission-denied, failure, and offline/error states. Never leave a blank screen.
12. Treat accessibility and responsive behavior as product requirements, not polish.
13. Never claim that a feature works until the relevant route, persistence path, permission path, and browser flow have been tested.

PRIMARY PRODUCT OUTCOME

When a student signs in, the application should answer these questions immediately:
- What matters most today?
- What is the next action I should take?
- What is at risk if I do nothing?
- Where can I continue the work I started?
- What evidence supports my academic status?

The primary student experience should prioritize:
1. One clear next action.
2. Today’s academic timeline.
3. Upcoming deadlines and overdue work.
4. Course-level context.
5. Progress and risk signals that are explained rather than merely decorated.
6. Fast capture or completion of academic work.
7. A quiet, reliable interface with low cognitive load.

DESIGN WORLD

Define the product as “a quiet study command center built like a high-end research desk”: warm off-white surfaces, ink-black text, restrained indigo or cobalt for action, one controlled signal color for urgency, subtle paper-like texture, precise editorial typography, disciplined grids, and generous whitespace. The interface should feel closer to a premium research notebook, a well-designed field instrument, and a focused operating system than to a school administration portal.

Avoid the following:
- Generic purple gradients.
- Excessive glassmorphism.
- Decorative dashboard charts with no decision value.
- Dense card grids where every item looks equally important.
- Fake system-health language such as “OPTIMAL” when it does not lead to an action.
- Overuse of pills, badges, floating blobs, heavy shadows, or animated particles.
- Unexplained AI sparkle motifs.
- Giant hero sections inside authenticated workflows.
- Inline style sprawl.
- Unusable tables on mobile.
- Placeholder copy presented as finished product copy.

IMPLEMENTATION ORDER

Phase 1: Audit and baseline. Map the repository, route graph, templates, queries, schema, environment variables, integrations, role permissions, uploads, and current test coverage. Run compilation and available tests. Record known failures.

Phase 2: Product foundation. Define the user jobs, navigation hierarchy, design tokens, shared layout, flash-message system, form conventions, responsive shell, and accessible interaction patterns.

Phase 3: Student command center. Remake the student dashboard, today view, task/deadline surfaces, course context, and progress summaries using persistent data.

Phase 4: Academic workflows. Remake courses, assignments, submissions, grades, attendance, and classroom flows while preserving or improving the current data paths.

Phase 5: Communication and intelligence. Clarify messages, notifications, and the exam predictor. Make every AI or heuristic result transparent about its source, state, and limitations.

Phase 6: Staff and operations. Remake teacher, principal, admin, admission, staff, school configuration, export, and classroom management flows with a clear operational information architecture.

Phase 7: QA and release hardening. Verify route access, authorization, persistence, responsive behavior, keyboard navigation, contrast, uploads, error handling, and regression coverage.

REQUIRED DELIVERABLE AT THE END OF EACH PHASE

Return:
- A concise summary of decisions.
- The exact files inspected or changed.
- The data and backend behavior preserved.
- The behavior intentionally redesigned.
- Tests executed and their results.
- Any unresolved risk or missing external dependency.
- The next smallest safe phase.

Begin by auditing the actual repository. Do not write UI code yet.
```

---

# 2. Forensic Audit Prompt

Use this after the master prompt if the coding agent begins implementation too early.

```text
Before changing code, perform a forensic audit of the existing Student OS repository.

Create a written audit with these sections:

1. Runtime and architecture. Identify the application entrypoint, Flask configuration, database connection strategy, schema initialization/migrations, authentication setup, CSRF behavior, mail configuration, file upload paths, and deployment/runtime files.

2. Route inventory. Build a table containing every route, HTTP method, blueprint, template or response, authentication requirement, role restriction, database tables touched, and current user value.

3. User journeys. Trace the complete flows for:
   - Anonymous visitor to login.
   - Student login to dashboard.
   - Student viewing courses and assignments.
   - Student submitting work.
   - Student viewing grades and attendance.
   - Student using the exam predictor.
   - Teacher posting an assignment and grading a submission.
   - Admin or principal managing people, classrooms, courses, admissions, and school settings.
   - User sending and receiving messages.
   - Password reset and email verification.

4. Data model. Map tables, primary keys, foreign keys, uniqueness rules, school scoping, ownership scoping, timestamp behavior, nullable fields, migrations, seed/demo data, and any mismatch between schema.sql and runtime code.

5. Template and asset map. Identify shared templates, layout templates, route-specific templates, missing referenced templates, duplicated markup, inline styles, external CDNs, image assets, upload-serving routes, and JavaScript dependencies.

6. Security and integrity review. Look for missing imports, missing CSRF protection, unsafe role checks, insecure object access, unscoped queries, unvalidated file types, path traversal risks, credential exposure, webhook verification gaps, password-reset risks, and debug/demo behavior that could reach production.

7. Product and UX review. Identify where the current product feels like a generic school portal, where the primary next action is unclear, where content is duplicated, where the hierarchy is weak, where mobile layouts break, and where users may not know what happened after an action.

8. Test baseline. Run the available compile checks and tests. If dependencies are missing, report that fact and do not hide it. Add a list of the minimum tests required before release.

Do not implement fixes in this step. Produce the audit first, then recommend a prioritized remediation plan sorted by user impact, data integrity, security, and implementation risk.
```

---

# 3. Product and UX Direction Prompt

Use this to force a coherent product strategy after the audit.

```text
Using the completed Student OS forensic audit, define the target product experience before writing the new interface.

Reposition Student OS as an academic command center, not a general-purpose school ERP. The product must help a serious student make progress during the next five minutes, while still supporting teacher, principal, and admin operations.

Write the target experience as:

- Product promise: one sentence.
- Primary user: one clearly described serious student.
- Secondary users: teacher, principal, and admin, each with a distinct job.
- Core tension: scattered responsibilities, deadlines, feedback, and performance signals are difficult to hold in working memory.
- Core loop: notice → choose → act → receive confirmation → see progress.
- Primary outcome: the user always knows the next meaningful action.
- Trust promise: the interface never invents academic facts and always distinguishes recorded data, calculated summaries, and generated suggestions.

Define the information hierarchy for the student:

1. Today.
2. Next action.
3. Deadlines and risk.
4. Courses.
5. Progress.
6. Feedback and messages.
7. Planning and prediction.
8. Account and preferences.

Define the information hierarchy for teachers and administrators separately. Do not force student-oriented language onto operational users.

For every major screen, specify:
- User intent.
- Primary task.
- Primary action.
- Secondary actions.
- Required context.
- Data source.
- Success state.
- Empty state.
- Error state.
- Permission-denied state.
- Mobile behavior.
- Keyboard and screen-reader behavior.

Use progressive disclosure. Show the decision-relevant summary first and allow the user to open supporting detail. Avoid showing every metric just because the database contains it.

Do not redesign a screen until its user job and next action are explicit.
```

---

# 4. Visual Design System Prompt

This prompt adapts the video’s mood, typography, whitespace, color, and reference-world technique to Student OS.

```text
Create a visual design system for Student OS using the following product world:

“An exceptionally well-designed research desk for a serious student: quiet morning light, cream paper, graphite ink, a cobalt bookmark, precise annotations, and a small red pencil mark only when something needs attention.”

The interface should communicate composure, intelligence, reliability, and momentum. It should feel premium through restraint and intentionality rather than decoration.

MOOD

Use a calm editorial workbench aesthetic with a light-first theme and a fully considered dark theme. The light theme should use warm neutral backgrounds rather than sterile pure white. The dark theme should use deep charcoal or ink rather than pure black. The product should feel focused and scholarly, not corporate or playful.

TYPOGRAPHY

Choose and document a distinctive, highly legible font system. Use one expressive but restrained display face for major page headings and one exceptionally readable UI/body face for navigation, data, labels, forms, and tables. If a display font harms readability or loading performance, prefer a strong variable sans-serif with deliberate weight and letter-spacing choices.

Specify:
- Display heading sizes and line heights.
- Page title size.
- Section title size.
- Body and helper text sizes.
- Data and numeric styles.
- Label casing and letter spacing.
- Maximum line lengths.
- Font loading and fallback behavior.

Headings should be visibly heavier and more intentional than body text, but the interface must not become shouty. Avoid all-caps for long labels.

WHITESPACE

Treat whitespace as a primary design directive. Use a consistent spacing scale and define both macro and micro rhythm. Give the next action room to breathe. Keep cards from becoming cramped, but do not create large empty areas that hide useful information.

COLOR SYSTEM

Use a 60-30-10 distribution:
- Approximately 60% warm neutral or ink background surfaces.
- Approximately 30% secondary surfaces such as cards, panels, table headers, and muted regions.
- Approximately 10% accent color for primary actions, active navigation, progress, and focus.

Use a separate, restrained signal palette for success, warning, danger, and attention. These colors must be semantically consistent and must never be used as decoration.

Document the exact tokens for:
- Background.
- Surface.
- Surface elevated.
- Border.
- Text primary.
- Text secondary.
- Text muted.
- Primary action.
- Primary action hover.
- Focus ring.
- Success.
- Warning.
- Danger.
- Informational accent.

Verify normal text contrast at least 4.5:1 and large text contrast at least 3:1. Prefer stronger contrast where feasible.

COMPONENT LANGUAGE

Define a restrained component system for:
- App shell.
- Sidebar and mobile navigation.
- Page header.
- Next-action panel.
- Deadline row.
- Course card.
- Progress meter.
- Metric summary.
- Data table.
- Timeline.
- Empty state.
- Loading skeleton.
- Inline validation.
- Flash message.
- Modal or drawer.
- Confirmation state.
- Error boundary.

Use soft borders, low-elevation shadows, small radii, and clear grouping. Avoid every component looking like a floating card. Use dividers, typography, spacing, and alignment to create hierarchy.

MOTION

Use motion only when it helps orientation or confirms an action. Keep transitions short and interruptible. Respect prefers-reduced-motion. Never animate essential information into existence, and never use motion to distract from an overdue task or error.

VISUAL AVOID LIST

Do not use generic purple gradients, decorative blobs, excessive glassmorphism, fake 3D, random illustrations, noisy background textures, excessive pill badges, gratuitous chart animation, or visual styles copied from generic AI dashboards.

Produce design tokens and component rules before styling individual pages.
```

---

# 5. Information Architecture and Navigation Prompt

```text
Remake Student OS navigation around user intent and daily momentum.

For students, use a calm primary navigation with these destinations:

1. Today — the default home and next-action command center.
2. Courses — course context, assignments, resources, and course progress.
3. Tasks — a unified view of assignments, deadlines, submissions, and completion state.
4. Progress — grades, attendance, trends, and explanations.
5. Messages — teacher feedback, conversations, and notifications.
6. Planner or Predictor — revision planning and exam-prediction workflows, clearly marked as calculated or generated guidance.
7. Profile and Settings — account, language, preferences, and verified email.

For teachers, use:
1. Overview.
2. My Courses.
3. Work to Review.
4. Students.
5. Attendance.
6. Messages.
7. Profile and Settings.

For principals and administrators, use:
1. Overview.
2. Classrooms.
3. Courses.
4. Admissions.
5. Staff.
6. Reports.
7. School Settings.
8. Profile and Settings.

Preserve existing route behavior where practical. If a route cannot be renamed safely, create a clear product-facing label while keeping a stable backend route or compatibility redirect.

Every screen must have:
- A visible page title.
- A one-sentence explanation of the job of the page.
- A primary action.
- An obvious route back to the relevant parent context.
- A current-navigation state that does not rely on color alone.
- A mobile navigation path.

Do not expose every administrative feature in the student navigation. Do not make users scan a long ungrouped sidebar. Use section labels only when they improve comprehension.
```

---

# 6. Student Dashboard / Today Prompt

```text
Remake the authenticated student dashboard as “Today,” the emotional and functional center of Student OS.

The page should answer within five seconds:
- What is my next action?
- What is due soon?
- What needs attention?
- How am I progressing?

LAYOUT

Use an asymmetric editorial layout rather than a uniform grid of equal cards.

The top region should contain:
- A concise welcome that uses the student’s real name when available.
- A short contextual sentence based on real data.
- One prominent Next Action panel.
- A small trust/source label indicating whether the content is recorded, calculated, or suggested.

The Next Action panel must be generated from real persisted data where possible. Examples include an upcoming assignment, an unsubmitted task, a teacher feedback item, an attendance concern, or a revision-plan item. If no next action exists, show a truthful empty state that helps the student create or discover one. Never invent a deadline.

The main content should contain:
- Today’s timeline.
- Upcoming work grouped by urgency rather than a flat list.
- A compact course pulse section showing only useful progress context.
- A progress summary with explainable GPA/grade and attendance calculations.
- Recent teacher feedback or notifications.

The page may include charts only when they answer a question. Prefer a compact trend, progress bar, or annotated comparison over a decorative chart. Explain calculated metrics in a tooltip or nearby helper text.

DATA RULES

Use real database queries and correct school/user scoping. Preserve current dashboard functionality where useful, but remove generic claims such as “system status optimal” unless the status is real, defined, and actionable.

STATES

Design loading skeletons, no-data states, overdue states, error states, and permission states. Empty states should describe what is missing and provide the next available action.

MOBILE

On small screens, put Next Action first, then urgent deadlines, then progress. Avoid requiring horizontal scrolling for the primary daily experience.

ACCESSIBILITY

Use semantic landmarks, a single meaningful H1, descriptive button labels, accessible live updates for action confirmation, and visible focus states. Charts must have a text summary or accessible data alternative.
```

---

# 7. Courses, Tasks, Assignments, and Submissions Prompt

```text
Remake the academic work loop without breaking the existing persistence model.

The desired loop is:
1. Student sees an assignment in Today or Tasks.
2. Student opens the assignment and immediately understands what is required, when it is due, and what course it belongs to.
3. Student can start, save, edit, attach, and submit work with clear status.
4. Student receives a truthful confirmation.
5. Teacher sees the submission in work-to-review.
6. Teacher can grade and provide feedback.
7. Student sees the grade and feedback in context.

COURSE LIST

Create a calm, scannable course index. Each course row/card should show course name, teacher, next deadline, progress signal, and an action to continue. Do not show fake enrollment counts or fabricated progress.

COURSE DETAIL

Use a clear hierarchy:
- Course title and teacher.
- Course-level progress or context.
- Next required action.
- Assignment list grouped by status.
- Feedback and grades.
- Enrolled students only for authorized staff.

ASSIGNMENTS

Show title, course, due date, submission status, grade status, attachment presence, and a short description. Use semantic statuses such as Not started, In progress, Submitted, Needs revision, Graded, Overdue, or No due date. Do not use color as the only status signal.

SUBMISSION UX

Provide a real form for content and attachments. Validate file size, file type, required fields, and ownership. Make it clear whether the user is saving a draft or submitting final work. Prevent accidental duplicate submissions or explain replacement behavior. After submission, show the persisted timestamp and submission status.

TEACHER REVIEW

Make review work a queue with clear priority and context. A teacher should see who submitted, for which assignment, when, and what remains to be graded. Grading should validate score ranges against max score and preserve feedback.

REPAIR ANY MISSING OR BROKEN TEMPLATE REFERENCES

If a route references a missing template such as submit_assignment.html, create the template and test the full GET and POST flow. Do not hide the problem with a redirect that loses the user’s intent.
```

---

# 8. Grades, Attendance, and Progress Prompt

```text
Remake academic progress so that it explains status instead of displaying isolated metrics.

The student Progress area must answer:
- How am I doing overall?
- Which courses need attention?
- How reliable is my attendance?
- What changed recently?
- What should I do next?

Use persistent grades and attendance data. Preserve the existing GPA calculation behavior unless the audit proves it is mathematically incorrect; if you change it, document the formula and add tests.

Show:
- Overall progress summary.
- Course-by-course performance.
- Attendance rate with present, absent, and late counts.
- Trend or recent-change context where data volume supports it.
- Plain-language explanations for calculated metrics.
- Links from a metric to the underlying records.

Do not label a student “Academic Honor,” “On Track,” “Stable,” or “At Risk” without a documented rule and sufficient data. When there is insufficient data, say so explicitly.

For teachers and principals, preserve aggregate views but separate them from the student experience. Use filters that are scoped to the current school and authorized courses/classrooms.

Use accessible tables for exact values and visual summaries only as secondary representations. On mobile, stack summaries and make tables horizontally scrollable with a visible cue or transform simple records into rows/cards.
```

---

# 9. Messages, Notifications, and Feedback Prompt

```text
Remake communication around actionable academic context.

Separate:
- Direct messages.
- System notifications.
- Teacher feedback on submitted work.
- Deadline or attendance alerts.

A notification should tell the user what happened, why it matters, when it happened, and where to act. Each actionable notification should link to the relevant object rather than dropping the user at a generic page.

Preserve unread counts and read state using persistent data. Avoid a notification list that is only a decorative feed. Provide thoughtful empty states, clear timestamps, and accessible status changes.

Messages must:
- Enforce sender/recipient and school scoping.
- Escape or safely render user-generated content.
- Have clear send confirmation and failure handling.
- Support keyboard navigation and mobile composition.
- Never claim that an email, notification, or external delivery succeeded unless the backend confirms it.
```

---

# 10. Exam Predictor and AI Integrity Prompt

```text
Remake the exam predictor as a transparent academic planning tool, not a magical AI feature.

Inspect the existing implementation before changing it. The current predictor uses uploaded assets, local text extraction, a deterministic heuristic engine, stored predicted topics/questions, and a generated revision plan. Do not describe these outputs as human-validated or guaranteed predictions.

The interface must clearly distinguish:
- Uploaded source material.
- Extracted text status.
- Deterministic or heuristic analysis.
- Generated topic suggestions.
- Generated question examples.
- Revision-plan recommendations.
- User-confirmed actions.

Show processing states:
- File selected.
- Uploading.
- Uploaded.
- Extracting.
- Analyzing.
- Results ready.
- Partial result.
- Failed with a retry path.

If analysis is synchronous and may take time, do not freeze the entire interface without feedback. If a background job is introduced, implement real persistence and status tracking rather than faking progress.

Every output should include a short explanation of its basis and limitations. Let the student edit, dismiss, reschedule, or mark revision-plan items complete. Never fabricate source coverage or confidence. Use confidence/probability only when the calculation is defined and explained.

Keep uploaded files private to the authorized student/school scope. Validate file types and sizes, store file metadata safely, and avoid exposing filesystem paths.
```

---

# 11. Staff, Principal, Admin, and Operations Prompt

```text
Remake operational workflows without allowing them to overwhelm the student command center.

Preserve the existing real functionality for:
- Classrooms and roster views.
- Attendance capture, QR flows, and exports.
- Course and enrollment management.
- Admissions.
- Staff management and CSV import.
- School settings and feature configuration.
- Reports and administrative views.

Use a separate operations-oriented information architecture with clear role boundaries. Staff should see the work that needs their attention: submissions to review, attendance to record, admissions to process, students needing follow-up, and courses to manage.

For every operational workflow:
- Verify the current user’s role on the server.
- Verify school ownership on every read and write.
- Verify object ownership for teachers where relevant.
- Validate input and uploads.
- Confirm the action using persisted data.
- Show errors without losing the form context when possible.
- Provide a clear back path.
- Add confirmation for destructive actions.
- Preserve export formats and test the generated output.

Do not give students access to staff/admin navigation merely because a template condition is present. Do not rely on hidden links for security.

If the current product has multiple terms for the same concept, choose one consistent UI term while retaining compatibility with backend field names.
```

---

# 12. Responsive and Accessibility Prompt

```text
Make accessibility and responsive behavior first-class requirements for the Student OS remake.

Responsive requirements:
- Design mobile-first, then expand for tablet and desktop.
- Keep the primary action visible without excessive scrolling.
- Replace the fixed desktop sidebar with an accessible mobile navigation drawer.
- Ensure tables have an intentional mobile representation.
- Prevent clipped headings, overflowing forms, and unusable modals.
- Keep tap targets at least approximately 44px where practical.
- Support landscape mobile layouts for dense academic tables.
- Test at 320px, 375px, 768px, 1024px, and wide desktop widths.

Accessibility requirements:
- Use semantic HTML landmarks and heading hierarchy.
- Add a skip link to the main content.
- Use labels associated with every form field.
- Provide visible :focus-visible states.
- Do not use color alone to indicate status.
- Provide accessible names for icon-only buttons.
- Make dialogs keyboard reachable, closable, and focus-managed.
- Announce important asynchronous updates through an appropriate live region.
- Respect prefers-reduced-motion.
- Ensure normal text contrast is at least 4.5:1 and large text at least 3:1.
- Provide text alternatives for charts, QR images, and decorative imagery.
- Make error messages specific and associated with the relevant field.

Before declaring completion, run a keyboard-only pass and a screen-reader-oriented semantic review.
```

---

# 13. Engineering Integrity and Data Truthfulness Prompt

```text
Apply this integrity review to every Student OS change.

For each new or changed feature, explicitly identify:
- The source table or trusted backend source.
- The authorized user scope.
- The school scope.
- The calculation or transformation applied.
- The persistence path.
- The confirmation returned to the user.
- The failure behavior.
- The test that proves it.

Reject any implementation that:
- Hardcodes records, counts, names, grades, attendance, deadlines, or notifications in production UI.
- Creates fake API responses to make a screen appear complete.
- Claims that an email, webhook, AI analysis, file upload, or deployment succeeded without backend confirmation.
- Puts credentials or secrets in templates, JavaScript, static files, logs, or client-visible HTML.
- Uses a client-side role check as the only authorization barrier.
- Loads an object by ID without checking school or ownership.
- Trusts an uploaded filename as a safe filesystem path.
- Renders user-generated HTML without an explicit safe policy.
- Deletes or replaces data without confirmation and an auditable path.
- Introduces a new integration without documenting required environment variables and a verified failure state.

If a feature cannot be completed truthfully because an external dependency is unavailable, build the honest unavailable state and explain the dependency. Do not simulate success.
```

---

# 14. Route-by-Route Remake Execution Prompt

Use this prompt to make the coding agent work incrementally rather than rewriting the whole repository in one opaque pass.

```text
Work in one route family at a time. Do not modify unrelated feature areas in this pass.

ROUTE FAMILY: [INSERT ROUTE FAMILY]

Examples:
- dashboard and Today
- courses and assignments
- grades and attendance
- classrooms
- messages and notifications
- exam predictor
- admissions and staff
- school settings
- authentication and account settings

Before editing:
1. List every route in this family.
2. List every template, helper, query, table, upload path, and integration it uses.
3. List existing behavior that must remain compatible.
4. List known bugs or missing pieces.
5. Define the target user jobs and next actions.
6. Define desktop, tablet, and mobile behavior.

Implement:
- Shared shell and page hierarchy first.
- Data-backed states second.
- Forms and mutations third.
- Error, empty, permission, and loading states fourth.
- Visual refinement last.

Do not introduce placeholder data. If the existing backend cannot support a requested visual or workflow, state the limitation and either add a real backend change or design an honest degraded state.

At the end:
- Show changed files.
- Run route-level tests.
- Test at least one allowed role and one denied role.
- Test empty data.
- Test a failure path.
- Test persistence after refresh.
- Test mobile layout.
- Report any unresolved issue.
```

---

# 15. QA and Release Verification Prompt

```text
Act as the release QA engineer for Student OS. Do not accept visual polish as evidence of correctness.

Build and execute a verification matrix for the implemented phase.

AUTHENTICATION

Verify anonymous access, valid login, invalid password, wrong selected role, logout, remember-me behavior, password reset, expired reset token, email verification state, and session behavior.

AUTHORIZATION

For every protected route, test:
- Anonymous user redirected appropriately.
- Student access.
- Teacher access.
- Principal access.
- Admin access.
- Cross-school object access denied.
- Cross-user object access denied.
- Teacher access limited to owned courses/classes where required.

PERSISTENCE

Create or mutate a real record, refresh the page, navigate away and back, and verify that the state persists in the database. Test duplicate submissions, duplicate enrollments, missing related records, and invalid IDs.

ACADEMIC FLOWS

Verify the complete paths for course viewing, assignment creation, student submission, teacher grading, grade display, attendance viewing/capture, classroom roster, notification creation/read state, message send/read state, and predictor upload/analysis/result display.

FILE AND INTEGRATION FLOWS

Verify allowed and disallowed file types, size limits, private access, missing files, unavailable mail configuration, failed webhook payload, unavailable predictor dependencies, and safe error messages.

UI AND ACCESSIBILITY

Test keyboard-only navigation, focus visibility, form labels, dialogs, status text, contrast, reduced-motion behavior, 320px mobile width, tablet width, desktop width, long names, long course titles, empty lists, large tables, and error banners.

VISUAL QUALITY

Check that:
- The product world is consistent.
- Typography has a clear hierarchy.
- Whitespace creates focus.
- The color system is restrained and semantic.
- The primary action is obvious.
- Cards are not overused.
- Charts are decision-relevant.
- No screen looks like a generic AI dashboard.
- No inline style or duplicated CSS undermines the design system without justification.

Report each check as PASS, FAIL, BLOCKED, or NOT APPLICABLE. Include reproduction steps and exact files for every failure. Never claim release readiness when a critical path is blocked.
```

---

# 16. Visual Refinement Prompts

Use one of these when the first remake is technically correct but visually weak.

## 16.1 If the UI feels generic

```text
The current Student OS build is functional but visually generic. Do not add more decoration. Refine the product world.

Make the interface feel like a premium research desk: warm paper surfaces, ink typography, restrained cobalt action color, deliberate alignment, editorial hierarchy, and quiet confidence. Replace generic gradients, excessive pills, and repeated equal-weight cards with typography, whitespace, dividers, and progressive disclosure.

For each major screen, identify the single most important decision the user must make and give that action the strongest visual hierarchy. Remove or demote every element that does not support the decision.

Do not change backend behavior in this pass. Change tokens, spacing, type hierarchy, component proportions, and surface treatment. Preserve all real data and interactions.
```

## 16.2 If the UI feels crowded

```text
The current Student OS interface is crowded and difficult to scan. Perform a hierarchy and whitespace pass.

Reduce simultaneous visual competition. Group related content, increase section rhythm, shorten supporting copy, remove redundant labels, and move secondary details into expandable or contextual views. Keep the Next Action, urgent deadline, and current status visible.

Do not solve crowding by hiding important information or shrinking text. Use progressive disclosure and stronger grouping. On mobile, prioritize the next action and urgent work before historical analytics.
```

## 16.3 If the UI feels flat or lifeless

```text
The current Student OS interface feels flat. Add depth through intentional hierarchy rather than gradients or decoration.

Use a stronger relationship between background, elevated surface, border, typography, and action color. Introduce one distinctive editorial detail per page, such as a timeline rule, annotated progress marker, chapter label, or course accent—not a collection of random ornaments.

Keep motion subtle, fast, interruptible, and disabled or minimized under prefers-reduced-motion. Do not add animated particles, floating blobs, or gratuitous chart animation.
```

## 16.4 If the dashboard feels like an admin portal

```text
The student dashboard still feels like a school administration portal. Recenter it on personal momentum.

Replace generic system-status language and organization-wide metrics with the student’s next action, upcoming work, feedback, progress, and risk. Use the student’s real context and provide a direct route to continue work. Keep administrative features out of the student’s primary navigation.

Do not remove real academic records. Reframe them around decisions the student can make today.
```

## 16.5 If the UI is beautiful but untrustworthy

```text
The current Student OS build looks polished but may imply data or capability that is not real. Perform a truthfulness pass.

Label recorded data, calculated summaries, heuristic predictions, generated suggestions, and unavailable integrations distinctly. Remove fake success states, fabricated counts, unexplained confidence values, and generic claims such as “optimal” or “AI-powered” when they are not supported by the backend.

For every important result, make its source and limitation understandable without overwhelming the user.
```

---

# 17. Final Acceptance Prompt

```text
Evaluate the remade Student OS as a product, not merely as code.

The remake is acceptable only if:

1. The application still uses real persistent data and existing valuable functionality has not been silently removed.
2. Authentication, authorization, school scoping, ownership checks, uploads, messages, and academic records are secure and tested.
3. A student can immediately identify the next meaningful action after login.
4. The main flow from deadline to work to submission to feedback is coherent.
5. Teachers and administrators can complete their real operational tasks without inheriting student-facing clutter.
6. The interface has a distinctive, consistent product world rather than generic AI-dashboard styling.
7. Typography, whitespace, color, spacing, component states, and motion follow a documented design system.
8. Empty, loading, error, denied, overdue, and partial-data states are designed and truthful.
9. The product works at mobile, tablet, and desktop widths.
10. Keyboard navigation, focus states, labels, semantic structure, contrast, reduced motion, and alternative text are verified.
11. No secrets are exposed client-side.
12. No fake backend responses, demo-only records, or unverified deployment claims remain in production paths.
13. Tests cover the critical user journeys and permission boundaries.
14. The agent can explain important architectural decisions and list every changed file.

Return a release report with:
- What was rebuilt.
- What was preserved.
- What changed in the user experience.
- What changed in the visual system.
- What changed in the data or backend layer.
- Tests and results.
- Known limitations.
- Recommended next improvements.
```

---

# 18. Optional Context Block to Append to Any Prompt

Use this compact block whenever a separate design or coding agent needs repository context.

```text
PROJECT CONTEXT: Student OS

Student OS is an existing Flask/Jinja academic application. The repository is the source of truth. It has Flask-Login authentication, SQLite locally with optional PostgreSQL support, hand-written SQL, Jinja templates, CSS under static/css, and blueprints under routes/.

Current feature families include dashboard, classrooms, admissions, staff, courses, assignments, submissions, grades, attendance, messages, settings/profile, school configuration, exam predictor, file uploads, exports, and webhooks.

The target product is not a generic school ERP. It is a calm academic command center for serious students that turns scattered responsibilities into one clear next action while preserving teacher, principal, and admin workflows.

Never fabricate data or integrations. Never expose secrets. Use persistent database data. Preserve valuable behavior. Verify role, school, and ownership scope server-side. Design loading, empty, success, error, denied, and partial states. Make the experience responsive, keyboard accessible, semantically structured, high-contrast, and visually distinctive.
```

---

# References

[1]: https://www.youtube.com/watch?v=83geKREHQY0 "Referenced prompt-making video"

[2]: https://github.com/mohit-maybe/Student-OS "Student OS repository"
