from config import config
from common import update_user_password, superuser_login


def main():
    auth_token = superuser_login()["access_token"]
    update_user_password(auth_token, "pb.tenantd", "username", "password")


if __name__ == "__main__":
    main()
