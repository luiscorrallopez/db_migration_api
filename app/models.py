import yaml
from sqlalchemy import Column, Integer, String, ForeignKey
from .database import Base

TYPE_MAP = {
    "integer": Integer,
    "string": String
}

with open("schemas.yml", "r") as f:
    schemas = yaml.safe_load(f)

for table, fields in schemas.items():
    attrs = {"__tablename__": table}
    for field_name, field_type in fields.items():
        col_type = TYPE_MAP[field_type]
        is_pk = field_name == "id"
        fk = None

        if field_name.endswith("_id") and table != "departments" and table != "jobs":
            ref_table = field_name.replace("_id", "s")
            fk = ForeignKey(f"{ref_table}.id")

        attrs[field_name] = Column(col_type, primary_key=is_pk, index=is_pk, nullable=False, foreign_key=fk) if fk \
            else Column(col_type, primary_key=is_pk, index=is_pk, nullable=False)

    model = type(table.capitalize(), (Base,), attrs)
    globals()[model.__name__] = model