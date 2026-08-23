# Student OS v2 Database Foundation

The schema is intentionally small for the first vertical slice.

## Core tables

### schools
- id
- name
- slug
- created_at

### users
- id (auth provider user ID)
- full_name
- email
- created_at

### memberships
- id
- school_id → schools.id
- user_id → users.id
- role (`admin`, `teacher`, `student`)
- created_at

Unique constraint: `(school_id, user_id)`.

### classes
- id
- school_id → schools.id
- name
- section
- academic_year
- created_at

### teacher_assignments
- id
- school_id → schools.id
- teacher_user_id → users.id
- class_id → classes.id
- created_at

### student_profiles
- id
- school_id → schools.id
- user_id → users.id
- admission_number
- class_id → classes.id
- created_at

Unique constraints: `(school_id, user_id)` and `(school_id, admission_number)`.

### attendance_records
- id
- school_id → schools.id
- class_id → classes.id
- student_user_id → users.id
- attendance_date
- status (`present`, `absent`, `late`, `excused`)
- marked_by → users.id
- created_at

Unique constraint: `(school_id, student_user_id, attendance_date)`.

## Security

Supabase Row Level Security should be enabled on every tenant table before production data is used. Policies must resolve school membership from the authenticated user rather than accepting an arbitrary `school_id` from the client.
