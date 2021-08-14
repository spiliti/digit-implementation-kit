import datetime as dt
import psycopg2
import json
import os
from common import superuser_login

from urllib.parse import urljoin
import requests
from config import config
#from uploader.parsers.ikon import IkonProperty
from uploader.parsers.ikonV2 import IkonPropertyV2


dbname = os.getenv("DB_NAME", "mohali_legacy_data")
dbuser = os.getenv("DB_USER", "postgres")
dbpassword = os.getenv("DB_PASSWORD", "postgres")
tenant = os.getenv("TENANT", "pb.mohali")
city = os.getenv("CITY", "MOHALI")
host = os.getenv("DB_HOST", "localhost")
batch = os.getenv("BATCH_NAME", "1")
table_name = os.getenv("TABLE_NAME", "mohali_assessments_to_cancel")
default_phone = os.getenv("DEFAULT_PHONE", "9999999999")
default_locality = os.getenv("DEFAULT_LOCALITY", "UNKNOWN")
batch_size = os.getenv("BATCH_SIZE", "100")

#dry_run = (False, True)[os.getenv("DRY_RUN", "True").lower() == "true"]
dry_run = False

connection = psycopg2.connect("dbname={} user={} password={} host={}".format(dbname, dbuser, dbpassword, host))
cursor = connection.cursor()
postgresql_select_Query = """
select row_to_json(pd) from {} as pd 
where financialyear='2020-21'
and propertyid='PT-1508-1126580'
and script_status is null
""".format(table_name)


def update_db_record(uuid, **kwargs):
    columns = []
    for key in kwargs.keys():
        columns.append(key + "=%s")

    query = """UPDATE {} SET {} where id = %s""".format(table_name, ",".join(columns))
    cursor.execute(query, list(kwargs.values()) + [uuid])
    connection.commit()
    pass


def main():
    continue_processing = True
    access_token = superuser_login()["access_token"]
    import time

    while continue_processing:
        cursor.execute(postgresql_select_Query)
        data = cursor.fetchmany(int(batch_size))

        # continue_processing = False
        if not data:
            print("No more data to process. Script exiting")
            continue_processing = False
            cursor.close()
            connection.close()

        for row in data:
            json_data = row[0]
            id = json_data["id"]
            print('Processing {}'.format(id))
            try:


                    assessment = {"id": id, "tenantId": "pb.mohali", "assessmentNumber": json_data["assessmentnumber"],"financialYear": json_data["financialyear"],"propertyId" : json_data["propertyid"] ,"assessmentDate" : json_data["assessmentdate"],"status" : json_data["status"] ,"source" : json_data["source"],"channel": json_data["channel"], "unitUsageList" : None  , "documents": None,"additionalDetails": {}}
                    assessment["auditDetails"]= {"createdBy": json_data["createdby"], "lastModifiedBy": json_data["lastmodifiedby"], "createdTime": json_data["createdtime"],"lastModifiedTime": json_data["lastmodifiedtime"]}
                    assessment["workflow"] = None


                    request_data = {
                        "RequestInfo": {
                            "authToken": access_token
                        },

                        "Assessment": assessment

                    }
                    # print(json.dumps(request_data, indent=2))
                    response = requests.post(
                        urljoin(config.HOST, "/property-services/assessment/_cancel?tenantId=pb.mohali"),
                        json=request_data)

                    res = response.json()

                    update_db_record(id,req_payload=json.dumps(request_data), res_payload=json.dumps(res),script_status="ok")  #storing response updating property status as ACTIVATE to approve property
                    print("Assesment cancelation for id ",id )

            except Exception as ex:
                import traceback
                traceback.print_exc()
                update_db_record(id, req_payload=json.dumps(request_data), res_payload=json.dumps(res), script_status=str(ex))

            if dry_run:
                print("Dry run only, exiting now")
                exit(0)


if __name__ == "__main__":
    main()
