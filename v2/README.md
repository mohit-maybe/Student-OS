# Student OS v2

A clean rebuild of Student OS for real school operations.

## Product principle

Build the smallest complete school workflow first, then expand. No feature is considered done until the full user journey works end-to-end.

## First vertical slice

Admin signs in → creates a class → adds a teacher → adds students → teacher records attendance → student sees attendance.

## Planned stack

- Next.js + TypeScript
- Tailwind CSS
- PostgreSQL via Supabase
- Supabase Auth
- Supabase Storage
- Vercel deployment

## Rules

1. Multi-school isolation is a foundation requirement, not a later feature.
2. Every database record that belongs to a school must be scoped to a school.
3. Permissions are enforced server-side; UI hiding is not security.
4. No demo credentials or secrets in source code.
5. Every completed feature gets tested against all relevant roles.
