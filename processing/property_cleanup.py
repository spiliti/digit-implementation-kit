from common import superuser_login, cleanup_property

properties = (
    ('PT-1012-622468', 'pb.testing'),
)

if __name__ == "__main__":
    login = superuser_login()
    auth_token = login["access_token"]

    cleanup_property(auth_token, properties)