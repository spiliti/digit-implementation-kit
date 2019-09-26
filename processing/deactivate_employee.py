from config import config
from common import update_user_activation, superuser_login


def main():
    auth_token = superuser_login()["access_token"]
    update_user_activation(auth_token, "pb", "9417630724", activate=True)


if __name__ == "__main__":
    main()
