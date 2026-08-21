import app


def main():
    app.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False, SECRET_KEY='smoke-test')
    client = app.app.test_client()
    for path in ('/', '/login', '/privacy', '/forgot-password'):
        response = client.get(path)
        print(path, response.status_code, response.content_type)
        if response.status_code >= 500:
            raise SystemExit(f'{path} returned {response.status_code}')


if __name__ == '__main__':
    main()
