# Video prompt framework notes

Source: https://www.youtube.com/watch?v=83geKREHQY0

## Observed framework

The video addresses the problem of generic, repetitive, lifeless AI-generated websites. It recommends progressively specifying the product world instead of asking for a vague modern design.

1. Select a capable design-oriented model.
2. Control the mood with a specific aesthetic world rather than the word modern.
3. Define typography and pairings explicitly.
4. Treat whitespace as a primary design directive, including micro and macro spacing.
5. Specify the hero or primary task surface with clear elements: focused headline, supporting copy, primary action, product visual, and trust signal.
6. Establish a color system using dominant, secondary, and accent proportions such as 60-30-10.
7. Use a Context-Directive-Constraint prompt structure.
8. Iterate by adding concrete real-world references when the result feels muddy or flat, then make focused post-generation adjustments.
9. Use visual references or screenshots when available.
10. Judge quality by perceived value, intentionality, readability, clarity, consistency, and contrast.

## Example motifs described in the analysis

Examples include Dark Academia with scrollytelling, typography-focused project management dashboards, whitespace-focused editorial layouts, outcome-driven hero sections, and B2B analytics interfaces with explicit color systems.

## Adaptation notes for Student OS

For a full-stack remake, use the framework at multiple levels: product world, global shell, dashboard, task surfaces, tables, forms, mobile navigation, and state-specific components. Keep the prompt explicit about preserving backend behavior and data integrity, and separate visual changes from backend changes. Require WCAG contrast, keyboard navigation, responsive behavior, loading/empty/error states, and truthful data handling as non-negotiable constraints.

# Audited Student OS baseline

The checked-out repository is a Flask/Jinja application, not a React/tRPC application. It uses Flask-Login authentication, SQLite locally with optional PostgreSQL support, hand-written SQL through db.py, Jinja templates, CSS in static/css/style.css, and blueprints under routes/.

Existing functional areas include dashboard, role-based login, classrooms, admissions, staff management, courses, assignments, submissions, grades, attendance, messages, settings/profile, school configuration, exam predictor, and webhooks. The schema includes schools, users, classrooms, courses, enrollments, grades, attendance, assignments, submissions, notifications, messages, remarks, student_details, teacher_details, exam_assets, predicted_topics, predicted_questions, and revision_plans.

The current dashboard is role-specific but analytics-oriented: students see GPA, courses, attendance, status, charts, recent activity, notifications, and an attendance QR modal; teachers and principals see aggregate metrics. The sidebar exposes many modules and management features.

Important audit findings for the remake prompt: the product currently feels more like a broad school-management portal than a focused student command center; the primary next action is not consistently surfaced; dashboard language contains generic system-status phrasing such as OPTIMAL; the visual system is heavily customized but has duplicated/overridden CSS and substantial inline styles; several role-specific flows and routes must be preserved; the app includes seeded demo-data logic controlled by SEED_DEMO; upload and AI-predictor behavior need truthfulness and explicit processing states; and the audit surfaced likely runtime fragility including missing imports in some module headers and a referenced submit_assignment.html template absent from the top-level template inventory. Existing tests could not run because pytest is not installed in the sandbox, although Python bytecode compilation completed successfully.
