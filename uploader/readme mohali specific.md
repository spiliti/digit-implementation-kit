### Property Tax Data Uploader

The property upload process involve two parts

- First parsing the Property details in a format that `Rainmaker (RM)` understand
- Second upload that format using `RM` APIs

The upload script implements this using a `Ikon` dump format, which provides a series of transaction without any unique property id linking them

The parsing is done mainly in `uploader/parsers/ikon.py`. The upload process stores the data in DB to support error checking and upload resumption

### How to run the Ikon Uploader

#### Setting up the database

Setup a DB and create a table based on city you are migrating. Here we will take example as mohali

```pgsql
CREATE DATABASE legacy_data;
CREATE USER legacy with encrypted password '<PASSWORD>';
GRANT all privileges on database legacy_data to legacy;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public to legacy;

-- ENABLE UUID extension as we will be using uuid functions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE mohali_pt_legacy_data (
    srno text,
    returnid text,
    acknowledgementno text,
    entrydate text,
    zone text,
    sector text,
    colony text,
    houseno text,
    owner text,
    floor text,
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

CREATE INDEX IF NOT EXISTS idx_mohali_pt_legacy_data_uuid on mohali_pt_legacy_data(uuid);
CREATE INDEX IF NOT EXISTS idx_mohali_pt_legacy_data_puuid on mohali_pt_legacy_data(parent_uuid);
CREATE INDEX IF NOT EXISTS idx_mohali_pt_legacy_data_rno on mohali_pt_legacy_data(receipt_number);
CREATE INDEX IF NOT EXISTS idx_mohali_pt_legacy_data_rstatus on mohali_pt_legacy_data(receipt_status);
CREATE INDEX IF NOT EXISTS idx_mohali_pt_legacy_data_ustatus on mohali_pt_legacy_data(upload_status);
CREATE INDEX IF NOT EXISTS idx_mohali_pt_legacy_data_session on mohali_pt_legacy_data(session);
CREATE INDEX IF NOT EXISTS idx_mohali_pt_legacy_data_rid on mohali_pt_legacy_data(returnid);
CREATE INDEX IF NOT EXISTS idx_mohali_pt_legacy_data_prid on mohali_pt_legacy_data(previous_returnid);
CREATE INDEX IF NOT EXISTS idx_mohali_pt_legacy_data_csector on mohali_pt_legacy_data(colony, sector);
CREATE INDEX IF NOT EXISTS idx_mohali_pt_legacy_data_locality on mohali_pt_legacy_data(new_locality_code);
CREATE INDEX IF NOT EXISTS idx_mohali_pt_legacy_data_colony_processed on mohali_pt_legacy_data(colony_processed);

CREATE TABLE mohali_boundary (
    code text,
    colony text,
    sector text,
    area text,
    colony_processed text
);

CREATE INDEX IF NOT EXISTS idx_mohali_boundary_code on mohali_boundary(code);
CREATE INDEX IF NOT EXISTS idx_mohali_boundary_colony on mohali_boundary(colony);
CREATE INDEX IF NOT EXISTS idx_mohali_boundary_sector on mohali_boundary(sector);
CREATE INDEX IF NOT EXISTS idx_mohali_boundary_colony_processed on mohali_boundary(colony_processed);

-- Set the FILLFACTOR to 50% so large updates don't take time
ALTER TABLE mohali_pt_legacy_data SET (FILLFACTOR = 50);
VACUUM FULL mohali_pt_legacy_data;
REINDEX TABLE mohali_pt_legacy_data;
```


We have created two tables `mohali_pt_legacy_data` (pld) and `mohali_boundary_data` (bd). We will be using `pld` and `bd` as shortcuts for these tables in the document moving forward

The fields in `pld` till `remarks` are for storing the data received in the CSV dumps from Ikons. The fields aftewards are used by the uploader script to manage state and status of the application. The `bd` table used to do mapping of old colony versus new boundary data in `RM` 

#### Importing the ikon data

Ikon provides data in different `xlsx` file for each year and each file has multiple tabs. To import this data as single csv file we first extract all the data in `csv` files

To do this use `uploader/process_excel_to_csv.py` and convert each file to csv.

Once all the files are converted, combine all of them to a single `csv`

```bash
cat *.csv > combined.csv
```

Open the `combined.csv` files and make sure the headers in below order

```csv
returnid,previous_returnid,acknowledgementno,entrydate,zone,sector,colony,houseno,owner,floor,exemptioncategory,landusedtype,usage,plotarea,totalcoveredarea,grosstax,firecharges,interestamt,penalty,rebate,exemptionamt,taxamt,paymentmode,transactionid,g8bookno,g8receiptno,paymentdate,propertytype,session,buildingcategory
```

If columns are not in this order, reorder them. After that import all the data into the DB using below command

```pgsql
COPY mohali_pt_legacy_data(returnid,previous_returnid,acknowledgementno,entrydate,zone,sector,colony,houseno,owner,floor,exemptioncategory,landusedtype,usage,plotarea,totalcoveredarea,grosstax,firecharges,interestamt,penalty,rebate,exemptionamt,taxamt,paymentmode,transactionid,g8bookno,g8receiptno,paymentdate,propertytype,session,buildingcategory,businessname,waterconnectionno,electrictyconnectionno,photoid)
FROM '/tmp/combined.csv'
WITH (format csv, QUOTE '"', header);
```


Now that the data is imported, we want to be able to identify each record using a unique identifier, so we assign a `uuid` to each record

```pgsql
update mohali_pt_legacy_data set uuid = uuid_generate_v4();

update mohali_pt_legacy_data set 
new_propertyid = NULL, upload_status = NULL, receipt_status = NULL, receipt_number = NUll, receipt_request = null, receipt_response = null, req_json = Null, parent_uuid = Null, upload_response = null;
```

--------------------------------------
MOHALI SPECIAL CASE
update mohali_pt_legacy_data set upload_status='WONT_UPLOAD' where acknowledgementno::int not in 
(select max(acknowledgementno::int) as ackno from mohali_pt_legacy_data 
group by split_part(returnid,'_',1)
)
--------------------------------------




We also map the `uuid` to `parent_uuid` for matching the `previous_returnid` using below queries

----------------------
MOHALI SPECIAL CASE FOR BELOW QUERIES

update  mohali_pt_legacy_data as pt1  set parent_uuid = (select max(uuid) from mohali_pt_legacy_data pt2
where split_part(pt2.ReturnId,'_',1) = split_part(pt1.ReturnId,'_',1)  and Session = '2013-14' group by split_part(pt2.ReturnId,'_',1) )
where Session = '2014-15';

SIMILAR REPEAT FOR ALL YEARS
----------------------

```PGSQL
update mohali_pt_legacy_data as pt1 set parent_uuid = ( select uuid from pt_legacy_data pt2 
where pt2.ReturnId = pt1.previous_returnid and Session = '2013-2014'
)where Session = '2014-2015';

update mohali_pt_legacy_data as pt1 set parent_uuid = ( select uuid from pt_legacy_data pt2 
where pt2.ReturnId = pt1.previous_returnid and Session = '2014-2015'
)where Session = '2015-2016';

update mohali_pt_legacy_data as pt1 set parent_uuid = ( select uuid from pt_legacy_data pt2 
where pt2.ReturnId = pt1.previous_returnid and Session = '2015-2016'
)where Session = '2016-2017';

update mohali_pt_legacy_data as pt1 set parent_uuid = ( select uuid from pt_legacy_data pt2 
where pt2.ReturnId = pt1.previous_returnid and Session = '2016-2017'
)where Session = '2017-2018';

update mohali_pt_legacy_data as pt1 set parent_uuid = ( select uuid from pt_legacy_data pt2 
where pt2.ReturnId = pt1.previous_returnid and Session = '2017-2018'
)where Session = '2018-2019';

update mohali_pt_legacy_data as pt1 set parent_uuid = ( select uuid from pt_legacy_data pt2 
where pt2.ReturnId = pt1.previous_returnid and Session = '2018-2019'
)where Session = '2019-2020';
```


---------------------------------------
MOHALI SPECIAL CASE

update mohali_pt_legacy_data set session='2013-2014' where session='2013-14'

SIMILAR REPEAT FOR ALL YEARS

------------------------------------
#### Mapping the colonies to RM

Make sure the boundary has a `UNKNOWN` code, so that colonies which are not mapped can be moved to `UNKNOWN` code 

Run the `revenue_boundary_gen_download.py` to download the boundary data for the given tenant.

Upload the 
`Rev Block/ward code` (sector), `Locality name` (colony),	`Locality Code` (code), `Area name` (area) fields to `bd` table

Now update the localities in DB

```PGSQL


update mohali_pt_legacy_data set colony_processed = regexp_replace(regexp_replace(trim(upper(colony)),'[^a-zA-Z0-9]+', ' ','g'),'\s+', ' ')

----------------------------------
MOHALI SPECIAL CASE

update mohali_pt_legacy_data set colony_processed = concat('SECTOR ',regexp_replace(regexp_replace(trim(upper(sector)),'[^a-zA-Z0-9]+', ' ','g'),'\s+', ' '))

----------------------------------

update mohali_boundary set colony_processed = regexp_replace(regexp_replace(trim(upper(colony)),'[^a-zA-Z0-9]+', ' ','g'),'\s+', ' ')

update mohali_pt_legacy_data as pt1 set new_locality_code = (
	select code from mohali_boundary jb where  jb.colony_processed = pt1.colony_processed and  jb.sector = pt1.sector
)
where new_locality_code isnull;

update mohali_pt_legacy_data as pt1 set new_locality_code = (
	select code from mohali_boundary jb where  pt1.colony_processed=jb.colony_processed  limit 1
)
where new_locality_code isnull;

update mohali_pt_legacy_data set new_locality_code = 'UNKNOWN' where new_locality_code isnull;

update mohali_pt_legacy_data set new_locality_code = 'UNKNOWN' where new_locality_code isnull and parent_uuid isnull;
```

#### Marking which data doesn't need to uploaded

Since we are getting transaction data from `ikon`, we will only need to upload property with latest details from the latest receipt. So a record which exist in all years (`2013-14` to `2019-20`), will only be processed in `2019-20`.

To do this we run the below query

```pgsql

update mohali_pt_legacy_data pd set upload_status = 'WONT_UPLOAD'
where
pd.upload_status is NULL and
pd.new_locality_code is not null
and exists (
    select uuid from mohali_pt_legacy_data as pt2
        where pt2.previous_returnid = pd.returnid
            and pt2.session = CONCAT(split_part(pd.session, '-',2), '-', (split_part(pd.session, '-',2)::int + 1)::text)
```
--------------------------------------
MOHALI SPECIAL CASE
update mohali_pt_legacy_data set upload_status='WONT_UPLOAD' where acknowledgementno::int not in 
(select max(acknowledgementno::int) as ackno from mohali_pt_legacy_data 
group by split_part(returnid,'_',1)
)
--------------------------------------



MOHALI SPECIAL CASE TO PROCESS MULTIPLE OWNERS AND FLOORS
--------------------------------------------------
-- Owners column contains address at last, also multiple owners are concatenated with '#' 
-- Potgresql code block below will fix this 
--sql block

add two temporary columns in mohali_pt_legacy_data as owner_brushed and owner_multi_temp

update mohali_pt_legacy_data set owner_brushed = owner

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
  FOR owners IN select owner_brushed,returnid,session from mohali_pt_legacy_data
  LOOP
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
       update mohali_pt_legacy_data set owner_multi_temp=actual_owners where returnid=owners.returnid and session=owners.session;
      -- raise notice 'actual owner % ******* % ',actual_owners,owners.owner_brushed;	   
  END LOOP;
END$$;


-- now actual owners format is in owner_multi_temp column, we can update actual owners as

update mohali_pt_legacy_data set owner=owner_multi_temp

update mohali_pt_legacy_data set owner=LTRIM(owner) where owner like ' %'  -- remove initial blank space in owners

--now we can remove the columns owner_brushed and owner_multi_temp


-- Floors are found to be concatenated with '#' therefore '#' has to be replaced by ' '
update mohali_pt_legacy_data set floor=replace(floor,'#',' ')

-- As Floor usage master may vary in mohali therefore we have to update floor usages also

update mohali_pt_legacy_data  set floor=replace(floor,'Hotel/Motel','Hotel') where floor like '%Hotel/Motel%'

update mohali_pt_legacy_data set floor=replace(floor,'Flats(Complexes/Society/Apartments/MIG Super)','Flats') where floor like '%Flats(Complexes/Society/Apartments/MIG Super)%'

update mohali_pt_legacy_data set floor=replace(floor,'Industrial /Educational / Godown','Industrial') where floor like '%Industrial /Educational / Godown%'

update mohali_pt_legacy_data set floor=replace(floor,'Multiplex/Shopping Malls','Shopping Malls') where floor like '%Multiplex/Shopping Malls%'


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
update mohali_pt_legacy_data set batchname =('{1,2,3,4,5,6,7,8,9,10}'::text[])[ceil(random()*10)] where upload_status is null;
```

After installing all the requirements, update the `run_pt_upload.sh`, use first with `DRY_RUN=True`, once the upload starts working use `DRY_RUN=False`  and use `BATCH_PARALLEL` to increase the number of parallel jobs 