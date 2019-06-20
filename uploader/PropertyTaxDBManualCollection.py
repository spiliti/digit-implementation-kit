import json
import os
import time

import psycopg2

from common import superuser_login
from uploader.PropertyTaxDBProcess import update_db_record
from uploader.PropertyTaxManualCollection import create_manual_receipt_collection, to_epoch

dbname = os.getenv("DB_NAME", "postgres")
dbuser = os.getenv("DB_USER", "postgres")
dbpassword = os.getenv("DB_PASSWORD", "postgres")
tenant = os.getenv("TENANT", "pb.testing")
host = os.getenv("DB_HOST", "localhost")
batch = os.getenv("BATCH_NAME", "1")


def main():
    connection = psycopg2.connect("dbname={} user={} password={} host={}".format(dbname, dbuser, dbpassword, host))
    cursor = connection.cursor()
    postgresql_select_Query = """
        select row_to_json(pd) from pt_legacy_data as pd where  
        pd.upload_status ='COMPLETED' and pd.receipt_status is NULL
        and batchname = '{}'
        and parent_uuid is null  
        limit 1
    """.format(batch)

    auth_token = superuser_login()["access_token"]
    cursor.execute(postgresql_select_Query)
    data = cursor.fetchmany(10)

    print ("found data for {}".format(len(data)))

    for row in data:
        json_data = row[0]
        uuid = json_data["uuid"]

        print ("processing uuid - {}".format(uuid))
        new_propertyid = json_data["new_propertyid"]

        session = json_data["Session"].replace("-20", "-")

        owner = json_data["Owner"].split('/')[0].strip()

        amount = {
            "PT_ADHOC_REBATE": 0,
            "PT_ADVANCE_CARRYFORWARD": 0,
            "PT_OWNER_EXEMPTION": 0,
            "PT_TIME_REBATE": -round(float(json_data["Rebate"])),
            "PT_UNIT_USAGE_EXEMPTION": -round(float(json_data["ExemptionAmt"])),
            "PT_ADHOC_PENALTY": 0,
            "PT_TAX": round(float(json_data["GrossTax"])),
            "PT_FIRE_CESS": round(float(json_data["FireCharges"])),
            "PT_CANCER_CESS": 0,
            "PT_TIME_PENALTY": round(float(json_data["Penalty"])),
            "PT_TIME_INTEREST": round(float(json_data["InterestAmt"]))
        }

        g8_book_no = json_data["G8BookNo"]

        g8_receipt_no = json_data["G8ReceiptNo"]

        if g8_receipt_no and g8_book_no:
            old_g8_receiptno = g8_book_no + '/' + g8_receipt_no
        elif g8_receipt_no:
            old_g8_receiptno = g8_receipt_no
        else:
            old_g8_receiptno = json_data["AcknowledgementNo"]

        payment_date = json_data["PaymentDate"]

        tax_amt = float(json_data["TaxAmt"])

        payment_mode = "Cash"  # json_data["PaymentMode"]

        try:
            start_time = time.time()
            receipt_request, receipt_response = create_manual_receipt_collection(auth_token, tenant,
                                                                                 new_propertyid, session, owner,
                                                                                 amount,
                                                                                 old_g8_receiptno,
                                                                                 to_epoch(payment_date),
                                                                                 tax_amt, payment_mode)
            time_taken_receipt = time.time() - start_time

            if "Receipt" in receipt_response:
                print("receipt creation successfull")
                update_db_record(uuid, receipt_number=receipt_response["Receipt"][0]["Bill"][0]["billDetails"][0][
                    "receiptNumber"],
                                 receipt_status="COMPLETED", time_taken_receipt=time_taken_receipt,
                                 receipt_response=json.dumps(receipt_response),
                                 receipt_request=json.dumps(receipt_request))
            else:
                print("receipt create failed with error")
                # Some error has occurred
                update_db_record(uuid, receipt_status="ERROR", receipt_response=json.dumps(receipt_response),
                                 receipt_request=json.dumps(receipt_request))

                pass
        except Exception as ex:
            import traceback
            traceback.print_exc()
            update_db_record(uuid, receipt_status="EXCEPTION", receipt_response=str(ex))


if __name__ == "__main__":
   main()
