import json
from tvm.models import Category, SubCategory, AdvisoryText
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# uses knowledge/templates.json to seed the database with data in absence of a front-end.
engine = create_engine("mysql+pymysql://root:@localhost:3306/tvm")
Session = sessionmaker(bind=engine)
session = Session()

with open("knowledge/templates.json") as f:
    data = json.load(f)

# Create categories
name_to_cat = {}
for c in data["categories"]:
    cat = Category(name=c["name"])
    session.add(cat)
    session.flush()  # get ID without full commit
    name_to_cat[c["name"]] = cat.id


# Create subcategories
name_to_sub = {}
for s in data["subcategories"]:
    sub = SubCategory(name=s["name"])
    session.add(sub)
    session.flush()
    name_to_sub[s["name"]] = sub.id

# Create advisory texts
for a in data["advisory_texts"]:
    advisory = AdvisoryText(
        category=name_to_cat[a["category"]],
        sub_category=name_to_sub[a["sub_category"]],
        text=a["text"]
    )
    session.add(advisory)

session.commit()
session.close()
