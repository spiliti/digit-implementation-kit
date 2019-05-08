import json

from pandas import read_html

from common import open_excel_file
from uploader.PropertyTax import RequestInfo, PropertyCreate, Property, PropertyDetail, Owner, CitizenInfo, Unit, \
    Address, Locality
import re

FLOOR_MAP = {
    "Upper Ground Floor": "0",
    "Other Floor": "0",
    "Lower Ground Floor": "-1",
    "Ground Floor - Vacant": "0",
    "Ground Floor - Vacant In Use": "0",
    "Ground Floor": "0",
    "Basement 2": "-2",
    "Basement 1": "-1",
    "Basement 3": "-3",
    "13th Floor": "13",
    "12th Floor": "12",
    "11th Floor": "11",
    "10th Floor": "10",
    "9th Floor": "9",
    "8th Floor": "8",
    "7th Floor": "7",
    "5th Floor": "5",
    "4th Floor": "4",
    "3rd Floor": "3",
    "2nd Floor": "2",
    "1st Floor": "1",
}

OC_MAP = {
    "Self Occupied": "SELFOCCUPIED",
    "Un-Productive": "UNOCCUPIED",
    "Rented": "RENTED"
}

from json import JSONEncoder

class MyEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__


def convert_json(d, convert):
    new_d = {}
    for k, v in d.items():
        if isinstance(v, list):
            new_d[convert(k)] = []
            for i, vv in enumerate(v):
                new_d[convert(k)].append(convert_json(v[i], convert))
        else:
            new_d[convert(k)] = convert_json(v,convert) if isinstance(v,dict) else v
    return new_d


camel_pat = re.compile(r'([A-Z])')
under_pat = re.compile(r'_([a-z])')


def camel_to_underscore(name):
    return camel_pat.sub(lambda x: '_' + x.group(1).lower(), name)


def underscore_to_camel(name):
    return under_pat.sub(lambda x: x.group(1).upper(), name)


def convert_load(*args, **kwargs):
    json_obj = json.load(*args, **kwargs)
    return convert_json(json_obj, camel_to_underscore)


def convert_dump(*args, **kwargs):
    args = (convert_json(args[0], underscore_to_camel),) + args[1:]
    json.dump(*args, **kwargs)


def residential_house_parse(property, context):
    pd: PropertyDetail = property.property_details[0]
    property.parse_owner_information(context["Owner"], context)
    property.property_details[0].units = []

    floor_set = set()

    for floor, covered_area, usage, occupancy, _, tax in parse_flat_information(context["Floor"]):
        unit = Unit(floor_no=FLOOR_MAP[floor],
                    usage_category_major="RESIDENTIAL",
                    occupancy_type=OC_MAP[occupancy],
                    unit_area=float(covered_area)/9)

        if OC_MAP[occupancy] == "RENTED":
            unit.arv = 0
        floor_set.add(FLOOR_MAP[floor])
        pd.units.append(unit)

    property.old_property_id = "RID{}".format(context["ReturnId"])
    property.additional_details = {
        "legacyInfo" : {
            "ReturnID": context["ReturnId"],
            "UploadYear": context["Session"],
            "TaxAmt": context["TaxAmt"],
            "AcknowledgementNo": context["AcknowledgementNo"],
            "Colony": context["Colony"],
            "Sector": context["Sector"],
            "ExemptionCategory": context["ExemptionCategory"],
            "TotalCoveredArea": context["TotalCoveredArea"],
            "GrossTax": context["GrossTax"],
            "AmountPaid": context["AmountPaid"]
        }
    }

    pd.usage_category_major = "RESIDENTIAL"

    pd.property_type = "BUILTUP"
    pd.no_of_floors = len(floor_set)

    pd.ownership_category = "INDIVIDUAL"

    if len(pd.owners) > 1:
        pd.sub_ownership_category = "MULTIPLEOWNERS"
    else:
        pd.sub_ownership_category = "SINGLEOWNER"

    if len(pd.units) == 1 and "0" not in floor_set:
        pd.property_sub_type = "SHAREDPROPERTY"
        pd.build_up_area = context["PlotArea"]
    else:
        pd.property_sub_type = "INDEPENDENTPROPERTY"
        pd.land_area = context["PlotArea"]

    property.tenant_id = 'pb.testing'
    locality = Locality(code=context["new_locality_code"])
    property.address = Address(city="Jalandhar", door_no=context["HouseNo"],locality=locality)
    pd.financial_year = "2019-20"
    x = MyEncoder().encode(property)
    print (json.dumps(convert_json(json.loads(x), underscore_to_camel), indent=2))


BC_MAP = {
    "Residential Houses": residential_house_parse,
    "Government buildings, including buildings of Government Undertakings, Board or Corporation": "",
    "Industrial (any manufacturing unit), educational institutions, and godowns": "",
    "Commercial buildings including Restaurants (except multiplexes, malls, marriage palaces)": "",
    "Flats": "",
    "Hotels - Having beyond 50 rooms": "",
    "Others": "",
    "Mix-Use Building used for multiple purposes (like Residential+Commercial+Industrial)": "",
    "Institutional buildings (other than educational institutions), including community halls/centres, sports stadiums, social clubs, bus stands, gold clubs, and such like buildings used for public purpose": "",
    "Hotels - Having 50 rooms or below": "",
    "Multiplex, Malls, Shopping Complex/Center etc.": "",
    "Vacant Plot": "",
    "Marriage Palaces": ""
}

# OTHERINDUSTRIAL,OTHERINDUSTRIALSUBMINOR,INDUSTRIAL,
# INSTITUTIONAL,
# OTHERS
# INDIVIDUAL, SINGLEOWNER
# INDIVIDUAL, MULTIPLEOWNERS
# INSTITUTIONALPRIVATE, PRIVATECOMPANY
# INSTITUTIONALPRIVATE, NGO
# INSTITUTIONALPRIVATE, PRIVATETRUST
# INSTITUTIONALPRIVATE, PRIVATEBOARD
# OTHERSPRIVATEINSTITUITION,
#
# INSTITUTIONALGOVERNMENT, STATEGOVERNMENT
# OTHERGOVERNMENTINSTITUITION
# CENTRALGOVERNMENT
# EVENTSPACE > MARRIAGEPALACE
# MULTIPLEX > ENTERTAINMENT
# RETAIL > MALLS



class IkonProperty(Property):

    def __init__(self, *args, **kwargs):
        super(IkonProperty, self).__init__()
        self.additional_details = {}
        self.property_details = [PropertyDetail(owners=[], additional_details={
            "inflammable": False,
            "heightAbove36Feet": False
        })]

    def parse_owner_information(self, owners, context=None):
        for name, father_name, mobile in parse_owners_information(owners):
            owner = Owner(name=name, father_or_husband_name=father_name, mobile_number=mobile)

            if 'W/O' in name:
                name, father_name = list(map(str.strip, name.split('W/O')))
                father_name = 'W/O ' + father_name
            elif 'D/O' in name:
                name, father_name = list(map(str.strip, name.split('D/O')))
                father_name = 'D/O ' + father_name
            elif 'S/O' in name:
                name, father_name = list(map(str.strip, name.split('S/O')))
                father_name = 'S/O ' + father_name

            if 'W/O' in father_name:
                owner.relationship = 'HUSBAND'
                owner.gender = 'Female'
            else:
                owner.relationship = 'FATHER'
                owner.gender = 'Male'

            owner.owner_type = 'NONE'

            self.property_details[0].owners.append(owner)

            if self.property_details[0].citizen_info is None:
                self.property_details[0].citizen_info = CitizenInfo(name=name, mobile_number=mobile)

    def parse_floor_information(self, text, context=None):
        if text.strip() == 'Â':
            self.property_details[0].property_type = "VACANT"
            # "usageCategoryMajor": "RESIDENTIAL",
            # "propertySubType": None,
            # "landArea": "90000",
            # "buildUpArea": None,
            # "propertyType": "VACANT",
            # "noOfFloors": 1,
            # "subOwnershipCategory": "SINGLEOWNER",
            # "ownershipCategory": "INDIVIDUAL",

        else:
            pass

    def process_record(self, context):
        func = BC_MAP[context["BuildingCategory"]]
        if func:
            func(self, context)
        else:
            raise Exception("No Mapping function")

        pass


class PropertyTaxParser():
    def create_property_object(self, auth_token):
        ri = RequestInfo(auth_token=auth_token)

        property = IkonProperty()
        PropertyCreate(ri, [property])


owner_pattern = re.compile("(?<![DSNW])/(?![OA])", re.I)


def parse_owners_information(text):
    text = text or """ASHOK KUMAR / ACHHRU RAM / 9779541015JEET KUMARI / W/O ASHOK KUMAR / 9779541015"""

    info = list(map(str.strip, owner_pattern.split(text, 2)))
    owners = []

    pat = re.compile("^\d+|^N/?A")

    while "/" in info[-1]:
        last_element = info[-1]
        # get the phone number
        phone = pat.findall(last_element)
        if len(phone) > 1:
            raise Exception("Issue occured")
        elif len(phone) == 1:
            info[-1] = phone[0]
        else:
            info[-1] = ""
            break

        split_index = len(info[-1])

        if len(last_element) > split_index:
            owners.append(info)
            info = list(map(str.strip, owner_pattern.split(last_element[split_index:], 2)))
        else:
            break

    if len(info) > 0:
        owners.append(info)

    return owners


def parse_flat_information(text):
    text = text or """Ground Floor / 1100.00 / Residential / Self Occupied / Pucca / 939.58Ground Floor - Vacant In Use / 250.00 / Residential / Self Occupied / Pucca / 185.421st Floor / 1100.00 / Residential / Self Occupied / Pucca / 613.252nd Floor / 1100.00 / Residential / Self Occupied / Pucca / 368.50"""

    info = list(map(str.strip, owner_pattern.split(text, 5)))
    owners = []
    while "/" in info[-1]:
        last_element = info[-1]

        # get the phone number
        split_index = last_element.find(".") + 3
        info[-1] = last_element[:split_index]
        owners.append(info)
        info = list(map(str.strip, owner_pattern.split(last_element[split_index:], 5)))

    owners.append(info)

    return owners



data = [
{"SrNo":"1","ReturnId":"43","AcknowledgementNo":"ACK-131672065564201961","EntryDate":"03/04/18","Zone":"JALANDHAR","Sector":"1","Colony":"Anand Nagar","HouseNo":"413","Owner":"IQBAL JIT SINGH / JASWANT SINGH / 9855002240TEJVINDER SINGH / JASWANT SINGH / 9855002240","Floor":"Ground Floor / 549.00 / Residential / Self Occupied / Pucca / 183.00Ground Floor - Vacant / 1251.00 / Residential / Self Occupied / Pucca / 209.00","ResidentialRate":"0","CommercialRate":"0","ExemptionCategory":"Non-Exempted","LandUsedType":"Others","Usage":"Built Up","PlotArea":"200","TotalCoveredArea":"549","GrossTax":"392","FireCharges":"0","InterestAmt":"0","Penalty":"0","Rebate":"39","ExemptionAmt":"0","TaxAmt":"353","AmountPaid":"353","PaymentMode":"Cash","TransactionID":"","Bank":"","G8BookNo":"27514","G8ReceiptNo":"6","PaymentDate":"03/04/18","PropertyType":"Residential","BuildingCategory":"Residential Houses","Session":"2018-2019","Remarks":"","uuid":"8c2a7418-1d09-4d30-9f09-4a7b8cedef23","previous_returnid":None,"status":"STAGE1","tenantid":None,"batchname":None,"new_propertyid":None,"new_locality_code":"JALLC340"},
{"SrNo":"2","ReturnId":"50","AcknowledgementNo":"ACK-131672073888111979","EntryDate":"03/04/18","Zone":"JALANDHAR","Sector":"1","Colony":"Janta Colony","HouseNo":"N/A","Owner":"MANPREET SINGH AULAKH / RANJIT SINGH AULAKH / 9501501007","Floor":"Ground Floor / 1620.00 / Residential / Self Occupied / Pucca / 540.00Ground Floor - Vacant / 657.00 / Residential / Self Occupied / Pucca / 110.001st Floor / 1170.00 / Residential / Self Occupied / Pucca / 195.00","ResidentialRate":"0","CommercialRate":"0","ExemptionCategory":"Non-Exempted","LandUsedType":"Others","Usage":"Built Up","PlotArea":"253","TotalCoveredArea":"2790","GrossTax":"845","FireCharges":"0","InterestAmt":"0","Penalty":"0","Rebate":"85","ExemptionAmt":"0","TaxAmt":"760","AmountPaid":"760","PaymentMode":"Cash","TransactionID":"","Bank":"","G8BookNo":"27514","G8ReceiptNo":"9","PaymentDate":"03/04/18","PropertyType":"Residential","BuildingCategory":"Residential Houses","Session":"2018-2019","Remarks":"","uuid":"8aeb2b94-b6fd-4dfb-ad88-10929740e9fa","previous_returnid":None,"status":"STAGE1","tenantid":None,"batchname":None,"new_propertyid":None,"new_locality_code":"JALLC566"},
{"SrNo":"4","ReturnId":"156","AcknowledgementNo":"ACK-131672891544719647","EntryDate":"04/04/18","Zone":"JALANDHAR","Sector":"1","Colony":"Friends Colony","HouseNo":"6:00 AM","Owner":"S.L AGNISH/SHANTA SHARMA / KHUSHI RAM / 9876266781","Floor":"Ground Floor / 1449.00 / Residential / Self Occupied / Pucca / 805.001st Floor / 1449.00 / Residential / Self Occupied / Pucca / 403.00","ResidentialRate":"0","CommercialRate":"0","ExemptionCategory":"Non-Exempted","LandUsedType":"Others","Usage":"Built Up","PlotArea":"161","TotalCoveredArea":"2898","GrossTax":"1208","FireCharges":"0","InterestAmt":"0","Penalty":"0","Rebate":"121","ExemptionAmt":"0","TaxAmt":"1087","AmountPaid":"1087","PaymentMode":"Cash","TransactionID":"","Bank":"","G8BookNo":"27515","G8ReceiptNo":"24","PaymentDate":"04/04/18","PropertyType":"Residential","BuildingCategory":"Residential Houses","Session":"2018-2019","Remarks":"","uuid":"7f40c849-1f3f-493c-934b-de9c9d7f2ddb","previous_returnid":None,"status":"STAGE1","tenantid":None,"batchname":None,"new_propertyid":None,"new_locality_code":"JALLC140"},
{"SrNo":"5","ReturnId":"158","AcknowledgementNo":"ACK-131672891840779817","EntryDate":"04/04/18","Zone":"JALANDHAR","Sector":"1","Colony":"Friends Colony","HouseNo":"1","Owner":"SARITA / SOM DATT SHARMA / 9814814775","Floor":"Ground Floor / 1656.00 / Residential / Self Occupied / Pucca / 920.001st Floor / 1656.00 / Residential / Self Occupied / Pucca / 460.00","ResidentialRate":"0","CommercialRate":"0","ExemptionCategory":"Non-Exempted","LandUsedType":"Others","Usage":"Built Up","PlotArea":"184","TotalCoveredArea":"3312","GrossTax":"1380","FireCharges":"0","InterestAmt":"0","Penalty":"0","Rebate":"138","ExemptionAmt":"0","TaxAmt":"1242","AmountPaid":"1242","PaymentMode":"Cash","TransactionID":"","Bank":"","G8BookNo":"27515","G8ReceiptNo":"25","PaymentDate":"04/04/18","PropertyType":"Residential","BuildingCategory":"Residential Houses","Session":"2018-2019","Remarks":"","uuid":"6e01e309-1e14-4d5e-91bb-26c5ac7e02d1","previous_returnid":None,"status":"STAGE1","tenantid":None,"batchname":None,"new_propertyid":None,"new_locality_code":"JALLC140"},
{"SrNo":"7","ReturnId":"415","AcknowledgementNo":"ACK-131673854451010127","EntryDate":"05/04/18","Zone":"JALANDHAR","Sector":"1","Colony":"Angad Nagar","HouseNo":"128","Owner":"HARBHAJAN SINGH / THAKUR SINGH / 9915664430","Floor":"Ground Floor / 1800.00 / Residential / Self Occupied / Pucca / 600.001st Floor / 1800.00 / Residential / Self Occupied / Pucca / 300.00","ResidentialRate":"0","CommercialRate":"0","ExemptionCategory":"Non-Exempted","LandUsedType":"Others","Usage":"Built Up","PlotArea":"200","TotalCoveredArea":"3600","GrossTax":"900","FireCharges":"0","InterestAmt":"0","Penalty":"0","Rebate":"90","ExemptionAmt":"0","TaxAmt":"810","AmountPaid":"810","PaymentMode":"Cash","TransactionID":"","Bank":"","G8BookNo":"27518","G8ReceiptNo":"34","PaymentDate":"05/04/18","PropertyType":"Residential","BuildingCategory":"Residential Houses","Session":"2018-2019","Remarks":"","uuid":"9a0c67f2-9b2a-4181-9c77-aebd4762e240","previous_returnid":None,"status":"STAGE1","tenantid":None,"batchname":None,"new_propertyid":None,"new_locality_code":"JALLC341"},
{"SrNo":"8","ReturnId":"451","AcknowledgementNo":"ACK-131674001043180235","EntryDate":"05/04/18","Zone":"JALANDHAR","Sector":"1","Colony":"Anand Nagar","HouseNo":"B-1/373","Owner":"SURJEET KAUR / HARJEET SINGH / 9872093750","Floor":"Ground Floor / 2106.00 / Residential / Self Occupied / Pucca / 702.00Ground Floor - Vacant / 2097.00 / Residential / Self Occupied / Pucca / 350.00","ResidentialRate":"0","CommercialRate":"0","ExemptionCategory":"Non-Exempted","LandUsedType":"Others","Usage":"Built Up","PlotArea":"467","TotalCoveredArea":"2106","GrossTax":"1052","FireCharges":"0","InterestAmt":"0","Penalty":"0","Rebate":"105","ExemptionAmt":"0","TaxAmt":"947","AmountPaid":"947","PaymentMode":"Online","TransactionID":"2018TXN000451","Bank":"","G8BookNo":"27634","G8ReceiptNo":"40","PaymentDate":"05/04/18","PropertyType":"Residential","BuildingCategory":"Residential Houses","Session":"2018-2019","Remarks":"NO","uuid":"d5098977-cc5d-4054-89ec-3d44ab453ca4","previous_returnid":None,"status":"STAGE1","tenantid":None,"batchname":None,"new_propertyid":None,"new_locality_code":"JALLC340"},
{"SrNo":"10","ReturnId":"482","AcknowledgementNo":"ACK-131674637511723224","EntryDate":"06/04/18","Zone":"JALANDHAR","Sector":"1","Colony":"New Anand Nagar","HouseNo":"119","Owner":"RAGHBIR SINGH / PURAN SINGH / 9815017680","Floor":"Ground Floor / 1800.00 / Residential / Self Occupied / Pucca / 600.00Ground Floor - Vacant / 270.00 / Residential / Self Occupied / Pucca / 45.001st Floor / 1600.00 / Residential / Self Occupied / Pucca / 267.00","ResidentialRate":"0","CommercialRate":"0","ExemptionCategory":"Non-Exempted","LandUsedType":"Others","Usage":"Built Up","PlotArea":"230","TotalCoveredArea":"3400","GrossTax":"912","FireCharges":"0","InterestAmt":"0","Penalty":"0","Rebate":"91","ExemptionAmt":"0","TaxAmt":"821","AmountPaid":"821","PaymentMode":"Cash","TransactionID":"","Bank":"","G8BookNo":"26867","G8ReceiptNo":"17","PaymentDate":"06/04/18","PropertyType":"Residential","BuildingCategory":"Residential Houses","Session":"2018-2019","Remarks":"","uuid":"17c2482c-5ea8-4287-bcad-16221f948a20","previous_returnid":None,"status":"STAGE1","tenantid":None,"batchname":None,"new_propertyid":None,"new_locality_code":"JALLC683"},
{"SrNo":"11","ReturnId":"483","AcknowledgementNo":"ACK-131674637943483282","EntryDate":"06/04/18","Zone":"JALANDHAR","Sector":"1","Colony":"Anand Nagar","HouseNo":"B-1-329","Owner":"AJIT SINGH / SANTA SINGH / 8427272123KULBIR SINGH / SWARAN SINGH / 8427272123","Floor":"Ground Floor / 1500.00 / Residential / Self Occupied / Pucca / 500.00Ground Floor - Vacant / 300.00 / Residential / Self Occupied / Pucca / 50.001st Floor / 1200.00 / Residential / Self Occupied / Pucca / 200.00","ResidentialRate":"0","CommercialRate":"0","ExemptionCategory":"Non-Exempted","LandUsedType":"Others","Usage":"Built Up","PlotArea":"200","TotalCoveredArea":"2700","GrossTax":"750","FireCharges":"0","InterestAmt":"0","Penalty":"0","Rebate":"75","ExemptionAmt":"0","TaxAmt":"675","AmountPaid":"675","PaymentMode":"Cash","TransactionID":"","Bank":"","G8BookNo":"26867","G8ReceiptNo":"18","PaymentDate":"06/04/18","PropertyType":"Residential","BuildingCategory":"Residential Houses","Session":"2018-2019","Remarks":"","uuid":"da71840a-4213-401f-8eeb-e0b75e009236","previous_returnid":None,"status":"STAGE1","tenantid":None,"batchname":None,"new_propertyid":None,"new_locality_code":"JALLC340"},
{"SrNo":"12","ReturnId":"575","AcknowledgementNo":"ACK-131675516782322293","EntryDate":"07/04/18","Zone":"JALANDHAR","Sector":"1","Colony":"Anand Nagar","HouseNo":"46/2","Owner":"HARJIT SINGH / GIAN SINGH / 9872093750","Floor":"Ground Floor / 702.00 / Residential / Self Occupied / Pucca / 234.00Ground Floor - Vacant / 1701.00 / Residential / Self Occupied / Pucca / 284.001st Floor / 702.00 / Residential / Self Occupied / Pucca / 117.00","ResidentialRate":"0","CommercialRate":"0","ExemptionCategory":"Non-Exempted","LandUsedType":"Others","Usage":"Built Up","PlotArea":"267","TotalCoveredArea":"1404","GrossTax":"635","FireCharges":"0","InterestAmt":"0","Penalty":"0","Rebate":"64","ExemptionAmt":"0","TaxAmt":"571","AmountPaid":"571","PaymentMode":"Online","TransactionID":"2018TXN000575","Bank":"","G8BookNo":"27635","G8ReceiptNo":"10","PaymentDate":"07/04/18","PropertyType":"Residential","BuildingCategory":"Residential Houses","Session":"2018-2019","Remarks":"no","uuid":"23fdbf04-4828-4764-b59a-b39314bc4bbe","previous_returnid":None,"status":"STAGE1","tenantid":None,"batchname":None,"new_propertyid":None,"new_locality_code":"JALLC340"},
{"SrNo":"13","ReturnId":"619","AcknowledgementNo":"ACK-131677225074654318","EntryDate":"09/04/18","Zone":"JALANDHAR","Sector":"1","Colony":"Greater Kailash Nagar","HouseNo":"556-57","Owner":"MOHINDER PAL SINGH / BELWANT SINGH / 9815904950","Floor":"Ground Floor / 3150.00 / Residential / Self Occupied / Pucca / 1750.001st Floor / 1494.00 / Residential / Self Occupied / Pucca / 415.00","ResidentialRate":"0","CommercialRate":"0","ExemptionCategory":"Non-Exempted","LandUsedType":"Others","Usage":"Built Up","PlotArea":"350","TotalCoveredArea":"4644","GrossTax":"2165","FireCharges":"0","InterestAmt":"0","Penalty":"0","Rebate":"217","ExemptionAmt":"0","TaxAmt":"1948","AmountPaid":"1948","PaymentMode":"Cash","TransactionID":"","Bank":"","G8BookNo":"26867","G8ReceiptNo":"31","PaymentDate":"09/04/18","PropertyType":"Residential","BuildingCategory":"Residential Houses","Session":"2018-2019","Remarks":"","uuid":"76026ed2-a4cf-40a8-8b92-fc788142fe25","previous_returnid":None,"status":"STAGE1","tenantid":None,"batchname":None,"new_propertyid":None,"new_locality_code":"JALLC149"}
]
# print(parse_owners_information(""))
# data = [
# "EXPORT CREDITGUARANTEE CORPORATION OF INDIA LTD. / N.A. / N/A",
# ]

udata = set()
count = 0

from csv import writer

converters = {
    ""
}

p = IkonProperty()
p.process_record(data[0])

# print(json.dumps(data[0], indent=2))
# dfs = read_html("/Users/tarunlalwani/Downloads/PTAX data 2017-18/2.xls")

# print(dfs)

# with open("floors.csv", mode="w") as f:
#     c = writer(f)
#     # c.writerow(['Name', 'FatherOrHusbandName', 'MobileNumber'])
#     headers = list(map(str.strip, "Floor / Covered Area / Usage / Occupancy / Structural Factor / Tax Amt".split("/")))
#     c.writerow(headers)
#
#     for d in data:
#         output = parse_flat_information(d)
#         # if len(output) > 1:
#         added = False
#         for o in output:
#             c.writerow(o)
#         #     if len(o[-1]) != 10 or o[-1] == "1111111111" or o[-1] == "9999999999":
#         #         udata.add(o[-1])
#         #         added = True
#         # if added:
#         #     print(o)
#         #     count = count + 1
#     # print(json.dumps(list(udata), indent=2))
#
# # print(count, len(data), "{}".format(count/len(data)))
