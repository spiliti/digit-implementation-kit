#!/bin/bash

cat tenants | xargs -n1 ./create_tenant.sh
