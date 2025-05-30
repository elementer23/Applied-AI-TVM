import json
from dotenv import load_dotenv
from models import AdvisoryText
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

# Create advisory texts directly with category and subcategory names
for a in data["advisory_texts"]:
    advisory = AdvisoryText(
        category=a["category"],
        sub_category=a["sub_category"],
        text=a["text"]
    )
    session.add(advisory)

session.commit()
session.close()