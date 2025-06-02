import json
from dotenv import load_dotenv
from models import AdvisoryText, Category, SubCategory
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

# uses knowledge/templates.json to seed the database with data in absence of a front-end.

load_dotenv(dotenv_path="../../.env")
engine = create_engine(os.getenv("SQL_CONNECTION"))
Session = sessionmaker(bind=engine)
session = Session()

with open("knowledge/templates.json") as f:
    data = json.load(f)

# Create categories
category_objects = {}
for cat in data["categories"]:
    # Check if category already exists to avoid duplicates
    existing_category = session.query(Category).filter_by(name=cat["name"]).first()
    if not existing_category:
        category = Category(name=cat["name"])
        session.add(category)
        category_objects[cat["name"]] = category
    else:
        category_objects[cat["name"]] = existing_category

session.commit()

# Create subcategories for each category
for cat_name, category_obj in category_objects.items():
    for subcat in data["subcategories"]:
        # Check if this specific subcategory already exists for this category
        existing_subcategory = session.query(SubCategory).filter_by(
            name=subcat["name"],
            category=category_obj.id
        ).first()
        if not existing_subcategory:
            subcategory = SubCategory(
                name=subcat["name"],
                category=category_obj.id
            )
            session.add(subcategory)

# Create advisory texts directly with category and subcategory names
for a in data["advisory_texts"]:
    # Check if advisory text already exists
    existing_advisory = session.query(AdvisoryText).filter_by(
        category=a["category"],
        sub_category=a["sub_category"]
    ).first()
    if not existing_advisory:
        advisory = AdvisoryText(
            category=a["category"],
            sub_category=a["sub_category"],
            text=a["text"]
        )
        session.add(advisory)

session.commit()
session.close()