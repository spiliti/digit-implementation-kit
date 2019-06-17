from common import superuser_login
from processing.generate_localization_data import process_boundary_file
from config import config

boundary_path = config.MDMS_LOCATION / config.CITY_NAME.lower() / "egov-location" / "boundary-data.json"

auth_token = superuser_login()["access_token"]

process_boundary_file(auth_token, boundary_path, write_localization=True, generate_file=False)
