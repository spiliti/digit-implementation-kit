numbers = [
    ('PT/1012/2020-21/000351', 'PT-1012-877434'),
]
#tenant_id="pb.testing"
#tenant_id=config.TENANT_ID

import json

from config import config
from common import superuser_login, search_receipt, search_property, cancel_receipt

login = superuser_login()
auth_token = login["access_token"]

for receiptNumber, receipt_propertyid in numbers[:]:
    payments = search_receipt(auth_token, receiptNumbers=receiptNumber,tenantId=config.TENANT_ID)["Payments"]

    if len(payments) > 0:
        # print("Receipts found - {}".format(len(receipts)))

        for payment in payments:
            propertyid = payment["paymentDetails"][0]["bill"]["consumerCode"]

            if receipt_propertyid != propertyid:
                print("Property ID mismatch for receiptnumber={}, Expected={}, Actual={}".format(receiptNumber,
                                                                                                 receipt_propertyid,
                                                                                                 propertyid))
                continue

            tenantid = payment["tenantId"]
            payment_status = payment["paymentStatus"]
            receipt_consumercode = propertyid
            # print(propertyid, assessment, receipt_status, tenantid)
            properties = search_property(auth_token, tenantid, propertyid)

            if "Properties" in properties:
                property = properties["Properties"]
            else:
                print("Property is not valid - {} - {}".format(propertyid, receiptNumber))
                continue

            if payment_status == "CANCELLED":
                print("FOUND as ALREADY CANCELLED ", receiptNumber)
                #print("CANCELLED")
                continue
            else:
                # print("NOT CANCELLED")
                # print("Receipt is NOT cancelled - {}".format(receiptNumber))
                pass

            # continue

            prop_details = {}

            if len(property) > 0:
                #for p in property[0]["propertyDetails"]:
                    #assessment_number = p["assessmentNumber"]
                    #fy = p["financialYear"]

                consumer_code = propertyid
                    #if assessment == assessment_number:
                    #    receipt_fy = fy

                    #prop_details[fy] = prop_details.get(fy, [])
                    #prop_details[fy].append(consumer_code)
                    # print(assessment_number, fy, consumer_code)

                # if len(prop_details[receipt_fy]) > 1:
                #     print(receiptNumber, receipt_status, propertyid, assessment_number, receipt_fy, prop_details[receipt_fy])

                #fetching all payments related to this property

                #property_payments = \
                #    search_receipt(auth_token, consumerCodes=propertyid, status="Approved")[
                #        "Payments"]

                property_payments = \
                    search_receipt(auth_token, consumerCodes=propertyid)[
                        "Payments"]

                # print("Total receipts - {} - {}".format(receiptNumber, len(receipts)))

                if len(property_payments) > 1:
                    # Multiple receipts are there, check the order
                    payments_new = []
                    payments_new = sorted(property_payments, key=lambda item: item["auditDetails"]["createdTime"])
                    latest_payment = payments_new[-1]

                    payment_last_status = latest_payment["paymentStatus"]
                    payment_consumercode = latest_payment["paymentDetails"][0]["bill"]["consumerCode"]
                    latest_receipt_number = latest_payment["paymentDetails"][0]["receiptNumber"]

                    if receiptNumber != latest_receipt_number:
                        print(
                            "The receipt {} cannot be cancelled. Latest cancellable receipt number - {}".format(
                                receiptNumber, latest_receipt_number
                            ))
                        continue

                # we only have one receipt for the given year, so cancel without any issues
                data = cancel_receipt(auth_token, receiptNumber, receipt_consumercode,tenantid,
                                      "Receipt cancellation requested by ULB",payment["id"])

                if "Payments" not in data:
                    print("Some error occurred - {}".format(receiptNumber), data)
                else:
                    print("receipt cancelled - {}".format(receiptNumber))

            else:
                print("Property not found for - {}".format(receiptNumber))
    else:
        print("Receipt not found - {}".format(receiptNumber))
