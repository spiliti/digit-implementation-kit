import json

import os
import xlwt
from xlwt import Worksheet
from config import config


def download_boundary(tenant, boundary_type):
    # url = "https://raw.githubusercontent.com/egovernments/punjab-mdms-data/master/data/{}/egov-location/boundary-data.json".replace(
    #     "{}", tenant.replace(".", "/"))
    wk = xlwt.Workbook()
    zone: Worksheet = wk.add_sheet("Revenue Zone")
    ward: Worksheet = wk.add_sheet("Revenue Block or Ward")
    locality: Worksheet = wk.add_sheet("Locality")
    for i, col in enumerate(["S.No", "Rev Zone Code*", "Rev Zone Name*", "tenant"]):
        zone.write(0, i, col)

    for i, col in enumerate(["S.No", "Rev Block/Ward Code*", "Rev Block/Ward Name*", "Rev Zone Name*", "tenant"]):
        ward.write(0, i, col)

    for i, col in enumerate(
            ["S.No", "Locality Code*", "Locality Name*", "Rev Block/Ward Name", "Area Name (Area 1, 2 or 3)",
             "tenant"]):
        locality.write(0, i, col)

    row_zone = 1
    row_ward = 1
    row_locality = 1

    tenants = ["pb.adampur", "pb.alawalpur", "pb.amritsar", "pb.bathinda", "pb.hoshiarpur", "pb.jagraon",
               "pb.jalandhar", "pb.khamano", "pb.ludhiana", "pb.machhiwara", "pb.makhu", "pb.moga", "pb.mohali",
               "pb.mullanpur", "pb.pathankot", "pb.patiala", "pb.phagwara", "pb.raikot", "pb.raman", "pb.sahnewal",
               "pb.samrala", "pb.sujanpur", "pb.goniana", "pb.balianwali", "pb.bhuchomandi", "pb.rampuraphul",
               "pb.maur", "pb.kotfatta", "pb.talwandisabo", "pb.bariwala", "pb.sardulgarh", "pb.sangatmandi",
               "pb.gidderbaha", "pb.bhagtabhai", "pb.bhairoopa", "pb.boha", "pb.chaunke", "pb.kotshamir",
               "pb.lehramohabbat", "pb.maluka", "pb.bhogpur", "pb.shahkot", "pb.mehraj", "pb.balachaur", "pb.kartarpur",
               "pb.hariana", "pb.mahilpur", "pb.mehatpur", "pb.mukerian", "pb.urmartanda", "pb.garhshankar",
               "pb.dasuya", "pb.kotissekhan", "pb.nathana", "pb.garhdiwala", "pb.shamchurasi", "pb.mudki", "pb.mamdot",
               "pb.jalalabad", "pb.nabha", "pb.cheema", "pb.nihalsinghwala", "pb.gurdaspur", "pb.fatehgarhpanjtoor",
               "pb.joga", "pb.kothaguru", "pb.baghapurana", "pb.fazilka", "pb.guruharsahai", "pb.faridkot", "pb.patran",
               "pb.arniwala", "pb.ghanaur", "pb.banur", "pb.abohar", "pb.kurali", "pb.amargarh", "pb.quadian",
               "pb.banga", "pb.khanauri", "pb.samana", "pb.tapa", "pb.moonak", "pb.derabassi", "pb.zirakpur",
               "pb.handiaya", "pb.maloud", "pb.dhanaula", "pb.ghagga", "pb.jaitu", "pb.longowal", "pb.chamkaursahib",
               "pb.lalru", "pb.nayagaon", "pb.sangrur", "pb.lohiankhas", "pb.bhadaur", "pb.begowal", "pb.zira",
               "pb.bhulath", "pb.kapurthala", "pb.goraya", "pb.nadala", "pb.nakodar", "pb.nurmahal", "pb.phillaur",
               "pb.sultanpurlodhi", "pb.dhilwan", "pb.talwara", "pb.ahmedgarh", "pb.rahon", "pb.bhawanigarh",
               "pb.barnala", "pb.bassipathana", "pb.kharar", "pb.srihargobindpur", "pb.rampura", "pb.dinanagar",
               "pb.badhnikalan", "pb.bareta", "pb.bhikhi", "pb.budhlada", "pb.kiratpur", "pb.mallanwala",
               "pb.mandikalan", "pb.patti", "pb.rayya", "pb.nangal", "pb.malout", "pb.derababananak",
               "pb.fatehgarhchurian", "pb.ajnala", "pb.khanna", "pb.kotkapura", "pb.muktsar", "pb.sanaur",
               "pb.tarntaran", "pb.lehragaga", "pb.payal", "pb.morinda", "pb.ropar", "pb.dirba", "pb.bhikhiwind",
               "pb.jandialaguru", "pb.anandpursahib", "pb.batala", "pb.dhariwal", "pb.khemkaran", "pb.nawanshahr",
               "pb.ramdass", "pb.sirhind", "pb.bhadson", "pb.mandigobindgarh", "pb.amloh", "pb.dhuri", "pb.doraha",
               "pb.malerkotla", "pb.bilga", "pb.majitha", "pb.narotjaimalsingh", "pb.ferozepur", "pb.rajpura",
               "pb.dharamkot", "pb.mansa", "pb.sunam", "pb.rajasansi", "pb.talwandibhai"]
    for t in tenants:
        boundary_path = config.MDMS_LOCATION / t.split(".")[-1] / "egov-location" / "boundary-data.json"
        print("processing ",t, " from ",boundary_path)
        if not os.path.isfile(boundary_path):
            print(boundary_path)
            print("No boundary data exists for tenantId \"{}\", not downloading".format(tenant.upper()))
            continue



    # response = requests.get(url)
    #
    # boundary = response.json()['TenantBoundary']

        with open(boundary_path) as f:
            boundary = json.load(f)['TenantBoundary']

        if boundary[0]["hierarchyType"]["code"] == boundary_type:
            boundary_data = boundary[0]["boundary"]
        elif len(boundary) > 1:
            boundary_data = boundary[1]["boundary"]
        else:
            print("boundary path error, skipping")
            continue


        for l1 in boundary_data["children"]:
            zone.write(row_zone, 0, row_zone)
            zone.write(row_zone, 1, l1['code'])
            zone.write(row_zone, 2, l1['name'])
            zone.write(row_zone,3,t)
            row_zone += 1

            for l2 in l1["children"]:
                ward.write(row_ward, 0, row_ward)
                ward.write(row_ward, 1, l2['code'])
                ward.write(row_ward, 2, l2['name'])
                ward.write(row_ward, 3, l1['name'])
                ward.write(row_ward, 4, t)
                row_ward += 1

                for value in l2["children"]:
                    name = value['name'].split(" - ")
                    if len(name) >= 3:
                        name = name[0:-2]
                    name = " - ".join(name)

                    locality.write(row_locality, 0, row_locality)
                    locality.write(row_locality, 1, value['code'])
                    locality.write(row_locality, 2, name)
                    locality.write(row_locality, 3, l2['code'])
                    locality.write(row_locality, 4, value['area'])
                    locality.write(row_locality,5,t)
                    row_locality += 1
                # print(value['name'] + "," + value['code'])
    file_name =  "all_rev_boundary.xls"
    dir_name = "boundary_download/"
    wk.save(dir_name+file_name)
    print("\n", "XLSX file created with file name : {}".format(tenant) + "_rev_boundary.xls")


if __name__ == "__main__":
    #tenants=["pb.adampur","pb.alawalpur","pb.amritsar","pb.bathinda","pb.hoshiarpur","pb.jagraon","pb.jalandhar","pb.khamano","pb.ludhiana","pb.machhiwara","pb.makhu","pb.moga","pb.mohali","pb.mullanpur","pb.pathankot","pb.patiala","pb.phagwara","pb.raikot","pb.raman","pb.sahnewal","pb.samrala","pb.sujanpur","pb.goniana","pb.balianwali","pb.bhuchomandi","pb.rampuraphul","pb.maur","pb.kotfatta","pb.talwandisabo","pb.bariwala","pb.sardulgarh","pb.sangatmandi","pb.gidderbaha","pb.bhagtabhai","pb.bhairoopa","pb.boha","pb.chaunke","pb.kotshamir","pb.lehramohabbat","pb.maluka","pb.bhogpur","pb.shahkot","pb.mehraj","pb.balachaur","pb.kartarpur","pb.hariana","pb.mahilpur","pb.mehatpur","pb.mukerian","pb.urmartanda","pb.garhshankar","pb.dasuya","pb.kotissekhan","pb.nathana","pb.garhdiwala","pb.shamchurasi","pb.mudki","pb.mamdot","pb.jalalabad","pb.nabha","pb.cheema","pb.nihalsinghwala","pb.gurdaspur","pb.fatehgarhpanjtoor","pb.joga","pb.kothaguru","pb.baghapurana","pb.fazilka","pb.guruharsahai","pb.faridkot","pb.patran","pb.arniwala","pb.ghanaur","pb.banur","pb.abohar","pb.kurali","pb.amargarh","pb.quadian","pb.banga","pb.khanauri","pb.samana","pb.tapa","pb.moonak","pb.derabassi","pb.zirakpur","pb.handiaya","pb.maloud","pb.dhanaula","pb.ghagga","pb.jaitu","pb.longowal","pb.chamkaursahib","pb.lalru","pb.nayagaon","pb.sangrur","pb.lohiankhas","pb.bhadaur","pb.begowal","pb.zira","pb.bhulath","pb.kapurthala","pb.goraya","pb.nadala","pb.nakodar","pb.nurmahal","pb.phillaur","pb.sultanpurlodhi","pb.dhilwan","pb.talwara","pb.ahmedgarh","pb.rahon","pb.bhawanigarh","pb.barnala","pb.bassipathana","pb.kharar","pb.srihargobindpur","pb.rampura","pb.dinanagar","pb.badhnikalan","pb.bareta","pb.bhikhi","pb.budhlada","pb.kiratpur","pb.mallanwala","pb.mandikalan","pb.patti","pb.rayya","pb.nangal","pb.malout","pb.derababananak","pb.fatehgarhchurian","pb.ajnala","pb.khanna","pb.kotkapura","pb.muktsar","pb.sanaur","pb.tarntaran","pb.lehragaga","pb.payal","pb.morinda","pb.ropar","pb.dirba","pb.bhikhiwind","pb.jandialaguru","pb.anandpursahib","pb.batala","pb.dhariwal","pb.khemkaran","pb.nawanshahr","pb.ramdass","pb.sirhind","pb.bhadson","pb.mandigobindgarh","pb.amloh","pb.dhuri","pb.doraha","pb.malerkotla","pb.bilga","pb.majitha","pb.narotjaimalsingh","pb.ferozepur","pb.rajpura","pb.dharamkot","pb.mansa","pb.sunam","pb.rajasansi","pb.talwandibhai"]
    #for t in tenants:
    #    download_boundary(t, "REVENUE")
    download_boundary(config.TENANT_ID, "REVENUE")



