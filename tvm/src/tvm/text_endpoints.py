from main import app, get_db
from fastapi import Depends, HTTPException, status, Response
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime


# Get all categories
@app.get("/categories/")
def read_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    if not categories:
        return HTTPException(status_code=404, detail="No categories found.")
    return categories

# Get the category with the given ID
@app.get("/categories/{category_id}")
def read_category(category_id: int, db: Session = Depends(get_db)):
    category = db.get(Category, category_id)
    if not category:
        return HTTPException(status_code=404, detail="Category not found.")
    return category

# Create a new category
@app.post("/categories/")
def create_category(category_name: str, db: Session = Depends(get_db)):
    category = db.get(Category, category_name)
    if category:
        raise HTTPException(status_code=400, detail="This category already exists.")
    new_category = Category(text=category_name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return Response(status_code=201, content=f"Category {new_category.text} successfully created.")

# Update the category with the given ID
@app.put("/categories/{category_id}")
def update_category(category_id: int, category_name: str, db: Session = Depends(get_db)):
    category = db.get(Category, category_id)
    if not category:
        return HTTPException(status_code=404, detail="Category not found.")
    setattr(category, Category.text, category_name)
    db.commit()
    db.refresh(category)
    return Response(status_code=200, content=f"Category {category_name} successfully updated.")

# Delete the category with the given ID
@app.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.get(Category, category_id)
    if not category:
        return HTTPException(status_code=404, detail="Category not found.")
    db.delete(category)
    db.commit()
    db.refresh(category)
    return Response(status_code=204, content=f"Category {category} successfully deleted.")

# Get all subcategories
@app.get("/subcategories/")
def read_subcategories(db: Session = Depends(get_db)):
    subcategories = db.query(SubCategory).all()
    if not subcategories:
        return HTTPException(status_code=404, detail="No subcategories found.")
    return subcategories

# Get the subcategory with the given ID
@app.get("/subcategories/{subcategory_id}")
def read_subcategory(subcategory_id: int, db: Session = Depends(get_db)):
    subcategory = db.query(SubCategory).filter(SubCategory.id == subcategory_id).first()
    if not subcategory:
        return HTTPException(status_code=404, detail="Subcategory not found.")
    return subcategory

# Create a new subcategory
@app.post("/subcategories/")
def create_subcategory(subcategory_name: str, db: Session = Depends(get_db)):
    subcategory = db.query(SubCategory).filter(SubCategory.name == subcategory_name).first()
    if subcategory:
        raise HTTPException(status_code=400, detail="This subcategory already exists.")
    new_subcategory = SubCategory(text=subcategory_name)
    db.add(new_subcategory)
    db.commit()
    db.refresh(new_subcategory)
    return Response(status_code=201,content=f"Subcategory {subcategory_name} successfully created.")

# Update the subcategory with the given ID
@app.put("/subcategories/{subcategory_id}")
def update_subcategory(subcategory_id: int, subcategory_name: str, db: Session = Depends(get_db)):
    subcategory = db.get(SubCategory, subcategory_id)
    if not subcategory:
        return HTTPException(status_code=404, detail="Subcategory not found.")
    setattr(subcategory, SubCategory.text, subcategory_name)
    db.commit()
    db.refresh(subcategory)
    return Response(status_code=200, content=f"Subcategory {subcategory_name} successfully updated.")

# Delete the subcategory with the given ID
@app.delete("/subcategories/{subcategory_id}")
def delete_category(subcategory_id: int, db: Session = Depends(get_db)):
    subcategory = db.get(SubCategory, subcategory_id)
    if not subcategory:
        return HTTPException(status_code=404, detail="Subcategory not found.")
    db.delete(subcategory)
    db.commit()
    db.refresh(subcategory)
    return Response(status_code=204, content=f"Subcategory {subcategory} successfully deleted.")

# Gets all advice texts
@app.get("/advisorytexts/")
def read_texts(db: Session = Depends(get_db)):
    advisorytexts = db.query(AdvisoryText).all()
    if not advisorytexts:
        return HTTPException(status_code=404, detail="No advice texts found.")
    return advisorytexts

# Gets the advice text with the given composite ID's
@app.get("/advisorytexts/catid={category_id}&subid={subcategory_id}")
def read_text(catid: int, subid: int, db: Session = Depends(get_db)):
    advisorytext = db.query(AdvisoryText).filter(AdvisoryText.category_id == catid && AdvisoryText.subcategory_id == subid).first()
    if not advisorytext:
        return HTTPException(status_code=404, detail="Advice text not found.")
    return advisorytext

# Create new advice text
@app.post("/advisorytexts/")
def create_text(advice_text: str, db: Session = Depends(get_db)):
    advice = db.query(AdvisoryText).filter(AdvisoryText.text == advice_text).first()
    if advice:
        raise HTTPException(status_code=400, detail="This text already exists.")
    new_advice = AdvisoryText(text=advice_text)
    db.add(new_advice)
    db.commit()
    db.refresh(new_advice)
    return Response(status_code=201, content=f"AdvisoryText {new_advice.text} successfully created.")

# Edits the advice text with the given ID
@app.put("/advisorytexts/catid={category_id}&subid={subcategory_id}")
def update_text(catid: int, subid: int, advice_text: str, db: Session = Depends(get_db)):
    advisorytext = db.query(AdvisoryText).filter(AdvisoryText.category_id == catid && AdvisoryText.subcategory_id == subid).first()
    if not advisorytext:
        return HTTPException(status_code=404, detail="Advice text not found.")
    setattr(advisorytext, AdvisoryText.text, advice_text)
    db.commit()
    db.refresh(advisorytext)
    return Response(status_code=200, content=f"Advisory Text {advice_text} successfully updated.")

# Deletes the advice text with the given ID
@app.delete("/advisorytexts/catid={category_id}&subid={subcategory_id}")
def delete_text(catid: int, subid: int, db: Session = Depends(get_db)):
    advisorytext = db.query(AdvisoryText).filter(AdvisoryText.category_id == catid && AdvisoryText.subcategory_id == subid).first()
    if not advisorytext:
        return HTTPException(status_code=404, detail="Advice text not found.")
    db.delete(advisorytext)
    db.commit()
    db.refresh(advisorytext)
    return Response(status_code=204, content=f"Subcategory {advisorytext} successfully deleted.")
