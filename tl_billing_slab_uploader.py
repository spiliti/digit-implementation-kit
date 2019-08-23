from common import superuser_login
from uploader_tl_billing_slab import create_and_update_billing_slab

tenants = [
    "pb.testing"
]


def main():
    auth_token = superuser_login()["access_token"]
    for tenant in tenants:
        create_and_update_billing_slab(auth_token, tenant)


if __name__ == "__main__":
    main()
