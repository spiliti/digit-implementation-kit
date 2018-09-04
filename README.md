#Setup

- Setup Python 3
- Run `pip3 install -r requirements.txt`

## config setup

Create `config/local.py` with below content

```python
from pathlib import Path
import os
from .global_config import config

print(config)

config.BOUNDARIES_FOLDER = Path(r"/Users/tarunlalwani/Desktop/eGovernments/implementation/scripts/source/")

config.MDMS_LOCATION = Path(r"/Users/tarunlalwani/Desktop/eGovernments/repos/punjab-mdms-data-uat/data/pb")

config.TENANT = "pb"
config.CITY_NAME = os.getenv("CITY", None) or "Zirakpur"

config.CONFIG_ENV = "PROD"

import importlib

importlib.import_module("." + config.CONFIG_ENV, "config")
``` 

Create environment config `config/PROD.py`

```python
from pathlib import Path

from .global_config import config
from attrdict import AttrDict

config.MDMS_LOCATION = Path(r"/Users/tarunlalwani/Desktop/eGovernments/repos/punjab-mdms-data-prod/data/pb")
config.HOST = "https://xxxxxx"

SUPERUSER = AttrDict()

SUPERUSER.username = "xxxx"
SUPERUSER.password = "xxxxx"
SUPERUSER.tenant_id = "pb.xxx"

config.SUPERUSER = SUPERUSER
```