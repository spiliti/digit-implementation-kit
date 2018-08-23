SET search_path TO hr_masters_v2_schema,public;

delete from egeis_hrconfigurationvalues where tenantid='pb.__tenant_id';
delete from egeis_hrconfiguration where tenantid='pb.__tenant_id';
delete from egeis_hrstatus where tenantid='pb.__tenant_id';

insert into egeis_hrstatus(id,objectname,code,description,tenantid) values (nextval('seq_egeis_hrStatus'),'Employee Master',
'EMPLOYED','Currently employee of the system','pb.__tenant_id');
insert into egeis_hrstatus(id,objectname,code,description,tenantid) values (nextval('seq_egeis_hrStatus'),'Employee Master',
'RETIRED','Employee who is currently retired','pb.__tenant_id');
insert into egeis_hrstatus(id,objectname,code,description,tenantid) values (nextval('seq_egeis_hrStatus'),'Employee Master',
'DECEASED','Employee who is deceased when in service','pb.__tenant_id');

insert into egeis_hrConfiguration(id,keyname,description,createdby,createddate,lastmodifiedby,lastmodifieddate,tenantid) values(nextval('seq_egeis_hrConfiguration'),'Weekly_holidays','Define the weekly off for the organization',1,now(),1,now(),'pb.__tenant_id');
insert into egeis_hrConfiguration(id,keyname,description,createdby,createddate,lastmodifiedby,lastmodifieddate,tenantid) values(nextval('seq_egeis_hrConfiguration'),'Autogenerate_employeecode','This will define if employee code needs to be system generated or manually captured',1,now(),1,now(),'pb.__tenant_id');
insert into egeis_hrConfiguration(id,keyname,description,createdby,createddate,lastmodifiedby,lastmodifieddate,tenantid) values(nextval('seq_egeis_hrConfiguration'),'Include_enclosed_holidays','This will define if system needs to consider the holidays coming between as leave or not',1,now(),1,now(),'pb.__tenant_id');
insert into egeis_hrConfiguration(id,keyname,description,createdby,createddate,lastmodifiedby,lastmodifieddate,tenantid) values(nextval('seq_egeis_hrConfiguration'),'Compensatory leave validity','This will define the number of days till which an employee can apply for compensatory off',1,now(),1,now(),'pb.__tenant_id');

insert into egeis_hrConfigurationValues(id,keyid,value,effectivefrom,createdby,createddate,lastmodifiedby,lastmodifieddate,tenantid)
values(nextval('seq_egeis_hrConfigurationValues'),(select id from egeis_hrconfiguration where keyname='Weekly_holidays' and tenantid='pb.__tenant_id'),'5-day week',
'2016-01-01',1,now(),1,now(),'pb.__tenant_id');
insert into egeis_hrConfigurationValues(id,keyid,value,effectivefrom,createdby,createddate,lastmodifiedby,lastmodifieddate,tenantid)
values(nextval('seq_egeis_hrConfigurationValues'),(select id from egeis_hrconfiguration where keyname='Autogenerate_employeecode' and tenantid='pb.__tenant_id'),'N',
'2016-01-01',1,now(),1,now(),'pb.__tenant_id');
insert into egeis_hrConfigurationValues(id,keyid,value,effectivefrom,createdby,createddate,lastmodifiedby,lastmodifieddate,tenantid)
values(nextval('seq_egeis_hrConfigurationValues'),(select id from egeis_hrconfiguration where keyname='Include_enclosed_holidays' and tenantid='pb.__tenant_id'),'N',
'2016-01-01',1,now(),1,now(),'pb.__tenant_id');
insert into egeis_hrConfigurationValues(id,keyid,value,effectivefrom,createdby,createddate,lastmodifiedby,lastmodifieddate,tenantid)
values(nextval('seq_egeis_hrConfigurationValues'),(select id from egeis_hrconfiguration where keyname='Compensatory leave validity' and tenantid='pb.__tenant_id'),'90',
'2016-01-01',1,now(),1,now(),'pb.__tenant_id');

insert into egeis_hrstatus(id,objectname,code,description,tenantid) values (nextval('seq_egeis_hrStatus'),'Employee Master',
'SUSPENDED','Employee who is suspended','pb.__tenant_id');

insert into egeis_hrstatus(id,objectname,code,description,tenantid) values (nextval('seq_egeis_hrStatus'),'Employee Master',
'TRANSFERRED','Employee who is transferred','pb.__tenant_id');

insert into egeis_hrstatus(id,objectname,code,description,tenantid) values (nextval('seq_egeis_hrStatus'),'LeaveApplication','APPLIED','Leave Status when applied','pb.__tenant_id');
insert into egeis_hrstatus(id,objectname,code,description,tenantid) values (nextval('seq_egeis_hrStatus'),'LeaveApplication','APPROVED','Leave Status when approved','pb.__tenant_id');
insert into egeis_hrstatus(id,objectname,code,description,tenantid) values (nextval('seq_egeis_hrStatus'),'LeaveApplication','REJECTED','Leave Status when rejected','pb.__tenant_id');
insert into egeis_hrstatus(id,objectname,code,description,tenantid) values (nextval('seq_egeis_hrStatus'),'LeaveApplication','CANCELLED','Leave Status when cancelled','pb.__tenant_id');
insert into egeis_hrstatus(id,objectname,code,description,tenantid) values (nextval('seq_egeis_hrStatus'),'LeaveApplication','RESUBMITTED','Leave Status when resubmitted','pb.__tenant_id');

insert into egeis_hrConfiguration(id,keyname,description,createdby,createddate,lastmodifiedby,lastmodifieddate,tenantid) values(nextval('seq_egeis_hrConfiguration'),'Cutoff_Date','Define the cut off date after which the application will go live',1,now(),1,now(),'pb.__tenant_id');

insert into egeis_hrConfigurationValues(id,keyid,value,effectivefrom,createdby,createddate,lastmodifiedby,lastmodifieddate,tenantid)
values(nextval('seq_egeis_hrConfigurationValues'),(select id from egeis_hrconfiguration where keyname='Cutoff_Date' and tenantid='pb.__tenant_id'),'2017-05-31',
'2016-01-01',1,now(),1,now(),'pb.__tenant_id');

insert into egeis_hrstatus(id,objectname,code,description,tenantid) values (nextval('seq_egeis_hrStatus'),'EmployeeMovement','APPLIED','Employee Movement when applied','pb.__tenant_id');
insert into egeis_hrstatus(id,objectname,code,description,tenantid) values (nextval('seq_egeis_hrStatus'),'EmployeeMovement','APPROVED','Employee Movement when approved','pb.__tenant_id');
insert into egeis_hrstatus(id,objectname,code,description,tenantid) values (nextval('seq_egeis_hrStatus'),'EmployeeMovement','REJECTED','Employee Movement when rejected','pb.__tenant_id');
insert into egeis_hrstatus(id,objectname,code,description,tenantid) values (nextval('seq_egeis_hrStatus'),'EmployeeMovement','CANCELLED','Employee Movement when cancelled','pb.__tenant_id');
insert into egeis_hrstatus(id,objectname,code,description,tenantid) values (nextval('seq_egeis_hrStatus'),'EmployeeMovement','RESUBMITTED','Employee Movement when resubmitted','pb.__tenant_id');

SELECT setval('seq_egeis_designation', nextval('seq_egeis_designation'), true);


INSERT INTO egeis_hrConfiguration (id, keyname, description, createdby, createddate, lastmodifiedby, lastmodifieddate, tenantid)
    VALUES (nextval('seq_egeis_hrConfiguration'), 'Autogenerate_username', 'This will define if username for employee needs to be system generated or manually captured', 1, now(), 1, now(), 'pb.__tenant_id');

INSERT INTO egeis_hrConfigurationValues (id, keyid, value, effectivefrom, createdby, createddate, lastmodifiedby, lastmodifieddate, tenantid)
    VALUES(nextval('seq_egeis_hrConfigurationValues'), (SELECT id FROM egeis_hrconfiguration WHERE keyname='Autogenerate_username' AND tenantid='pb.__tenant_id'), 'Y', '2016-01-01', 1, now(), 1, now(), 'pb.__tenant_id');

update egeis_hrconfiguration set keyname='Compensatory_leave_validity' where keyname='Compensatory leave validity';

insert into egeis_hrstatus(id,objectname,code,description,tenantid) values (nextval('seq_egeis_hrStatus'),'LeaveApplication','FORWARDED','Leave Status when forwarded','pb.__tenant_id');


insert into eg_role (id,name,code,description,createddate,createdby,lastmodifiedby,lastmodifieddate,version,tenantid)values
(nextval('SEQ_EG_ROLE'),'Citizen','CITIZEN','Citizen who can raise complaint',now(),1,1,now(),0,'pb.__tenant_id')
ON CONFLICT (code, tenantid) DO NOTHING;

insert into eg_role (id,name,code,description,createddate,createdby,lastmodifiedby,lastmodifieddate,version,tenantid)values
(nextval('SEQ_EG_ROLE'),'Employee','EMPLOYEE','Default role for all employees',now(),1,1,now(),0,'pb.__tenant_id')
ON CONFLICT (code, tenantid) DO NOTHING;

insert into eg_role (id,name,code,description,createddate,createdby,lastmodifiedby,lastmodifieddate,version,tenantid)values
(nextval('SEQ_EG_ROLE'),'Grievance Routing Officer','GRO','Grievance Routing Officer',now(),1,1,now(),0,'pb.__tenant_id')
ON CONFLICT (code, tenantid) DO NOTHING;

insert into eg_role (id,name,code,description,createddate,createdby,lastmodifiedby,lastmodifieddate,version,tenantid)values
(nextval('SEQ_EG_ROLE'),'Citizen Service Representative','CSR',
'Employee who files and follows up complaints on behalf of the citizen',now(),1,1,now(),0,'pb.__tenant_id')
ON CONFLICT (code, tenantid) DO NOTHING;

insert into eg_role (id,name,code,description,createddate,createdby,lastmodifiedby,lastmodifieddate,version,tenantid)values
(nextval('SEQ_EG_ROLE'),'PGR Administrator','PGR-ADMIN','Admin role that has super access over the system',now(),1,1,now(),0,'pb.__tenant_id')
ON CONFLICT (code, tenantid) DO NOTHING;

insert into eg_role (id,name,code,description,createddate,createdby,lastmodifiedby,lastmodifieddate,version,tenantid)values
(nextval('SEQ_EG_ROLE'),'Super User','SUPERUSER','System Administrator. Can change all master data and has access to all the system screens.',now(),1,1,now(),0,'pb.__tenant_id')
ON CONFLICT (code, tenantid) DO NOTHING;