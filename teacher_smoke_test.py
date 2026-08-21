import app


def main():
    app.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, SECRET_KEY='teacher-smoke-test')
    client = app.app.test_client()
    response = client.post('/login', data={'username': 'mr_smith', 'password': 'password', 'role': 'teacher'}, follow_redirects=True)
    print('/login teacher', response.status_code, response.request.path)
    if response.status_code >= 500:
        raise SystemExit('teacher login failed')
    for path in ('/dashboard', '/courses', '/grades', '/attendance', '/messages', '/settings', '/profile', '/admin/staff', '/admissions/enroll'):
        response = client.get(path)
        print(path, response.status_code, response.content_type)
        if response.status_code >= 500:
            raise SystemExit(f'{path} returned {response.status_code}')
    denied = client.get('/superadmin/schools')
    print('/superadmin/schools for teacher', denied.status_code, denied.request.path)
    if denied.status_code >= 500:
        raise SystemExit('teacher authorization flow failed')


if __name__ == '__main__':
    main()
