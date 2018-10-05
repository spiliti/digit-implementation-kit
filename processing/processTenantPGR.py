from inspect import getsourcefile
import os.path as path, sys
current_dir = path.dirname(path.dirname(path.abspath(getsourcefile(lambda:0))))
sys.path.insert(0, current_dir[:current_dir.rfind(path.sep)])

import traceback
from os.path import dirname

try:
    import create_employee_script
except ImportError as ex:
     dirname(dirname(__file__))


from config import config, load_config

import boundaryGen
import departmentGen
import designationGen
import tenantGen
import employeeGen

cities = ["Alawalpur"]
cities = ["Dasuya", "Handiaya", "Lalru", "Shahkot", "SultanpurLodhi", "Adampur", "Alawalpur", "Arniwala", "BassiPathana", "Bhogpur", "Dasuya", "Dharamkot", "Garhshankar", "Hariana", "Khanauri", "LohianKhas", "Mahilpur", "Makhu", "Mallanwala", "Mudki", "ShamChurasi", "Sunam", "Talwara", "Tapa", "UrmarTanda", "Zirakpur"]

cities = ["Shahkot", "Handiaya", "Lalru", "Dasuya", "Sultanpur Lodhi", "Zirakpur"]

# cities = ["Testing"]

cities = ["Adampur", "Alawalpur", "Bassi Pathana", "Bhogpur", "Dharamkot", "Garhshankar", "Hariana", "Sham Churasi", "Sunam", "Tapa", "Urmar Tanda"]

cities = ["Adampur", "Bassi Pathana", "Bhogpur", "Dharamkot", "Garhshankar", "Hariana", "Sham Churasi", "Sunam", "Tapa", "Urmar Tanda"]

for city in cities[2:]:
    try:
        config.CITY_NAME = city.replace(" ", "")
        load_config()

        # step = "Creating employees"
        # create_employee_script.main()
        step = "Generating tenant data"
        print(step)
        tenantGen.main()

        step = "Generating department data"
        print(step)
        departmentGen.main()

        step = "Generating designation data"
        print(step)
        designationGen.main()

        step = "Generating Boundary data"
        print(step)
        boundaryGen.main()

        step = "Generating Employee data"
        print(step)
        employeeGen.main()

    except Exception as ex:
        print("City", city, "failed", step, str(ex))
        traceback.print_exc()