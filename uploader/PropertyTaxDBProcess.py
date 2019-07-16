import psycopg2
import json
import os
from common import superuser_login
from uploader.PropertyTaxParser import IkonProperty

dbname = os.getenv("DB_NAME", "postgres")
dbuser = os.getenv("DB_USER", "postgres")
dbpassword = os.getenv("DB_PASSWORD", "postgres")
tenant = os.getenv("TENANT", "pb.jalandhar")
host = os.getenv("DB_HOST", "localhost")
batch = os.getenv("BATCH_NAME", "")
table_name = os.getenv("TABLE_NAME", "pt_legacy_data")
default_phone = os.getenv("DEFAULT_PHONE", "9999999999")
default_locality = os.getenv("DEFAULT_LOCALITY", "SUN62")
batch_size = os.getenv("BATCH_SIZE", "100")
dry_run = (False, True)[os.getenv("DRY_RUN", "True").lower() == "true"]

connection = psycopg2.connect("dbname={} user={} password={} host={}".format(dbname, dbuser, dbpassword, host))
cursor = connection.cursor()
postgresql_select_Query = """
select row_to_json(pd) from {} as pd 
where 
pd.upload_status is NULL and 
pd.new_locality_code is not null 
and session = '2019-2020'
and batchname = '{}' 
limit {} 
""".format(table_name, batch, batch_size)


def update_db_record(uuid, **kwargs):
    columns = []
    for key in kwargs.keys():
        columns.append(key + "=%s")

    query = """UPDATE {} SET {} where uuid = %s""".format(table_name, ",".join(columns))
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
            uuid = json_data["uuid"]
            print('Processing {}'.format(uuid))
            try:
                p = IkonProperty()
                p.process_record(json_data, tenant)
                pd = p.property_details[0]
                # pd.financial_year = "2018-19"
                # p.tenant_id = tenant
                # for o in pd.owners:
                #     o.mobile_number = default_phone
                # pd.citizen_info.mobile_number = default_phone
                pd.source = "LEGACY_RECORD"
                # p.address.locality = {
                #     "code": default_locality,
                #     "area": "AREA1"
                # }
                p.additional_details = {}

                start = time.time()
                req, res = p.upload_property(access_token)
                time_taken = time.time() - start

                if "Properties" in res:
                    pt_id = res["Properties"][0]["propertyId"]
                    ack_no = res["Properties"][0]["acknowldgementNumber"]
                    calc = res["Properties"][0]["propertyDetails"][0]["calculation"]
                    total_amount = calc["totalAmount"]
                    tax_amount = calc["taxAmount"]
                    # upload_status = "COMPLETED"
                    print("Record updloaded successfully", pt_id)
                    update_db_record(uuid, upload_status="COMPLETED",
                                     upload_response=json.dumps(res),
                                     new_tax=tax_amount,
                                     new_total=total_amount,
                                     new_propertyid=pt_id,
                                     new_assessmentnumber=ack_no,
                                     req_json=json.dumps(req),
                                     time_taken=time_taken)
                else:
                    # Some error has occurred
                    print("Error occured while uploading data")
                    print(json.dumps(req, indent=1))
                    print(json.dumps(res, indent=1))
                    update_db_record(uuid, upload_status="ERROR",
                                     upload_response=json.dumps(res),
                                     req_json=json.dumps(req))
            except Exception as ex:
                import traceback
                traceback.print_exc()
                update_db_record(uuid, upload_status="EXCEPTION", upload_response=str(ex))

            if dry_run:
                print("Dry run only, exiting now")
                exit(0)


if __name__ == "__main__":
    main()
