#!/bin/bash

  export tenant_id=$1
  cat TenantGoLive.template.sql | sed -e "s|__tenant_id|$tenant_id|g" > TenantGoLive.$tenant_id.sql

