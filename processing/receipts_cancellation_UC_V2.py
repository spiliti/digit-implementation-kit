import json

from config import config
from common import superuser_login, search_receipt, search_property, cancel_receipt

login = superuser_login()
auth_token = login["access_token"]
numbers = [
    ('MP/504/2020-21/002909')
]

#businessservice='RT.Municipal_Shops_Rent'
businessservice='UC'

Ticket_No=" "

reason_for_cancellation = "requested by ulb through Ticket "+Ticket_No

for receiptNumber in numbers:
    payments = search_receipt(auth_token, receiptNumbers=receiptNumber,tenantId=config.TENANT_ID,businessCode=businessservice)["Payments"]

    if len(payments) > 0:
        #print("Receipts found {}".format(len(payments)))
        for payment in payments:
            receipt_application_number = payment["paymentDetails"][0]["bill"]["consumerCode"]
            #print("application number ", receipt_application_number)

            #if '' != receipt_application_number:
            #    print("UC Application number mismatch for receiptnumber={}, Expected={}, Actual={}".format(receiptNumber, '', receipt_application_number))
            #    continue

            tenantid = payment["tenantId"]  # this block can be removed as we already searched receipts only that belong to desired tenant configred as config.TENANT_ID
            if tenantid != config.TENANT_ID:
                print("Receipt no {} doesnot belong to tenant {}".format(receiptNumber,config.TENANT_ID))
                continue

            payment_status = payment["paymentStatus"]
            receipt_consumercode = receipt_application_number

            if payment_status == "CANCELLED":
                print("FOUND as ALREADY CANCELLED ", receiptNumber)
                continue
            else:
                pass

            paymentId=payment["id"]
            data = cancel_receipt(auth_token, receiptNumber, receipt_consumercode,tenantid,
                                  reason_for_cancellation,paymentId,business_code=businessservice)

            if "Payments" not in data:
                print("Some error occurred - {}".format(receiptNumber), data)
            else:
                print("receipt cancelled - {}".format(receiptNumber))

    else:
        print("Receipt not found - {} or doesnot belong to tenant {}".format(receiptNumber,config.TENANT_ID))
