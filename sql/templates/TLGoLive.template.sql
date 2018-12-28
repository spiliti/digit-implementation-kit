BEGIN;

--> user module (roles for new TL employee roles)
insert into eg_role (id,name,code,description,createddate,createdby,lastmodifiedby,lastmodifieddate,version,tenantid)values
(nextval('SEQ_EG_ROLE'),'TL Counter Employee','TL_CEMP','Counter Employee in Trade License who files TL on behalf of the citizen',now(),1,1,now(),0,'pb.__city__')
ON CONFLICT (code, tenantid) DO NOTHING;

insert into eg_role (id,name,code,description,createddate,createdby,lastmodifiedby,lastmodifieddate,version,tenantid)values
(nextval('SEQ_EG_ROLE'),'TL Approver','TL_APPROVER','Approver who verifies and approves the TL application',now(),1,1,now(),0,'pb.__city__')
ON CONFLICT (code, tenantid) DO NOTHING;


--> billing service queries ( includes businessservice, taxperiod, txheadmaster, glcodemaster )

INSERT INTO egbs_business_service_details (id, businessservice, collectionmodesnotallowed, callbackforapportioning, partpaymentallowed, callbackapportionurl, createddate, lastmodifieddate, createdby, lastmodifiedby, tenantid) VALUES (uuid_in(md5(random()::text || now()::text)::cstring), 'TL', '', false, false, NULL, (select extract ('epoch' from (select * from now()))*1000)
, (select extract ('epoch' from (select * from now()))*1000)
, '94', '94', 'pb.__city__') ON CONFLICT DO NOTHING;


INSERT INTO egbs_taxperiod (id, service, code, fromdate, todate, financialyear, createddate, lastmodifieddate, createdby, lastmodifiedby, tenantid, periodcycle) VALUES (nextval('seq_egbs_taxperiod'), 'TL', 'TLAN2014-15', 1396310400000, 1427846399000, '2014-15', (select extract ('epoch' from (select * from now()))*1000)
, (select extract ('epoch' from (select * from now()))*1000)
, '94', '94', 'pb.__city__', 'ANNUAL');
INSERT INTO egbs_taxperiod (id, service, code, fromdate, todate, financialyear, createddate, lastmodifieddate, createdby, lastmodifiedby, tenantid, periodcycle) VALUES (nextval('seq_egbs_taxperiod'), 'TL', 'TLAN2015-16', 1427846400000, 1459468799000, '2015-16', (select extract ('epoch' from (select * from now()))*1000)
, (select extract ('epoch' from (select * from now()))*1000)
, '94', '94', 'pb.__city__', 'ANNUAL');
INSERT INTO egbs_taxperiod (id, service, code, fromdate, todate, financialyear, createddate, lastmodifieddate, createdby, lastmodifiedby, tenantid, periodcycle) VALUES (nextval('seq_egbs_taxperiod'), 'TL', 'TLAN2016-17', 1459468800000, 1491004799000, '2016-17', (select extract ('epoch' from (select * from now()))*1000)
, (select extract ('epoch' from (select * from now()))*1000)
, '94', '94', 'pb.__city__', 'ANNUAL');
INSERT INTO egbs_taxperiod (id, service, code, fromdate, todate, financialyear, createddate, lastmodifieddate, createdby, lastmodifiedby, tenantid, periodcycle) VALUES (nextval('seq_egbs_taxperiod'), 'TL', 'TLAN2017-18', 1491004800000, 1522540799000, '2017-18', (select extract ('epoch' from (select * from now()))*1000)
, (select extract ('epoch' from (select * from now()))*1000)
, '94', '94', 'pb.__city__', 'ANNUAL');
INSERT INTO egbs_taxperiod (id, service, code, fromdate, todate, financialyear, createddate, lastmodifieddate, createdby, lastmodifiedby, tenantid, periodcycle) VALUES (nextval('seq_egbs_taxperiod'), 'TL', 'TLAN2018-19', 1522540800000, 1554076799000, '2018-19', (select extract ('epoch' from (select * from now()))*1000)
, (select extract ('epoch' from (select * from now()))*1000)
, '94', '94', 'pb.__city__', 'ANNUAL');


INSERT INTO egbs_taxheadmaster (id, tenantid, category, service, name, code, isdebit, isactualdemand, orderno, validfrom, validtill, createdby, createdtime, lastmodifiedby, lastmodifiedtime) VALUES (nextval('seq_egbs_taxheadmaster'), 'pb.__city__', 'PENALTY', 'TL', 'TL adhoc penalty', 'TL_ADHOC_PENALTY', false, true, 1, 1143849600000, 1554076799000, '94', (select extract ('epoch' from (select * from now()))*1000)
, '94', (select extract ('epoch' from (select * from now()))*1000)
);
INSERT INTO egbs_taxheadmaster (id, tenantid, category, service, name, code, isdebit, isactualdemand, orderno, validfrom, validtill, createdby, createdtime, lastmodifiedby, lastmodifiedtime) VALUES (nextval('seq_egbs_taxheadmaster'), 'pb.__city__', 'REBATE', 'TL', 'TL adhoc rebate', 'TL_ADHOC_REBATE', true, true, 100, 1143849600000, 1554076799000, '94', (select extract ('epoch' from (select * from now()))*1000)
, '94', (select extract ('epoch' from (select * from now()))*1000)
);
INSERT INTO egbs_taxheadmaster (id, tenantid, category, service, name, code, isdebit, isactualdemand, orderno, validfrom, validtill, createdby, createdtime, lastmodifiedby, lastmodifiedtime) VALUES (nextval('seq_egbs_taxheadmaster'), 'pb.__city__', 'TAX', 'TL', 'propertytax', 'TL_TAX', false, true, 3, 1143849600000, 1554076799000, '94', (select extract ('epoch' from (select * from now()))*1000)
, '94', (select extract ('epoch' from (select * from now()))*1000)
);


INSERT INTO egbs_glcodemaster (id, tenantid, taxhead, service, fromdate, todate, createdby, createdtime, lastmodifiedby, lastmodifiedtime, glcode) VALUES (nextval('seq_egbs_glcodemaster'), 'pb.__city__', 'TL_TAX', 'TL', 1143849600000, 1554076799000, '94', (select extract ('epoch' from (select * from now()))*1000)
, '94', (select extract ('epoch' from (select * from now()))*1000)
, '1100102');
INSERT INTO egbs_glcodemaster (id, tenantid, taxhead, service, fromdate, todate, createdby, createdtime, lastmodifiedby, lastmodifiedtime, glcode) VALUES (nextval('seq_egbs_glcodemaster'), 'pb.__city__', 'TL_ADHOC_PENALTY', 'TL', 1143849600000, 1554076799000, '94', (select extract ('epoch' from (select * from now()))*1000)
, '94', (select extract ('epoch' from (select * from now()))*1000)
, '1718002');
INSERT INTO egbs_glcodemaster (id, tenantid, taxhead, service, fromdate, todate, createdby, createdtime, lastmodifiedby, lastmodifiedtime, glcode) VALUES (nextval('seq_egbs_glcodemaster'), 'pb.__city__', 'TL_ADHOC_REBATE', 'TL', 1143849600000, 1554076799000, '94', (select extract ('epoch' from (select * from now()))*1000)
, '94', (select extract ('epoch' from (select * from now()))*1000)
, '2703002');


--> egf-master/financials ( chartofaccount )

INSERT INTO egf_chartofaccount (id, glcode, name, accountcodepurposeid, description, isactiveforposting, parentid, type, classification, functionrequired, budgetcheckrequired, majorcode, issubledger, createdby, createddate, lastmodifiedby, lastmodifieddate, version, tenantid) VALUES (nextval('seq_egf_chartofaccount'), '1100102', 'Trade License-General Tax', NULL, NULL, true, (select id from egf_chartofaccount where glcode = '11001' and tenantid='pb.__city__'), 'I', 4, false, false, '110', false, NULL, now(), NULL, now(), NULL, 'pb.__city__');

INSERT INTO egf_chartofaccount (id, glcode, name, accountcodepurposeid, description, isactiveforposting, parentid, type, classification, functionrequired, budgetcheckrequired, majorcode, issubledger, createdby, createddate, lastmodifiedby, lastmodifieddate, version, tenantid) VALUES (nextval('seq_egf_chartofaccount'), '1718002', 'TL-Interest or Penalty', NULL, NULL, true, (select id from egf_chartofaccount where glcode = '17180' and tenantid='pb.__city__'), 'I', 4, false, false, '171', false, NULL, now(), NULL, now(), NULL, 'pb.__city__');

INSERT INTO egf_chartofaccount (id, glcode, name, accountcodepurposeid, description, isactiveforposting, parentid, type, classification, functionrequired, budgetcheckrequired, majorcode, issubledger, createdby, createddate, lastmodifiedby, lastmodifieddate, version, tenantid) VALUES (nextval('seq_egf_chartofaccount'), '2703002', 'Write off - TL Tax', NULL, NULL, true, (select id from egf_chartofaccount where glcode = '27030' and tenantid='pb.__city__'), 'E', 4, false, false, '270', false, NULL, now(), NULL, now(), NULL, 'pb.__city__');


--> common masters ( businesscategory ad businessdetails)

insert into eg_businesscategory(id,name,code,active,tenantid,version,createdby,lastmodifiedby,createddate,lastmodifieddate) values(
nextval('seq_eg_businesscategory'),'Trade License','TL',true,'pb.__city__',0,1,1,(select extract ('epoch' from (select * from now()))*1000)
,(select extract ('epoch' from (select * from now()))*1000)
) ON CONFLICT DO NOTHING;

insert into eg_businessdetails(id,name,businessurl,isenabled,code,businesstype,fund,function,department,vouchercreation,
businesscategory,isvoucherapproved,createdby,
lastmodifiedby,ordernumber,version,tenantid,callbackforapportioning,createddate,lastmodifieddate)
values(nextval('seq_eg_businessdetails'),'Trade License','/receipts/receipt-create.action',true,'TL','ADHOC','01','909100','DEPT_1',false,
(select id from eg_businesscategory where code='TL' and tenantid='pb.__city__'),false,1,1,1,0,'pb.__city__',false,(select extract ('epoch' from (select * from now()))*1000)
,(select extract ('epoch' from (select * from now()))*1000)
) ON CONFLICT DO NOTHING;

COMMIT;
