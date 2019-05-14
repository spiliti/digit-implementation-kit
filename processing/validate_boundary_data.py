import json
import os
from pathlib import Path

from common import superuser_login, validate_boundary_data
from config import config
from processing.revenueBoundaryDownload import download_boundary

boundary_path = config.MDMS_LOCATION / config.CITY_NAME.lower() / "egov-location" / "boundary-data.json"

auth_token = superuser_login()["access_token"]


def process_boundary_of_all_ulb(auth_token):
    print("MDMS LOCATION : {}".format(config.MDMS_LOCATION))
    print("ENV : {}\n".format(config.CONFIG_ENV))

    tenat_with_error_count = 0
    error_details = {}
    for folder in os.scandir(config.MDMS_LOCATION):
        boundary_path = Path(folder.path) / "egov-location" / "boundary-data.json"

        if os.path.isfile(boundary_path):

            with open(boundary_path) as f:
                boundary_data = json.load(f)

            tenantid = boundary_data["tenantId"]
            boundary_type = "REVENUE"

            errors = validate_boundary_data(auth_token, boundary_data, boundary_type)

            if len(errors) > 0:
                print("\n")
                print("========================" * 3)
                print("\t" * 8, folder.path.split("/")[-1].upper())
                print("========================" * 3)

                for error in errors:
                    print(error)

                download_boundary(tenantid, boundary_type)
                tenat_with_error_count += 1
                error_details[tenat_with_error_count] = tenantid

    print("\n" * 2, "::Tenant with Error::")
    for count, tenant in error_details.items():
        print(count, " : ", tenant)


def process_boundary_of_env_ulb(auth_token):
    print("MDMS LOCATION : {}".format(config.MDMS_LOCATION))
    print("ENV : {}\n".format(config.CONFIG_ENV))


    if os.path.isfile(boundary_path):

        with open(boundary_path) as f:
            boundary_data = json.load(f)

        tenantid = boundary_data["tenantId"]
        boundary_type = "REVENUE"

        errors = validate_boundary_data(auth_token, boundary_data, boundary_type)

        if len(errors) > 0:
            print("\n")
            print("========================" * 3)
            print("\t" * 8, config.CITY_NAME.upper())
            print("========================" * 3)

            for error in errors:
                print(error)

            download_boundary(tenantid, boundary_type)
        else:
            print("Processing of ulb \"{}\" Sucessfull with No Error".format(config.CITY_NAME))




process_boundary_of_env_ulb(auth_token)
