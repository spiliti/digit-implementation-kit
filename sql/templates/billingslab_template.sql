delete from eg_pt_billingslab_v2 where tenantid = '__tenant_id';

INSERT INTO public.eg_pt_billingslab_v2 (id, tenantid, propertytype, propertysubtype, usagecategorymajor, usagecategoryminor, usagecategorysubminor, usagecategorydetail, ownershipcategory, subownershipcategory, fromfloor, tofloor, areatype, occupancytype, fromplotsize, toplotsize, unitrate, createdby, createdtime, lastmodifiedby, lastmodifiedtime, ispropertymultifloored, unbuiltunitrate, arvpercent)

select uuid_in(md5(random()::text || now()::text || random()::text)::cstring ) as id, '__tenant_id' as tenantid, propertytype, propertysubtype, usagecategorymajor, usagecategoryminor, usagecategorysubminor, usagecategorydetail, ownershipcategory, subownershipcategory, fromfloor, tofloor, areatype, occupancytype, fromplotsize, toplotsize, unitrate, createdby, createdtime, lastmodifiedby, lastmodifiedtime, ispropertymultifloored, unbuiltunitrate, arvpercent from eg_pt_billingslab_v2 where tenantid = 'pb.categoryc';

