from common import create_boundary
from config import load_admin_boundary_config


def main():
    create_boundary(load_admin_boundary_config, "ADMIN")


if __name__ == "__main__":
    main()
