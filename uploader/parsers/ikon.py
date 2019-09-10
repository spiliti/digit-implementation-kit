import re

from uploader.PropertyTax import *

from uploader.parsers.utils import *

owner_pattern = re.compile("(?<![DSNMW])/(?![OSA])", re.I)


class IkonProperty(Property):

    def __init__(self, *args, **kwargs):
        super(IkonProperty, self).__init__()
        self.additional_details = {}
        self.property_details = [PropertyDetail(owners=[], additional_details={
            "inflammable": False,
            "heightAbove36Feet": False
        })]

    def process_additional_details(self, context):
        self.old_property_id = "RID{}".format(context["returnid"])
        self.additional_details = {
            "legacyInfo": {
                "returnid": context["returnid"],
                "session": context["session"],
                "taxamt": context["taxamt"],
                "acknowledgementno": context["acknowledgementno"],
                "colony": context["colony"],
                "sector": context["sector"],
                "exemptioncategory": context["exemptioncategory"],
                "totalcoveredarea": context["totalcoveredarea"],
                "grosstax": context["grosstax"],
                "amountpaid": context["amountpaid"]
            }
        }

    def process_usage(self, context):
        pd = self.property_details[0]
        if context["usage"] == "Vacant Plot":
            pd.property_type = "VACANT"
            pd.no_of_floors = 1
        else:
            pd.property_type = "BUILTUP"

    def process_address(self, context, city):
        locality = Locality(code=context["new_locality_code"])
        self.address = Address(city=city, door_no=context["houseno"], locality=locality)

        if len(self.address.door_no) > 64:
            self.address.door_no = self.address.door_no[:64]
            self.additional_details["legacyInfo"]["houseno"] = context["houseno"]

    def process_owner_information(self, context=None):
        owners = context["owner"]

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
                self.property_details[0].citizen_info = CitizenInfo(name=
                                                                    name, mobile_number=mobile)

    def process_floor_information(self, context):
        floors = context["floor"].strip()
        pd: PropertyDetail = self.property_details[0]
        pd.units = []

        if floors == 'Â' or floors == '' or floors is None:
            pd.property_type = "VACANT"
            pd.no_of_floors = 1
            pd.land_area = context["plotarea"]
        else:

            floor_set = set()

            building_category = context["buildingcategory"]

            for floor, covered_area, usage, occupancy, _, tax in parse_flat_information(context["floor"]):
                unit = Unit(floor_no=get_floor_number(floor),
                            occupancy_type=OC_MAP[occupancy],
                            unit_area=float(covered_area) / 9)

                if OC_MAP[occupancy] == "RENTED":
                    unit.arv = float(tax) * (100 / 7.5)

                    if unit.arv == 0:
                        unit.arv = None
                        unit.occupancy_type = "UNOCCUPIED"

                floor_set.add(get_floor_number(floor))

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

            if len(floor_set) == 1 and "0" not in floor_set:
                pd.property_sub_type = "SHAREDPROPERTY"
                pd.no_of_floors = 2
                pd.build_up_area = context["plotarea"]
            else:
                pd.property_sub_type = "INDEPENDENTPROPERTY"
                pd.land_area = context["plotarea"]

    def process_record(self, context, tenantid, city, financial_year="2019-20"):
        # func = BC_MAP[context["BuildingCategory"]]
        # if func:
        #     func(self, context)
        # else:
        #     raise Exception("No Mapping function")
        financial_year = context["session"].replace("-20", "-")
        self.process_owner_information(context)
        self.process_exemption(context)
        self.process_property_type(context)
        self.process_additional_details(context)
        self.process_address(context, city)
        self.property_details[0].financial_year = financial_year
        self.process_ownershiptype(context)
        self.process_usage(context)
        self.process_floor_information(context)
        self.correct_mobile_number(context)
        self.correct_data_specific_issue(context)
        self.tenant_id = tenantid
        pass

    def process_property_type(self, context):
        property_type = context['propertytype']

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
        land_type = context["landusedtype"]

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
            "--select--": "NONE",
            "Person, who had served, or are serving, in any rank, whether as a combatant or a non-combatant, in the Naval, Military or Air Forces of the Union of India": "DEFENSE",
            "Joint Owners - Both/All Widows": "WIDOW",
            "Handicapped": "HANDICAPPED",
            "Freedom Fighters": "FREEDOMFIGHTER",
            "BPL": "BPL"
        }

        ecat = context["exemptioncategory"]

        if ecat == "Joint Owners - Both/All Widows":
            for owner in self.property_details[0].owners:
                owner.owner_type = "WIDOW"
        else:
            self.property_details[0].owners[0].owner_type = EC_MAP[ecat]

    def correct_mobile_number(self, context):
        pd = self.property_details[0]

        pattern = re.compile("[^a-zA-Z0-9 \-'`\.]")

        for owner in pd.owners:
            if len(owner.mobile_number) != 10 or \
                    owner.mobile_number == "0000000000" or \
                    owner.mobile_number == "1111111111" or owner.mobile_number[:1] not in ["6", "7", "8", "9"]:
                owner.mobile_number = "9999999999"
            owner.name = pattern.sub("-", owner.name)
            owner.father_or_husband_name = pattern.sub("-", owner.father_or_husband_name)
        ci = pd.citizen_info

        if len(ci.mobile_number) != 10 \
                or ci.mobile_number == "0000000000" \
                or ci.mobile_number == "1111111111" \
                or ci.mobile_number[:1] not in ["6", "7", "8", "9"]:
            ci.mobile_number = "9999999999"

        ci.name = pattern.sub("-", ci.name)

    def correct_data_specific_issue(self, context):
        pd = self.property_details[0]
        if len(pd.units) > 0:
            pd.property_type = "BUILTUP"

            unique_property_type = set([unit.usage_category_major for unit in pd.units])

            if len(pd.property_type) == 1:
                pd.usage_category_major = unique_property_type[0]

            elif len(pd.property_type) > 1:
                pd.usage_category_major = "MIXED"

            for unit in pd.units:
                if not unit.floor_no:
                    unit.floor_no = "0"


OC_MAP = {
    "Self Occupied": "SELFOCCUPIED",
    "Un-Productive": "UNOCCUPIED",
    "Rented": "RENTED",
    "Vacant AreaLand": "UNOCCUPIED"
}

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
    floors = []
    while "/" in info[-1]:
        last_element = info[-1].strip().strip("/").strip()

        # get the phone number
        split_index = last_element.find(".") + 3
        info[-1] = last_element[:split_index]
        floors.append(info)
        remaining = last_element[split_index:].strip().strip("/").strip()
        if remaining:
            info = list(map(str.strip, owner_pattern.split(remaining, 5)))
        else:
            info = None
            break

    if info and len(info) == 6:
        floors.append(info)

    return floors
