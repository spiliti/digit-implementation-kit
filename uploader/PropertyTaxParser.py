import json
from urllib.parse import urlparse, urljoin

import requests

from config import config

from common import open_excel_file, superuser_login
from uploader.PropertyTax import RequestInfo, Property, PropertyDetail, Owner, CitizenInfo, Unit, \
    Address, Locality, Institution, PropertyCreateRequest
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


class PropertyEncoder(JSONEncoder):
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
            new_d[convert(k)] = convert_json(v, convert) if isinstance(v, dict) else v
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


BD_UNIT_MAP = {
    "Residential Houses": (None, None, None),
    # "Government buildings, including buildings of Government Undertakings, Board or Corporation": "",
    "Industrial (any manufacturing unit), educational institutions, and godowns": (
    "INDUSTRIAL", "OTHERINDUSTRIALSUBMINOR", "OTHERINDUSTRIAL"),
    "Commercial buildings including Restaurants (except multiplexes, malls, marriage palaces)": (
    "COMMERCIAL", "OTHERCOMMERCIALSUBMINOR", "OTHERCOMMERCIAL"),
    "Flats": (""),
    "Hotels - Having beyond 50 rooms": ("COMMERCIAL", "HOTELS", None),
    "Others": ("COMMERCIAL", "OTHERCOMMERCIALSUBMINOR", "OTHERCOMMERCIAL"),
    # "Mix-Use Building used for multiple purposes (like Residential+Commercial+Industrial)": "",
    "Institutional buildings (other than educational institutions), including community halls/centres, sports stadiums, social clubs, bus stands, gold clubs, and such like buildings used for public purpose": (
    "INSTITUTIONAL", "OTHERINSTITUTIONALSUBMINOR", "OTHERINSTITUTIONAL"),
    "Hotels - Having 50 rooms or below": ("COMMERCIAL", "HOTELS", None),
    "Multiplex, Malls, Shopping Complex/Center etc.": ("COMMERCIAL", "RETAIL", "MALLS"),
    "Vacant Plot": (None, None, None),
    "Marriage Palaces": ("COMMERCIAL", "EVENTSPACE", "MARRIAGEPALACE")
}


# OTHERINDUSTRIAL,OTHERINDUSTRIALSUBMINOR,INDUSTRIAL,
# INSTITUTIONAL,
# OTHERS
# INDIVIDUAL, SINGLEOWNER
# INDIVIDUAL, MULTIPLEOWNERS
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

    def process_additional_details(self, context):
        self.old_property_id = "RID{}".format(context["ReturnId"])
        self.additional_details = {
            "legacyInfo": {
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

    def process_usage(self, context):
        pd = self.property_details[0]
        if context["Usage"] == "Vacant Plot":
            pd.property_type = "VACANT"
            pd.no_of_floors = 1
        else:
            pd.property_type = "BUILTUP"

    def process_address(self, context):
        locality = Locality(code=context["new_locality_code"])
        self.address = Address(city="Jalandhar", door_no=context["HouseNo"], locality=locality)

    def process_owner_information(self, context=None):
        owners = context["Owner"]

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

    def process_floor_information(self, context):
        floors = context["Floor"].strip()
        pd: PropertyDetail = self.property_details[0]
        pd.units = []

        if floors == 'Â' or floors == '':
            pd.property_type = "VACANT"
            pd.land_area = context["PlotArea"]
        else:

            floor_set = set()

            building_category = context["BuildingCategory"]

            for floor, covered_area, usage, occupancy, _, tax in parse_flat_information(context["Floor"]):
                unit = Unit(floor_no=FLOOR_MAP[floor],
                            occupancy_type=OC_MAP[occupancy],
                            unit_area=float(covered_area) / 9)

                if OC_MAP[occupancy] == "RENTED":
                    unit.arv = float(tax) * (100 / 7.5)
                floor_set.add(FLOOR_MAP[floor])

                if usage == "Residential":
                    unit.usage_category_major = "RESIDENTIAL"
                else:
                    unit.usage_category_major = "NONRESIDENTIAL"

                    if building_category in BD_UNIT_MAP:
                        unit.usage_category_minor, unit.usage_category_sub_minor, unit.usage_category_detail = \
                        BD_UNIT_MAP[building_category]
                    else:
                        unit.usage_category_minor = "COMMERCIAL"
                        unit.usage_category_sub_minor = "OTHERCOMMERCIALSUBMINOR"
                        unit.usage_category_detail = "OTHERCOMMERCIAL"
                pd.units.append(unit)

            pd.no_of_floors = len(floor_set)

            if len(pd.units) == 1 and "0" not in floor_set:
                pd.property_sub_type = "SHAREDPROPERTY"
                pd.no_of_floors = 2
                pd.build_up_area = context["PlotArea"]
            else:
                pd.property_sub_type = "INDEPENDENTPROPERTY"
                pd.land_area = context["PlotArea"]

    def process_record(self, context, tenantid, financial_year="2019-20"):
        # func = BC_MAP[context["BuildingCategory"]]
        # if func:
        #     func(self, context)
        # else:
        #     raise Exception("No Mapping function")

        self.process_owner_information(context)
        self.process_exemption(context)
        self.process_property_type(context)
        self.process_address(context)
        self.property_details[0].financial_year = financial_year
        self.process_ownershiptype(context)
        self.process_additional_details(context)
        self.process_usage(context)
        self.process_floor_information(context)
        self.correct_mobile_number(context)
        self.tenant_id = tenantid
        pass

    def get_property_json(self):
        property_encoder = PropertyEncoder().encode(self)
        return convert_json(json.loads(property_encoder), underscore_to_camel)

    def process_property_type(self, context):
        property_type = context['PropertyType']

        PT_MAP = {
            "Mix-Use": "MIXED",
            "Residential": "RESIDENTIAL",
            "0": "RESIDENTIAL",
            "Industrial": "NONRESIDENTIAL",
            "Non-Residential": "NONRESIDENTIAL"
        }

        self.property_details[0].usage_category_major = PT_MAP[property_type]

    def process_ownershiptype(self, context):
        pd = self.property_details[0]
        land_type = context["LandUsedType"]

        ONC_MAP = {
            "The building and land of Hospitals or Dispensaries owned by the State Government": (
                "INSTITUTIONALGOVERNMENT", "STATEGOVERNMENT"),
            "The building and land owned and used by the Corporation": ("INSTITUTIONALPRIVATE", "PRIVATECOMPANY"),
            "The building and land used for Schools and Colleges owned or aided by the State Government": (
                "INSTITUTIONALGOVERNMENT", "STATEGOVERNMENT")
        }

        # INSTITUTIONALPRIVATE, PRIVATECOMPANY
        # INSTITUTIONALPRIVATE, NGO
        # INSTITUTIONALPRIVATE, PRIVATETRUST
        # INSTITUTIONALPRIVATE, PRIVATEBOARD
        # OTHERSPRIVATEINSTITUITION,
        #
        # INSTITUTIONALGOVERNMENT, STATEGOVERNMENT
        # OTHERGOVERNMENTINSTITUITION
        # CENTRALGOVERNMENT

        pd.ownership_category = "INDIVIDUAL"

        if len(pd.owners) > 1:
            pd.sub_ownership_category = "MULTIPLEOWNERS"
        else:
            if land_type in ONC_MAP:
                pd.ownership_category = ONC_MAP[land_type][0]
                pd.sub_ownership_category = ONC_MAP[land_type][1]

                pd.institution = Institution("UNKNOWN", pd.sub_ownership_category, "UNKNOWN")
                for o in pd.owners:
                    o.designation = "Designation"
                    o.alt_contact_number = "91234567890"

            else:
                pd.sub_ownership_category = "SINGLEOWNER"

    def process_exemption(self, context):
        EC_MAP = {
            "Widows": "WIDOW",
            "Non-Exempted": "NONE",
            "Person, who had served, or are serving, in any rank, whether as a combatant or a non-combatant, in the Naval, Military or Air Forces of the Union of India": "DEFENSE",
            "Joint Owners - Both/All Widows": "WIDOW",
            "Handicapped": "HANDICAPPED",
            "Freedom Fighters": "FREEDOMFIGHTER",
            "BPL": "BPL"
        }

        ecat = context["ExemptionCategory"]

        if ecat == "Joint Owners - Both/All Widows":
            for owner in self.property_details[0].owners:
                owner.owner_type = "WIDOW"
        else:
            self.property_details[0].owners[0].owner_type = EC_MAP[ecat]

    def upload_property(self, access_token):
        request_data = {
            "RequestInfo": {
                "authToken": access_token
            },
            "Properties": [
                self.get_property_json()
            ]
        }
        print(json.dumps(request_data, indent=2))
        response = requests.post(
            urljoin(config.HOST, "/pt-services-v2/property/_create?tenantId=pb.testing"),
            json=request_data)

        res = response.json()

        return request_data, res

    def correct_mobile_number(self, context):
        pd = self.property_details[0]

        pattern = re.compile("[^a-zA-Z0-9 \-'`\.]")

        for owner in pd.owners:
            if len(owner.mobile_number) != 10 or \
                    owner.mobile_number == "0000000000" or \
                    owner.mobile_number == "1111111111" or owner.mobile_number[:1] not in ["6", "7", "8", "9"]:
                owner.mobile_number = "9999999999"
            owner.name = pattern.sub("-", owner.name)
        ci = pd.citizen_info

        if len(ci.mobile_number) != 10 \
                or ci.mobile_number == "0000000000" \
                or ci.mobile_number == "1111111111" \
                or ci.mobile_number[:1] not in ["6", "7", "8", "9"]:
                ci.mobile_number = "9999999999"


class PropertyTaxParser():
    def create_property_object(self, auth_token):
        ri = RequestInfo(auth_token=auth_token)

        property = IkonProperty()
        PropertyCreateRequest(ri, [property])


owner_pattern = re.compile("(?<![DSNW])/(?![OA])", re.I)


def parse_owners_information(text):
    # text = text or """ASHOK KUMAR / ACHHRU RAM / 9779541015JEET KUMARI / W/O ASHOK KUMAR / 9779541015"""

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
    # text = text or """Ground Floor / 1100.00 / Residential / Self Occupied / Pucca / 939.58Ground Floor - Vacant In Use / 250.00 / Residential / Self Occupied / Pucca / 185.421st Floor / 1100.00 / Residential / Self Occupied / Pucca / 613.252nd Floor / 1100.00 / Residential / Self Occupied / Pucca / 368.50"""

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

if __name__ == "__main__":
    p = IkonProperty()

    from uploader import PropertyTaxData

    start = 0
    end = 1

    access_token = superuser_login()["access_token"]
    ri = RequestInfo(auth_token=access_token)
    pc = PropertyCreateRequest(request_info=ri, properties=[None])

    for d in PropertyTaxData.data[start:]:
        start = start + 1
        print(start)
        p.process_record(d, "pb.testing")

        req, res = p.upload_property()

        break

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
