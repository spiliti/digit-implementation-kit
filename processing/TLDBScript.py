import io
from config import config

tenants = [
    "pb.abohar",
    "pb.zira"
]


with io.open(config.BASE_PPATH / "sql" / "templates" / "TLGoLive.template.sql") as f:
    template = f.read()
    data = []

    for tenant in tenants:
        data = template.replace("pb.__city__", tenant)

        with io.open(config.BASE_PPATH / "sql" / "output" / "TL" / "TL_{}.sql".format(tenant), mode="w") as f2:
            # f2.write("\n\n".join(data))
            f2.write(data)
