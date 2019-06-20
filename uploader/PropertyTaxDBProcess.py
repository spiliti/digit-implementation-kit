import psycopg2
import json
import os
from common import superuser_login
from uploader.PropertyTaxParser import IkonProperty

dbname = os.getenv("DB_NAME", "postgres")
dbuser = os.getenv("DB_USER", "postgres")
dbpassword = os.getenv("DB_PASSWORD", "postgres")
tenant = os.getenv("TENANT", "pb.testing")
host = os.getenv("DB_HOST", "localhost")
batch = os.getenv("BATCH_NAME", "1")
connection = psycopg2.connect("dbname={} user={} password={} host={}".format(dbname, dbuser, dbpassword, host))
cursor = connection.cursor()
postgresql_select_Query = """
select row_to_json(pd) from pt_legacy_data as pd where pd.upload_status is NULL and pd.new_locality_code is not null and pd.parent_uuid is null and batchname='{}' limit 10
""".format(batch)


def update_db_record(uuid, **kwargs):
    columns = []
    for key in kwargs.keys():
        columns.append(key + "=%s")

    query = """UPDATE pt_legacy_data SET {} where uuid = %s""".format(",".join(columns))
    cursor.execute(query, list(kwargs.values()) + [uuid])
    connection.commit()
    pass


def main():
    continue_processing = True
    access_token = superuser_login()["access_token"]
    import time

    while continue_processing:
        cursor.execute(postgresql_select_Query)
        data = cursor.fetchmany(10)

        #continue_processing = False
        if not data:
            print ("No more data to process. Script exiting")
            continue_processing = False
            cursor.close()
            connection.close()

        for row in data:
            json_data = row[0]
            uuid = json_data["uuid"]
            print ('Processing {}'.format(uuid))
            try:
                p = IkonProperty()
                p.process_record(json_data, tenant)

                start = time.clock()
                req, res = p.upload_property(access_token)
                time_taken = time.clock() - start

                if "Properties" in res:
                    pt_id = res["Properties"][0]["propertyId"]
                    ack_no = res["Properties"][0]["acknowldgementNumber"]
                    calc = res["Properties"][0]["propertyDetails"][0]["calculation"]
                    total_amount = calc["totalAmount"]
                    tax_amount = calc["taxAmount"]
                    # upload_status = "COMPLETED"
                    print("Record updloaded successfully")
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
                    print(json.dumps(res))
                    update_db_record(uuid, upload_status="ERROR",
                                     upload_response=json.dumps(res),
                                     req_json=json.dumps(req))
            except Exception as ex:
                import traceback
                traceback.print_exc()
                update_db_record(uuid, upload_status="EXCEPTION", upload_response=str(ex))



if __name__ == "__main__":
    main()
