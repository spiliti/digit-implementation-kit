extra columns to demand
   (i) DocumentId in case of owner exemption
   
List of OwnerTypes
            NA
            Not Applicable
            Widow
            Defense Person
            Handicapped 

As Patiala records received contains manual enteries also for session 2018-19 or below, 
    1. therefore duplicacy is there (should be filtered)
    2. dates are in different formats like dd-mm-yy, dd/mm/yyyy, mm/dd/yy, dd-mmm-yyyy etc
       2.1 dates from online systems seems to be in format dd-mm-yy
           convert these dates to 4-digit year dd-mm-yyyy (Hint: Use VALUE() function and then format as date)
       2.2 still some of only transactions contains dd/mm/yyyy which belongs to session 2019-20 onwards
           replace them from '/' to '-' means dd/mm/yyyy to dd-mm-yyyy
    3. Check '/' in 'M/S Firm name' in owner column
    4. Check " ' " single qoute (post of es) and replace with space
    5. CLIENT_DATA_PROPERTY_ID seems to be sequatial return id, therefore this column is being copied and used as Aknwoledgement number
       assuming higher this acknowledgement number, latest is the return date
    6. update session column to 4-digit years by using formula ="20"&SUBSTITUTE(AM160,"-","-20") e.g. 2021-22 to 2021-2022
    7. Some of Government Building received as ownertype(land_used_type) "Citizen Propery", it should be updated to Government property as under
        select * from patiala_pt_legacy_data 
        --update patiala_pt_legacy_data set landusedtype='State Government Property' 
        where buildingcategory='Government building' and landusedtype='Citizen Property'
       
       
       achieving above corrections in excel:
         filtered for sessions 2019-20, 2020-21 and 2021-22 and converted 2 digit year to 4-digit year   

OWNER DETAILS column in excel to be corrected as =LEFT(L3,Len(L3)-2) to remove last '#' (Hash)
Similarly LEASE DETAIL, FLOOR_AREA_DETAIL, UNCOVERED AREA DETAIL to be corrected to remove '#' at last

updated unit map from building_categories and unit usages
BD_UNIT_MAP = {
    "Residential Houses": (None, None, None),
    "Residential House": (None, None, None),
    

    # "Government buildings, including buildings of Government Undertakings, Board or Corporation": "",
    # Institutional Building,Community Hall,Social Clubs,Sports stadiums,Bus Stand, and Such like Building
    "Industrial (any manufacturing unit), educational institutions, and godowns": (
        "INDUSTRIAL", "OTHERINDUSTRIALSUBMINOR", "OTHERINDUSTRIAL"),
    "Commercial buildings including Restaurants (except multiplexes, malls, marriage palaces)": (
        "COMMERCIAL", "OTHERCOMMERCIALSUBMINOR", "OTHERCOMMERCIAL"),
    "Commercial Buildings except Multiplexes, Malls, Marriage Palaces": ("COMMERCIAL", "OTHERCOMMERCIALSUBMINOR", "OTHERCOMMERCIAL"),
    "Commercial Buildings except Multiplexes, Malls, Marriage Palaces,Godown":("COMMERCIAL", "OTHERCOMMERCIALSUBMINOR", "OTHERCOMMERCIAL"),
    "Flats": (""),
    "Commercial Buildings except Multiplexes, Malls, Marriage Palaces,Parking space (only in respect of multi-storey flats or buildings).":(""),
    "Hotels - Having beyond 50 rooms": ("COMMERCIAL", "HOTELS", None),
    "Hotel": ("COMMERCIAL", "HOTELS", None),
    "Others": ("COMMERCIAL", "OTHERCOMMERCIALSUBMINOR", "OTHERCOMMERCIAL"),
    # "Mix-Use Building used for multiple purposes (like Residential+Commercial+Industrial)": "",
    "Institutional buildings (other than educational institutions), including community halls/centres, sports stadiums, social clubs, bus stands, gold clubs, and such like buildings used for public purpose": (
        "INSTITUTIONAL", "OTHERINSTITUTIONALSUBMINOR", "OTHERINSTITUTIONAL"),
    "Hotels - Having 50 rooms or below": ("COMMERCIAL", "HOTELS", None),
    "Multiplex, Malls, Shopping Complex/Center etc.": ("COMMERCIAL", "RETAIL", "MALLS"),
    "Vacant Plot": (None, None, None),
    "Vacant Plot(Commercial)": (None, None, None),
    "Vacant Plot(Residential)": (None, None, None),
    "Marriage Palaces": ("COMMERCIAL", "EVENTSPACE", "MARRIAGEPALACE"),
    "Petrol Pump":("COMMERCIAL", "OTHERCOMMERCIALSUBMINOR", "OTHERCOMMERCIAL"),
    "Multiplex": ("COMMERCIAL","ENTERTAINMENT","MULTIPLEX"),
    "Mall": ("COMMERCIAL","RETAIL","ESTABLISHMENTSINMALLS"),
    "Gas Godown": ("COMMERCIAL", "OTHERCOMMERCIALSUBMINOR", "OTHERCOMMERCIAL"),
    "Commercial Buildings except Multiplexes, Malls, Marriage Palaces,Residential House":("COMMERCIAL", "OTHERCOMMERCIALSUBMINOR", "OTHERCOMMERCIAL")
    
}

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


------------------------------------------------
Preparing Legacy DB Data
------------------------------------------------
CREATE TABLE patiala_pt_legacy_data (
    srno text,
    returnid text,
    acknowledgementno text,
    entrydate text,
    zone text,
    sector text,
    colony text,
    houseno text,
    owner text,
    leasedetail text,
    address text,
    floor text,
    unbuiltarea text,
    residentialrate text,
    commercialrate text,
    exemptioncategory text,
    landusedtype text,
    usage text,
    plotarea text,
    totalcoveredarea text,
    grosstax text,
    firecharges text,
    interestamt text,
    penalty text,
    rebate text,
    exemptionamt text,
    taxamt text,
    amountpaid text,
    paymentmode text,
    transactionid text,
    bank text,
    g8bookno text,
    g8receiptno text,
    paymentdate text,
    propertytype text,
    buildingcategory text,
    session text,
    remarks text,
    businessname text,
    waterconnectionno text,
    electrictyconnectionno text,
    photoid text,
    client_data_id text,
    height_above_36ft text,
        
    ----------------
    uuid text default uuid_generate_v4(),
    previous_returnid text,
    status text default 'stage1'::text,
    tenantid text,
    batchname text,
    new_propertyid text,
    upload_status text,
    upload_response text,
    new_assessmentnumber text,
    new_tax text,
    new_total text,
    req_json text,
    time_taken float8,
    new_locality_code text,
    receipt_status text,
    receipt_request text,
    receipt_response text,
    receipt_number text,
    time_taken_receipt float8,
    parent_uuid text,
    colony_processed text,
    upload_response_workflow text,
    upload_response_assessment text
);

CREATE INDEX IF NOT EXISTS idx_patiala_pt_legacy_data_uuid on patiala_pt_legacy_data(uuid);
CREATE INDEX IF NOT EXISTS idx_patiala_pt_legacy_data_puuid on patiala_pt_legacy_data(parent_uuid);
CREATE INDEX IF NOT EXISTS idx_patiala_pt_legacy_data_rno on patiala_pt_legacy_data(receipt_number);
CREATE INDEX IF NOT EXISTS idx_patiala_pt_legacy_data_rstatus on patiala_pt_legacy_data(receipt_status);
CREATE INDEX IF NOT EXISTS idx_patiala_pt_legacy_data_ustatus on patiala_pt_legacy_data(upload_status);
CREATE INDEX IF NOT EXISTS idx_patiala_pt_legacy_data_session on patiala_pt_legacy_data(session);
CREATE INDEX IF NOT EXISTS idx_patiala_pt_legacy_data_rid on patiala_pt_legacy_data(returnid);
CREATE INDEX IF NOT EXISTS idx_patiala_pt_legacy_data_prid on patiala_pt_legacy_data(previous_returnid);
CREATE INDEX IF NOT EXISTS idx_patiala_pt_legacy_data_csector on patiala_pt_legacy_data(colony, sector);
CREATE INDEX IF NOT EXISTS idx_patiala_pt_legacy_data_locality on patiala_pt_legacy_data(new_locality_code);
CREATE INDEX IF NOT EXISTS idx_patiala_pt_legacy_data_colony_processed on patiala_pt_legacy_data(colony_processed);

CREATE TABLE patiala_boundary (
    code text,
    colony text,
    sector text,
    area text,
    colony_processed text
);

CREATE INDEX IF NOT EXISTS idx_patiala_boundary_code on patiala_boundary(code);
CREATE INDEX IF NOT EXISTS idx_patiala_boundary_colony on patiala_boundary(colony);
CREATE INDEX IF NOT EXISTS idx_patiala_boundary_sector on patiala_boundary(sector);
CREATE INDEX IF NOT EXISTS idx_patiala_boundary_colony_processed on patiala_boundary(colony_processed);

-- Set the FILLFACTOR to 50% so large updates don't take time
ALTER TABLE patiala_pt_legacy_data SET (FILLFACTOR = 50);
VACUUM FULL patiala_pt_legacy_data;
REINDEX TABLE patiala_pt_legacy_data;
```


```csv
returnid,previous_returnid,acknowledgementno,entrydate,zone,sector,colony,houseno,owner,leasedetail,address,floor,unbuiltarea,exemptioncategory,landusedtype,usage,plotarea,totalcoveredarea,grosstax,firecharges,interestamt,penalty,rebate,exemptionamt,taxamt,paymentmode,transactionid,g8bookno,g8receiptno,paymentdate,propertytype,session,buildingcategory,client_data_id,height_above_36ft
```


```pgsql
COPY patiala_pt_legacy_data(returnid,previous_returnid,acknowledgementno,entrydate,zone,sector,colony,houseno,owner,leasedetail,address,floor,unbuiltarea,exemptioncategory,landusedtype,usage,plotarea,totalcoveredarea,grosstax,firecharges,interestamt,penalty,rebate,exemptionamt,taxamt,paymentmode,transactionid,g8bookno,g8receiptno,paymentdate,propertytype,session,buildingcategory,client_data_id,height_above_36ft)
FROM '/tmp/combined.csv'
WITH (format csv, QUOTE '"', header);
```


Now that the data is imported, we want to be able to identify each record using a unique identifier, so we assign a `uuid` to each record


```pgsql
update patiala_pt_legacy_data set uuid = uuid_generate_v4();

update patiala_pt_legacy_data set 
new_propertyid = NULL, upload_status = NULL, receipt_status = NULL, receipt_number = NUll, receipt_request = null, receipt_response = null, req_json = Null, parent_uuid = Null, upload_response = null;
```

--------------------------------------
patiala SPECIAL CASE
-------------------------------------------
update patiala_pt_legacy_data set upload_status='WONT_UPLOAD' where acknowledgementno::int not in 
(select max(acknowledgementno::int) as ackno from patiala_pt_legacy_data 
group by returnid
)
--------------------------------------




We also map the `uuid` to `parent_uuid` for matching the `previous_returnid` using below queries

----------------------
patiala SPECIAL CASE FOR BELOW QUERIES
-----------------------------------------------
update  patiala_pt_legacy_data as pt1  set parent_uuid = (select max(uuid) from patiala_pt_legacy_data pt2
where pt2.ReturnId = pt1.ReturnId  and Session = '2013-2014' group by pt2.ReturnId)
where Session = '2014-2015';


update  patiala_pt_legacy_data as pt1  set parent_uuid = (select max(uuid) from patiala_pt_legacy_data pt2
where pt2.ReturnId = pt1.ReturnId  and Session = '2014-2015' group by pt2.ReturnId)
where Session = '2015-2016';


update  patiala_pt_legacy_data as pt1  set parent_uuid = (select max(uuid) from patiala_pt_legacy_data pt2
where pt2.ReturnId = pt1.ReturnId  and Session = '2015-2016' group by pt2.ReturnId)
where Session = '2016-2017';

update  patiala_pt_legacy_data as pt1  set parent_uuid = (select max(uuid) from patiala_pt_legacy_data pt2
where pt2.ReturnId = pt1.ReturnId  and Session = '2016-2017' group by pt2.ReturnId)
where Session = '2017-2018';


update  patiala_pt_legacy_data as pt1  set parent_uuid = (select max(uuid) from patiala_pt_legacy_data pt2
where pt2.ReturnId = pt1.ReturnId  and Session = '2017-2018' group by pt2.ReturnId)
where Session = '2018-2019';


update  patiala_pt_legacy_data as pt1  set parent_uuid = (select max(uuid) from patiala_pt_legacy_data pt2
where pt2.ReturnId = pt1.ReturnId  and Session = '2018-2019' group by pt2.ReturnId)
where Session = '2019-2020';


update  patiala_pt_legacy_data as pt1  set parent_uuid = (select max(uuid) from patiala_pt_legacy_data pt2
where pt2.ReturnId = pt1.ReturnId  and Session = '2019-2020' group by pt2.ReturnId)
where Session = '2020-2021';


update  patiala_pt_legacy_data as pt1  set parent_uuid = (select max(uuid) from patiala_pt_legacy_data pt2
where pt2.ReturnId = pt1.ReturnId  and Session = '2020-2021' group by pt2.ReturnId)
where Session = '2021-2022';


------------------------------------
#### Mapping the colonies to RM

Make sure the boundary has a `UNKNOWN` code, so that colonies which are not mapped can be moved to `UNKNOWN` code 

Run the `revenue_boundary_gen_download.py` to download the boundary data for the given tenant.

Upload the 
`Rev Block/ward code` (sector), `Locality name` (colony),	`Locality Code` (code), `Area name` (area) fields to `bd` table

Now update the localities in DB

```PGSQL


-----------------------------------------------------------
FOUND THAT MANY COLONY IN PATIALA IS HAVING AREA1 as well as AREA2 enteries 
therefore locality table is to be altered with postfixed as MAIN with higher AREATYPE value


---------------------------------------------------------------------------------------------

patiala SPECIAL CASE
---------------------

update patiala_pt_legacy_data set colony_processed=regexp_replace(regexp_replace(trim(upper(colony)),'[^a-zA-Z0-9]+', ' ','g'),'\s+', ' ')


update patiala_boundary set colony_processed = regexp_replace(regexp_replace(trim(upper(colony)),'[^a-zA-Z0-9]+', ' ','g'),'\s+', ' ')

PATIALA SPECIAL LOCALITY CODE MATCHING
---------------------------------
1.
update patiala_pt_legacy_data as pt1 set new_locality_code = (
	select code from patiala_boundary jb where  jb.colony_processed = pt1.colony_processed and  jb.sector = pt1.sector -- and jb.area=upper(replace(pt1.zone,' ',''))
)where new_locality_code isnull;
------------

2.
update patiala_pt_legacy_data as pt1 set new_locality_code = (
	select code from patiala_boundary jb where  pt1.colony_processed=jb.colony_processed  and jb.area=upper(replace(pt1.zone,' ','')) order by area limit 1
)where new_locality_code isnull;

----------------------------
3.
update patiala_pt_legacy_data as pt1 set new_locality_code = (
	select code from patiala_boundary jb where  pt1.colony_processed=jb.colony_processed   order by area limit 1
)where new_locality_code isnull;
--------------------------

4.
update patiala_pt_legacy_data set new_locality_code = 'UNKNOWN' where new_locality_code isnull;

-------------------------
OBSOLETE
update patiala_pt_legacy_data as pt1 set new_locality_code = (
	select code from patiala_boundary jb where  jb.colony_processed = pt1.colony_processed and  jb.sector = pt1.sector
)where new_locality_code isnull;

update patiala_pt_legacy_data as pt1 set new_locality_code = (
	select code from patiala_boundary jb where  pt1.colony_processed=jb.colony_processed  limit 1
)where new_locality_code isnull;

update patiala_pt_legacy_data set new_locality_code = 'UNKNOWN' where new_locality_code isnull;

update patiala_pt_legacy_data set new_locality_code = 'UNKNOWN' where new_locality_code isnull and parent_uuid isnull;
-------------------------------------------


#Now for Patiala only those locality_code should be 'UNKNOWN' which assessments belongs to before 2018-19


```
checking localities should have been updated according to correct block and area as more than one colonies may have same name

select new_locality_code,count(*) from patiala_pt_legacy_data group by new_locality_code

select * from patiala_boundary

select distinct colony_processed from patiala_pt_legacy_data where new_locality_code='UNKNOWN'

select * from patiala_pt_legacy_data where colony is null

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```pgsql

patiala SPECIAL CASE
---------------------------
update patiala_pt_legacy_data set upload_status='WONT_UPLOAD' where acknowledgementno::int not in 
(select max(acknowledgementno::int) as ackno from patiala_pt_legacy_data 
group by returnid
)
----------------------------------------------------------------------------------------------------------------------------------------------------------


patiala SPECIAL CASE TO PROCESS MULTIPLE OWNERS AND FLOORS
--------------------------------------------------
-- Owners column contains address at last, also multiple owners are concatenated with '#' 
-- Potgresql code block below will fix this 
--sql block

add two temporary columns in patiala_pt_legacy_data as owner_brushed and owner_multi_temp

update patiala_pt_legacy_data set owner_brushed = owner


DO $$
 DECLARE
  t text[];
  owners record;
  actual_owners text;
  own text;
  counter integer;
 BEGIN
  raise notice 'started';
  counter := 0;
  FOR owners IN select owner_brushed,returnid,session from patiala_pt_legacy_data
  LOOP
       if owners.owner_brushed is null then
         continue; 
       end if;
       actual_owners='';
       if position('#' in owners.owner_brushed) = 0 then
         actual_owners=substring(owners.owner_brushed,0, length(owners.owner_brushed)+1);
       else     
         raise notice 'processing %',owners.owner_brushed;
         select into t string_to_array(owners.owner_brushed,'#');
		 foreach own in array t loop
              actual_owners=concat( actual_owners,' ',substring(own,0, length(own)+1));
		 end loop;
       end if;
       raise notice 'processed record no % ',counter;
       counter := counter + 1;
       update patiala_pt_legacy_data set owner_multi_temp=actual_owners where returnid=owners.returnid and session=owners.session;
      -- raise notice 'actual owner % ******* % ',actual_owners,owners.owner_brushed;	   
  END LOOP;
END$$;


-- now actual owners format is in owner_multi_temp column, we can update actual owners as

update patiala_pt_legacy_data set owner=owner_multi_temp

update patiala_pt_legacy_data set owner=LTRIM(owner) where owner like ' %'  -- remove initial blank space in owners

--now we can remove the columns owner_brushed and owner_multi_temp


-- Floors are found to be concatenated with '#' therefore '#' has to be replaced by ' '

update patiala_pt_legacy_data set floor=replace(floor,'#',' ')
update patiala_pt_legacy_data set leasedetail=replace(leasedetail,'#',' ')

Check before execution 
----------------------------
--update patiala_pt_legacy_data set owner=replace(owner,'Not Provided / Not Applicable','NA') 
select owner from patiala_pt_legacy_data
where owner like '%Not Provided / Not Applicable%'


select floor,leasedetail from patiala_pt_legacy_data where leasedetail is not null and upload_status is null
---------------------------------------------------


Now we are ready to upload the complete data


### Uploading the Ikon data

Clone the implementation kit repo. You need `python3` and `pip3` to use the kit

Run the below commands to install all the required packages

```PGSQL
pip3 install -r requirements.txt
```

In the DB assign the batch id to each record (assumed 10 in this case)

```PGSQL
update patiala_pt_legacy_data set batchname =('{1,2,3,4,5,6,7,8,9,10}'::text[])[ceil(random()*10)] where upload_status is null;
```

After installing all the requirements, update the `run_pt_upload.sh`, use first with `DRY_RUN=True`, once the upload starts working use `DRY_RUN=False`  and use `BATCH_PARALLEL` to increase the number of parallel jobs 

----------------------------------------------------------------
AFTER MIGRATION
-----------------------------------------------------------------

To Settle the demands as all migrated assessments are to be set as paid
-------------------------------------------------------------

--update egbs_demanddetail_v1 set collectionamount=taxamount 
--select count(*) from egbs_demanddetail_v1
where demandid in (select d.id
from egbs_demanddetail_v1 dd, egbs_demand_v1 d
where dd.demandid=d.id
--and d.status!='CANCELLED'
and d.consumercode in (select propertyid from eg_pt_property where tenantId='pb.patiala' and source='LEGACY_RECORD' and channel='LEGACY_MIGRATION' and status='ACTIVE' and createdtime>1622268421628)
and consumercode not in (select distinct consumercode from egbs_bill_v1 bill, egbs_billdetail_v1 bd where status='ACTIVE' and bd.billid=bill.id and consumercode in (select propertyid from eg_pt_property where tenantId='pb.patiala' and source='LEGACY_RECORD' and channel='LEGACY_MIGRATION' and status='ACTIVE' ))
group by d.id)



All Properties with RENTED units are made under status INWORKFLOW so that needed to be APPROVED before assessments
---------------------------------------------------------------------------------------------------------------------- 
--update eg_pt_property set status='INWORKFLOW' 
--select count(*) from eg_pt_property
where id in (select propertyid from eg_pt_unit where occupancytype='RENTED' and active='true') and status='ACTIVE' and tenantid='pb.patiala' and source='LEGACY_RECORD' and channel='LEGACY_MIGRATION' and createdtime>1622268421628  


----------------------------------------
To set height above 36ft for all Flats
----------------------------------------
update eg_pt_property set additionaldetails=cast(concat('{ "heightAbove36Feet": true,',substring(additionaldetails::text,2)) as json)
where additionaldetails->'legacyInfo'->>'buildingcategory'='Flat' and tenantid='pb.patiala' and channel='LEGACY_MIGRATION' and source='LEGACY_RECORD' and status='ACTIVE'
