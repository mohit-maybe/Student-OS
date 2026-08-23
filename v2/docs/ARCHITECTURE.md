# Student OS v2 Architecture

## Core domains

- Identity: users, sessions, roles
- School: schools, memberships, settings
- Academic structure: classes, sections, subjects, teacher assignments
- Students: profiles and enrollment
- Attendance: daily attendance records
- Academics: assessments, marks, report cards
- Communication: announcements and messages

## Tenancy model

Every school is a tenant. A user belongs to one or more schools through a membership record. Domain tables carry `school_id` so tenant boundaries are explicit.

The application must never trust a school ID supplied by the browser. The server derives the active school from the authenticated membership/session and verifies access before every mutation.

## Roles

### Admin

Manage school settings, staff, students, classes, subjects and reports.

### Teacher

Access only assigned classes/subjects, manage attendance and academic records, and communicate with their school.

### Student

Read their own profile, attendance, academic results and school announcements.

## First vertical slice

1. Authentication
2. School membership
3. Admin creates class/section
4. Admin creates teacher membership
5. Admin enrolls student
6. Teacher records attendance
7. Student reads attendance

## Engineering rules

- TypeScript strict mode.
- Server-side authorization for every protected operation.
- Database constraints for tenant and relationship integrity.
- Validation at API boundaries.
- No business logic duplicated between three role dashboards.
- Prefer small domain functions over giant route handlers.
- Add tests before calling a vertical slice complete.
