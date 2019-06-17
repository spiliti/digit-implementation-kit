import json

from config import config
from common import superuser_login, search_receipt, search_property, cancel_receipt

login = superuser_login()
auth_token = login["access_token"]
numbers = [
    ('TL/1210/2019-20/000030', 'PB-TL-2019-04-25-002422'),
]

reason_for_cancellation = "Receipt cancellation based on PI-5452"

for receiptNumber, tl_application_number in numbers[:]:
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
                print("CANCELLED")
                continue
            else:
                pass

            data = cancel_receipt(auth_token, receiptNumber, receipt_consumercode,
                                  reason_for_cancellation)

            if "Receipt" not in data:
                print("Some error occurred - {}".format(receiptNumber), data)
            else:
                print("receipt cancelled - {}".format(receiptNumber))

    else:
        print("Receipt not found - {}".format(receiptNumber))
