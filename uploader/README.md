### Property Tax Data Uploader

The property upload process involve two parts

- First parsing the Property details in a format that `Rainmaker (RM)` understand
- Second upload that format using `RM` APIs

The upload script implements this using a `Ikon` dump format, which provides a series of transaction without any unique property id linking them

The parsing is done mainly in `uploader/parsers/ikon.py`. The upload process stores the data in DB to support error checking and upload resumption

### How to run the Ikon Uploader

#### Setting up the database

Setup a DB and create a table based on city you are migrating. Here we will take example as Jalandhar

```postgres-sql
CREATE DATABASE legacy_data;
CREATE USER legacy with encrypted password '<PASSWORD>';
GRANT all privileges on database legacy_data to legacy;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public to legacy;

-- ENABLE UUID extension as we will be using uuid functions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE public.jalandhar_pt_legacy_data (
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
    colony_processed text
);

CREATE INDEX IF NOT EXISTS idx_jalandhar_pt_legacy_data_uuid on jalandhar_pt_legacy_data(uuid);
CREATE INDEX IF NOT EXISTS idx_jalandhar_pt_legacy_data_puuid on jalandhar_pt_legacy_data(parent_uuid);
CREATE INDEX IF NOT EXISTS idx_jalandhar_pt_legacy_data_rno on jalandhar_pt_legacy_data(receipt_number);
CREATE INDEX IF NOT EXISTS idx_jalandhar_pt_legacy_data_rstatus on jalandhar_pt_legacy_data(receipt_status);
CREATE INDEX IF NOT EXISTS idx_jalandhar_pt_legacy_data_ustatus on jalandhar_pt_legacy_data(upload_status);
CREATE INDEX IF NOT EXISTS idx_jalandhar_pt_legacy_data_session on jalandhar_pt_legacy_data(session);
CREATE INDEX IF NOT EXISTS idx_jalandhar_pt_legacy_data_rid on jalandhar_pt_legacy_data(returnid);
CREATE INDEX IF NOT EXISTS idx_jalandhar_pt_legacy_data_prid on jalandhar_pt_legacy_data(previous_returnid);
CREATE INDEX IF NOT EXISTS idx_jalandhar_pt_legacy_data_csector on jalandhar_pt_legacy_data(colony, sector);
CREATE INDEX IF NOT EXISTS idx_jalandhar_pt_legacy_data_locality on jalandhar_pt_legacy_data(new_locality_code);
CREATE INDEX IF NOT EXISTS idx_jalandhar_pt_legacy_data_colony_processed on jalandhar_pt_legacy_data(colony_processed);

CREATE TABLE jalandhar_boundary (
    code text,
    colony text,
    sector text,
    area text,
    colony_processed text
);

CREATE INDEX IF NOT EXISTS idx_jalandhar_boundary_code on jalandhar_boundary(code);
CREATE INDEX IF NOT EXISTS idx_jalandhar_boundary_colony on jalandhar_boundary(colony);
CREATE INDEX IF NOT EXISTS idx_jalandhar_boundary_sector on jalandhar_boundary(sector);
CREATE INDEX IF NOT EXISTS idx_jalandhar_boundary_colony_processed on jalandhar_boundary(colony_processed);

-- Set the FILLFACTOR to 50% so large updates don't take time
ALTER TABLE jalandhar_pt_legacy_data SET (FILLFACTOR = 50);
VACUUM FULL jalandhar_pt_legacy_data;
REINDEX TABLE jalandhar_pt_legacy_data;
```

We have created two tables `jalandhar_pt_legacy_data` (pld) and `jalandhar_boundary_data` (bd). 

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

```postgres-sql
COPY jalandhar_pt_legacy_data(returnid,previous_returnid,acknowledgementno,entrydate,zone,sector,colony,houseno,owner,floor,exemptioncategory,landusedtype,usage,plotarea,totalcoveredarea,grosstax,firecharges,interestamt,penalty,rebate,exemptionamt,taxamt,paymentmode,transactionid,g8bookno,g8receiptno,paymentdate,propertytype,session,buildingcategory)
FROM '/tmp/combined.csv'
WITH (format csv, QUOTE '"', header);
```