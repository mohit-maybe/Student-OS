import app


def main():
    app.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, SECRET_KEY='role-smoke-test')
    client = app.app.test_client()
    response = client.post('/login', data={'username': 'alice', 'password': 'password', 'role': 'student'}, follow_redirects=True)
    print('/login student', response.status_code, response.request.path)
    if response.status_code >= 500:
        raise SystemExit('student login failed')
    for path in ('/dashboard', '/courses', '/course/1', '/course/1/assignment/1/submit', '/grades', '/attendance', '/classrooms', '/messages', '/exam-predictor', '/settings', '/profile'):
        response = client.get(path)
        print(path, response.status_code, response.content_type)
        if response.status_code >= 500:
            raise SystemExit(f'{path} returned {response.status_code}')


if __name__ == '__main__':
    main()
