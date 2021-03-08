from config import config
from common import update_user_activation, superuser_login,remove_user_photo



def main():
    auth_token = superuser_login()["access_token"]
    #update_user_activation(auth_token, "pb.baghapurana", "EMP1", activate=True)
    remove_user_photo(auth_token, 'pb.jalandhar', 'PTEMPJALCFC05')


if __name__ == "__main__":
    main()
