import json

from config import config
from common import superuser_login, search_receipt, search_property, cancel_receipt, search_FireNOC

login = superuser_login()
auth_token = login["access_token"]
numbers = [
    ('FN/801/2020-21/xxxxx', 'PB-FN-2020-07-09-xxxxxx'),
]
tenant_id=config.TENANT_ID
ticket_no=""

reason_for_cancellation = "Receipt cancellation requested by ULB through Ticket No. "+ticket_no


for receiptNumber, fn_application_number in numbers[:]:
    # Check whether trade license issued against this appliction
    FNOC_detail = search_FireNOC(auth_token, fn_application_number)
    # print(TL_detail)
    if FNOC_detail["FireNOCs"] != None and len(FNOC_detail["FireNOCs"]) > 0:  # if NOC  found
        if FNOC_detail["FireNOCs"][0]["fireNOCDetails"]["status"] == "APPROVED":  # and is in APPROVED status
            Exit_msg = "Not allowed to cancel receipt number " + receiptNumber + " or Application Number "+fn_application_number+" APPROVED FireNOC FOUND with NOC No " + \
                       FNOC_detail["FireNOCs"][0]["fireNOCNumber"] + ", please cancel the issued NOC before canceling this receipt"
            print(Exit_msg)
            continue  # continue to next cancellation request

    # if license not found or is not in Approved Status then search the receipt and proceed to cancel


    receipts = search_receipt(auth_token, receiptNumbers=receiptNumber)["Receipt"]

    if len(receipts) > 0:
        # print("Receipts found - {}".format(len(receipts)))

        for receipt in receipts:
            receipt_application_number = receipt["consumerCode"]

            if fn_application_number != receipt_application_number:
                print("Fire NOC Application number mismatch for receiptnumber={}, Expected={}, Actual={}".format(receiptNumber, fn_application_number, receipt_application_number))
                continue

            tenantid = receipt["tenantId"]
            if tenant_id!=tenantid:
                print("This receipt ",receiptNumber," doesnot belong to tenant ",tenant_id)
                continue
            receipt_status = receipt["Bill"][0]["billDetails"][0]["status"]
            receipt_consumercode = receipt["Bill"][0]["billDetails"][0]["consumerCode"]

            if receipt_status == "Cancelled":
                print("ALREADY CANCELLED")
                continue
            else:
                pass

            data = cancel_receipt(auth_token, receiptNumber, receipt_consumercode,tenant_id,reason_for_cancellation)

            if "Receipt" not in data:
                print("Some error occurred - {}".format(receiptNumber), data)
            else:
                print("receipt cancelled - {}".format(receiptNumber))

    else:
        print("Receipt not found - {}".format(receiptNumber))
