from common import superuser_login, update_property_status

properties = (
    ('PT-806-1002672', 'pb.gurdaspur'),
)

if __name__ == "__main__":
    login = superuser_login()
    auth_token = login["access_token"]

    update_property_status(auth_token, properties, "INACTIVE")