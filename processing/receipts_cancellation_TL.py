import json
import sys

from config import config
from common import superuser_login, search_receipt, search_property, cancel_receipt, search_TL

login = superuser_login()
auth_token = login["access_token"]
numbers = [

    ('TL/1012/2020-21/000074','PB-TL-2020-04-14-016221'),
    ('TL/1210/2019-20/000030', 'PB-TL-2019-04-25-002422')
]
tenant_id="pb.testing"

reason_for_cancellation = "Receipt cancellation based on PI-5452"

for receiptNumber, tl_application_number in numbers[:]:
    #Check whether trade license issued against this appliction
    TL_detail = search_TL(auth_token, tl_application_number)
    #print(TL_detail)
    if TL_detail["Licenses"]!=None and len(TL_detail["Licenses"]) > 0:  # if licene  founs
        if TL_detail["Licenses"][0]["status"] == "APPROVED":  # and is in APPROVED status
            Exit_msg="Not allowed to cancel receipt number " + receiptNumber + " APPROVED LICENSE FOUND with License No "+TL_detail["Licenses"][0]["licenseNumber"]+", please cancel the issued license before canceling this receipt"
            print(Exit_msg)
            continue   #continue to next cancellation request

     #if license not found or is not in Approved Status then search the receipt and proceed to cancel

    receipts = search_receipt(auth_token, receiptNumbers=receiptNumber)["Receipt"]

    if len(receipts) > 0:
        # print("Receipts found - {}".format(len(receipts)))

        for receipt in receipts:
            receipt_application_number = receipt["consumerCode"]
            if tl_application_number != receipt_application_number:
                print("TL Application number mismatch for receiptnumber={}, Expected={}, Actual={}".format(receiptNumber, tl_application_number, receipt_application_number))
                continue

            tenantid = receipt["tenantId"]
            receipt_status = receipt["Bill"][0]["billDetails"][0]["status"]
            receipt_consumercode = receipt["Bill"][0]["billDetails"][0]["consumerCode"]

            if receipt_status == "Cancelled":
                print("ALREADY CANCELLED")
                continue
            else:
                pass

            data = cancel_receipt(auth_token, receiptNumber, receipt_consumercode,tenant_id,
                                  reason_for_cancellation)

            if "Receipt" not in data:
                print("Some error occurred - {}".format(receiptNumber), data)
            else:
                print("receipt cancelled - {}".format(receiptNumber))

    else:
        print("Receipt not found - {}".format(receiptNumber))
        