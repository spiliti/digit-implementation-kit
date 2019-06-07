numbers = [
    ('PT/316/2019-20/001112', 'PT-316-100006'),
    ('PT/316/2019-20/001111', 'PT-316-099990'),
]

import json

from config import config
from common import superuser_login, search_receipt, search_property, cancel_receipt

login = superuser_login()
auth_token = login["access_token"]

for receiptNumber, receipt_propertyid in numbers[:]:
    receipts = search_receipt(auth_token, receiptNumbers=receiptNumber)["Receipt"]

    if len(receipts) > 0:
        # print("Receipts found - {}".format(len(receipts)))

        for receipt in receipts:
            propertyid, assessment = receipt["consumerCode"].split(":")

            if receipt_propertyid != propertyid:
                print("Property ID mismatch for receiptnumber={}, Expected={}, Actual={}".format(receiptNumber,
                                                                                                 receipt_propertyid,
                                                                                                 propertyid))
                continue

            tenantid = receipt["tenantId"]
            receipt_status = receipt["Bill"][0]["billDetails"][0]["status"]
            receipt_consumercode = receipt["Bill"][0]["billDetails"][0]["consumerCode"]
            # print(propertyid, assessment, receipt_status, tenantid)
            properties = search_property(auth_token, tenantid, propertyid)

            if "Properties" in properties:
                property = properties["Properties"]
            else:
                print("Property is not valid - {} - {}".format(propertyid, receiptNumber))
                continue

            if receipt_status == "Cancelled":
                # print("Receipt is already cancelled - {}".format(receiptNumber))
                print("CANCELLED")
                continue
            else:
                # print("NOT CANCELLED")
                # print("Receipt is NOT cancelled - {}".format(receiptNumber))
                pass

            # continue

            prop_details = {}

            if len(property) > 0:
                for p in property[0]["propertyDetails"]:
                    assessment_number = p["assessmentNumber"]
                    fy = p["financialYear"]

                    consumer_code = propertyid + ":" + assessment_number
                    if assessment == assessment_number:
                        receipt_fy = fy

                    prop_details[fy] = prop_details.get(fy, [])
                    prop_details[fy].append(consumer_code)
                    # print(assessment_number, fy, consumer_code)

                # if len(prop_details[receipt_fy]) > 1:
                #     print(receiptNumber, receipt_status, propertyid, assessment_number, receipt_fy, prop_details[receipt_fy])

                receipts = \
                    search_receipt(auth_token, consumerCode=",".join(prop_details[receipt_fy]), status="Approved")[
                        "Receipt"]

                # print("Total receipts - {} - {}".format(receiptNumber, len(receipts)))

                if len(receipts) > 1:
                    # Multiple receipts are there, check the order
                    receipts_new = []
                    receipts_new = sorted(receipts, key=lambda item: item["auditDetails"]["createdDate"])
                    latest_receipt = receipts_new[-1]

                    receipt_last_status = latest_receipt["Bill"][0]["billDetails"][0]["status"]
                    receipt_consumercode = latest_receipt["consumerCode"]
                    latest_receipt_number = latest_receipt["receiptNumber"]

                    if receiptNumber != latest_receipt_number:
                        print(
                            "The receipt {} cannot be cancelled. Latest cancellable receipt number - {}".format(
                                receiptNumber, latest_receipt_number
                            ))
                        continue

                # we only have one receipt for the given year, so cancel without any issues
                data = cancel_receipt(auth_token, receiptNumber, receipt_consumercode,
                                      "Receipt cancellation based on PI-4773")

                if "Receipt" not in data:
                    print("Some error occurred - {}".format(receiptNumber), data)
                else:
                    print("receipt cancelled - {}".format(receiptNumber))

            else:
                print("Property not found for - {}".format(receiptNumber))
    else:
        print("Receipt not found - {}".format(receiptNumber))
