import re

from uploader.PropertyTaxV2 import *

from uploader.parsers.utils import *

owner_pattern = re.compile("(?<![DSNMW])/(?![OSA])", re.I)


class IkonPropertyV2(Property):

    def __init__(self, *args, **kwargs):
        super(IkonPropertyV2, self).__init__()
        self.owners = []
        #self.additional_details = {}
        #self.property_details = [PropertyDetail(owners=[], additional_details={
        #    "inflammable": False,
        #    "heightAbove36Feet": False
        #})]

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
                "amountpaid": context["amountpaid"],
                "businessname": context["businessname"],
                "waterconnectionno": context["waterconnectionno"],
                "electricityconnectionno": context["electrictyconnectionno"],
                "photo_id": context["photoid"]

            }
        }

    def process_usage(self, context):
        #pd = self.property_details[0]
        if context["usage"] == "Vacant Plot":
            self.property_type = "VACANT"
            self.no_of_floors = 1
        else:
            self.property_type = "BUILTUP"

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

            self.owners.append(owner)
            #print("owner processed ..")

            #if self.property_details[0].citizen_info is None:
            #    self.property_details[0].citizen_info = CitizenInfo(name=
            #                                                        name, mobile_number=mobile)

    def process_floor_information(self, context):
        self.build_up_area = context["totalcoveredarea"]
        floors = context["floor"].strip()
        #pd: PropertyDetail = self.property_details[0]
        self.units = []

        if floors == 'Â' or floors == '' or floors is None:
            self.property_type = "VACANT"
            self.no_of_floors = 1
            self.land_area = context["plotarea"]
        else:
            self.property_type = "BUILTUP"
            floor_set = set()

            building_category = context["buildingcategory"]

            for floor, covered_area, usage, occupancy, _, tax in parse_flat_information(context["floor"]):
                if "- VACANT" in floor.upper():
                    continue   # to skip any vacant area on floor (Basicaly ...Ground Floor - Vacant... floors are not to be added and assumed to be calculated automaticaly)
                construction_detail=ConstructionDetail(built_up_area=float(covered_area) / 9)
                unit = Unit(floor_no=get_floor_number(floor),
                            occupancy_type=OC_MAP[occupancy],
                            construction_detail=construction_detail)

                if OC_MAP[occupancy] == "RENTED":
                    unit.arv = round(float(tax) * (100 / 7.5), 2)

                    if unit.arv == 0:
                        unit.arv = None
                        unit.occupancy_type = "UNOCCUPIED"

                floor_set.add(get_floor_number(floor))

                if usage == "Residential" or usage.strip() == 'Residential Houses' or usage.strip() == "Flats" or usage.strip() == "Flat":
                    unit.usage_category_major = "RESIDENTIAL"
                    unit.usage_category="RESIDENTIAL"
                else:
                    unit.usage_category_major = "NONRESIDENTIAL"
                    unit.usage_category="NONRESIDENTIAL"

                    if building_category in BD_UNIT_MAP:
                        unit.usage_category_minor, unit.usage_category_sub_minor, unit.usage_category_detail = \
                            BD_UNIT_MAP[building_category]
                    else:
                        unit.usage_category_minor = "COMMERCIAL"
                        unit.usage_category_sub_minor = "OTHERCOMMERCIALSUBMINOR"
                        unit.usage_category_detail = "OTHERCOMMERCIAL"

                #according to V2 usageCategory has Dot (.) seperated usage categories
                unit.usage_category = unit.usage_category_major
                if unit.usage_category_minor is not None:
                    unit.usage_category = unit.usage_category +"."+unit.usage_category_minor
                if unit.usage_category_sub_minor is not None:
                    unit.usage_category = unit.usage_category + "." + unit.usage_category_sub_minor
                if unit.usage_category_detail is not None:
                    unit.usage_category = unit.usage_category + "." + unit.usage_category_detail

                self.units.append(unit)

            self.no_of_floors = len(floor_set)

            if len(floor_set) == 1 and "0" not in floor_set:
                self.property_sub_type = "SHAREDPROPERTY"
                self.property_type=self.property_type+"."+self.property_sub_type
                self.no_of_floors = 2
                self.build_up_area = context["plotarea"]
                self.land_area = context["plotarea"]    # added and this line was not in V1, land_area was giving error for None type
            else:
                self.property_sub_type = "INDEPENDENTPROPERTY"
                self.property_type = self.property_type + "." + self.property_sub_type
                self.land_area = context["plotarea"]

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
        self.process_address(context, city) # in locality, only localitycode is assigned but area attribute is null yet
        #self.property_details[0].financial_year = financial_year  #propertyDetails was in V1
        self.process_ownershiptype(context)
        self.process_usage(context)   #propertyType VACANT OR BUILTUP
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
        self.usage_category_minor = "None"
        self.usage_category_minor = None
        self.usage_category_major = PT_MAP[property_type]
        self.usage_category = PT_MAP[property_type]

    def process_ownershiptype(self, context):
        #pd = self.property_details[0]
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

        #pd.ownership_category = "INDIVIDUAL"
        self.ownership_category = "INDIVIDUAL"

        if len(self.owners) > 1:
            self.sub_ownership_category = "MULTIPLEOWNERS"
            self.ownership_category=self.ownership_category + "." + self.sub_ownership_category  # For v2 properties
        else:
            if land_type in ONC_MAP:
                self.ownership_category = ONC_MAP[land_type][0]
                self.sub_ownership_category = ONC_MAP[land_type][1]
                self.ownership_category = self.ownership_category + "." + self.sub_ownership_category  # for v2 properties

                self.institution = Institution("UNKNOWN", self.sub_ownership_category, "UNKNOWN")
                for o in self.owners:
                    o.designation = "Designation"
                    o.alt_contact_number = "91234567890"
            else:
                self.sub_ownership_category = "SINGLEOWNER"
                self.ownership_category = self.ownership_category + "." + self.sub_ownership_category  # for v2 properties

    def process_exemption(self, context):
        EC_MAP = {
            "Widows": "WIDOW",
            "Non-Exempted": "NONE",
            "--select--": "NONE",
            "Person, who had served, or are serving, in any rank, whether as a combatant or a non-combatant, in the Naval, Military or Air Forces of the Union of India": "DEFENSE",
            "Joint Owners - Both/All Widows": "WIDOW",
            "Handicapped": "HANDICAPPED",
            "Freedom Fighters": "FREEDOMFIGHTER",
            "BPL": "BPL",
            "Non Govt. Aided Education Organizations": "NONE",
            "Registered charitable and philanthropic organizations": "CHARITABLETRUST",
            "Religious activities, religious ceremonies": "RELIGIOUSINSTITUTION"
        }

        ecat = context["exemptioncategory"]

        if ecat == "Joint Owners - Both/All Widows":
            for owner in self.owners:
                owner.owner_type = "WIDOW"
                d=Document("12345","DEATHCERTIFICATE")
                owner.documents = []
                owner.documents.append(d)
        else:
            self.owners[0].owner_type = EC_MAP[ecat]
            if self.owners[0].owner_type == "WIDOW":
                d = Document("12345", "DEATHCERTIFICATE")
                self.owners[0].documents = []
                self.owners[0].documents.append(d)
            elif self.owners[0].owner_type == "HANDICAPPED":
                d = Document("44444","HANDICAPCERTIFICATE")
                self.owners[0].documents = []
                self.owners[0].documents.append(d)
            elif self.owners[0].owner_type == "FREEDOMFIGHTER":
                d = Document("44444","COMPETENTAUTHORITY")
                self.owners[0].documents = []
                self.owners[0].documents.append(d)


    def correct_mobile_number(self, context):
        #pd = self.property_details[0]

        pattern = re.compile("[^a-zA-Z0-9 \-'`\.]")

        for owner in self.owners:
            if len(owner.mobile_number) != 10 or \
                    owner.mobile_number == "0000000000" or \
                    owner.mobile_number == "1111111111" or owner.mobile_number[:1] not in ["6", "7", "8", "9"]:
                owner.mobile_number = "9999999999"
            owner.name = pattern.sub("-", owner.name)
            owner.father_or_husband_name = pattern.sub("-", owner.father_or_husband_name)
        #ci = pd.citizen_info   #citizen_info was in V1

        #if len(ci.mobile_number) != 10 \
        #        or ci.mobile_number == "0000000000" \
        #        or ci.mobile_number == "1111111111" \
        #        or ci.mobile_number[:1] not in ["6", "7", "8", "9"]:
        #    ci.mobile_number = "9999999999"

        #ci.name = pattern.sub("-", ci.name)

    def correct_data_specific_issue(self, context):
        #pd = self.property_details[0]

        if len(self.units) > 0 and self.property_type is None:
            self.property_type = "BUILTUP"

            #unique_property_type = set([unit.usage_category_major for unit in pd.units])
            distinct_unit_usage_type = set([unit.usage_category_major for unit in self.units])



            #if len(pd.property_type) == 1:
            if len(distinct_unit_usage_type) == 1:
                self.usage_category_major = list(distinct_unit_usage_type)[0]

            #elif len(pd.property_type) > 1:
            elif len(distinct_unit_usage_type) > 1:
                self.usage_category_major = "MIXED"

            for unit in self.units:
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
    # Institutional Building,Community Hall,Social Clubs,Sports stadiums,Bus Stand, and Such like Building
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

        remaining =  last_element[split_index:].strip().strip("/").strip() # may be floor number is null
        #check whether above variable 'remaining' is having first element as floorNumber if no then add empty floor number (because in mohali data floor number may not be there)
        if remaining:
            try:
                first=(remaining.split("/"),1)[0]
                float(first[0])
                #means first element is float then we have to add empty floor number to complete floor set
                remaining = " / " + remaining
            except ValueError:
                print("floor number ok")
                #if value is not a float then its ok that first element is floor number

        if remaining:
            info = list(map(str.strip, owner_pattern.split(remaining, 5)))
        else:
            info = None
            break

    if info and len(info) == 6:
        floors.append(info)

    return floors
