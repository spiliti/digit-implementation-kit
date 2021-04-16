import json

from config import config
from common import superuser_login, search_receipt, search_property, cancel_receipt, search_TL

login = superuser_login()
auth_token = login["access_token"]
numbers = [
    #('TL/1802/2021-22/001260', 'PB-TL-2021-04-12-056396'),
    ('TL/1802/2021-22/001260','PB-TL-2021-04-12-056396')
]
tenant_id=config.TENANT_ID

ticket_no=""
reason_for_cancellation = "Receipt cancellation requested by ULB through Ticket No. "+ticket_no

for receiptNumber, tl_application_number in numbers[:]:
    # Check whether trade license issued against this appliction
    TL_detail = search_TL(auth_token, tl_application_number)
    # print(TL_detail)
    if TL_detail["Licenses"] != None and len(TL_detail["Licenses"]) > 0:  # if licene  founs
        if TL_detail["Licenses"][0]["status"] == "APPROVED":  # and is in APPROVED status
            Exit_msg = "Not allowed to cancel receipt number " + receiptNumber + " APPROVED LICENSE FOUND with License No " + \
                       TL_detail["Licenses"][0][
                           "licenseNumber"] + ", please cancel the issued license before canceling this receipt"
            print(Exit_msg)
            continue  # continue to next cancellation request

    # if license not found or is not in Approved Status then search the receipt and proceed to cancel

    payments = search_receipt(auth_token, receiptNumbers=receiptNumber,tenantId=tenant_id,businessCode='TL')["Payments"]

    if len(payments) > 0:
        # print("Receipts found - {}".format(len(receipts)))

        for payment in payments:
            receipt_application_number = payment["paymentDetails"][0]["bill"]["consumerCode"]

            if tl_application_number != receipt_application_number:
                print("TL Application number mismatch for receiptnumber={}, Expected={}, Actual={}".format(receiptNumber, tl_application_number, receipt_application_number))
                continue

            tenantid = payment["tenantId"]
            payment_status = payment["paymentStatus"]
            receipt_consumercode = receipt_application_number

            if payment_status == "CANCELLED":
                print("ALREADY CANCELLED")
                continue
            else:
                pass

            paymentId = payment["id"]
            data = cancel_receipt(auth_token, receiptNumber, receipt_consumercode,tenant_id,
                                  reason_for_cancellation,paymentId,business_code='TL')

            if "Payments" not in data:
                print("Some error occurred - {}".format(receiptNumber), data)
            else:
                print("receipt cancelled - {}".format(receiptNumber))

    else:
        print("Receipt not found - {}".format(receiptNumber))
