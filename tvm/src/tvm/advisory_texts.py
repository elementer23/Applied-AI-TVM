from fastapi import Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from main import app, get_db
from models import *
from authentication import get_current_user
from typing import List


# Get all categories
@app.get("/categories/")
def read_categories(db: Session = Depends(get_db)):
    """
    Get all categories of risks.
    """
    categories = db.query(Category).all()
    if not categories:
        return HTTPException(status_code=404, detail="No categories found.")
    return categories

# Get the category with the given ID
@app.get("/categories/{category_id}")
def read_category(category_id: int, db: Session = Depends(get_db)):
    """
    Get a specific category of risk for the given ID.
    """
    category = db.get(Category, category_id)
    if not category:
        return HTTPException(status_code=404, detail="Category not found.")
    return category

# Create a new category
@app.post("/categories/")
def create_category(category_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new category of risk.
    """
    if current_user.role == "admin":
        category = db.get(Category, category_name)
        if category:
            raise HTTPException(status_code=400, detail="This category already exists.")
        new_category = Category(name=category_name)
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return Response(status_code=201, content=f"Category {new_category.name} successfully created.")
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to create a category.")

# Update the category with the given ID
@app.put("/categories/{category_id}")
def update_category(category_id: int, category_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update a specific category of risk for the given ID.
    """
    if current_user.role == "admin":
        category = db.get(Category, category_id)
        if not category:
            return HTTPException(status_code=404, detail="Category not found.")
        setattr(category, Category.name, category_name)
        db.commit()
        db.refresh(category)
        return Response(status_code=200, content=f"Category {category_name} successfully updated.")
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to update a category.")

# Delete the category with the given ID
@app.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete the category of risk corresponding to the given ID.
    """
    if current_user.role == "admin":
        category = db.get(Category, category_id)
        if not category:
            return HTTPException(status_code=404, detail="Category not found.")
        db.delete(category)
        db.commit()
        db.refresh(category)
        return Response(status_code=204, content=f"Category {category} successfully deleted.")
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to delete a category.")

# Get all subcategories
@app.get("/subcategories/")
def read_subcategories(db: Session = Depends(get_db)):
    """
    Gets all subcategories of risk willingness.
    """
    subcategories = db.query(SubCategory).all()
    if not subcategories:
        return HTTPException(status_code=404, detail="No subcategories found.")
    return subcategories

# Get the subcategory with the given ID
@app.get("/subcategories/{subcategory_id}")
def read_subcategory(subcategory_id: int, db: Session = Depends(get_db)):
    """
    Gets a specific subcategory of risk willingness corresponding to the given ID.
    """
    subcategory = db.query(SubCategory).filter(SubCategory.id == subcategory_id).first()
    if not subcategory:
        return HTTPException(status_code=404, detail="Subcategory not found.")
    return subcategory

# Create a new subcategory
@app.post("/subcategories/")
def create_subcategory(subcategory_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Creates a new subcategory of risk willingness.
    """
    if current_user.role == "admin":
        subcategory = db.query(SubCategory).filter(SubCategory.name == subcategory_name).first()
        if subcategory:
            raise HTTPException(status_code=400, detail="This subcategory already exists.")
        new_subcategory = SubCategory(name=subcategory_name)
        db.add(new_subcategory)
        db.commit()
        db.refresh(new_subcategory)
        return Response(status_code=201, content=f"Subcategory {new_subcategory.name} successfully created.")
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to create a subcategory.")

# Update the subcategory with the given ID
@app.put("/subcategories/{subcategory_id}")
def update_subcategory(subcategory_id: int, subcategory_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update a specific subcategory of risk willingness for the given ID.
    """
    if current_user.role == "admin":
        subcategory = db.get(SubCategory, subcategory_id)
        if not subcategory:
            return HTTPException(status_code=404, detail="Subcategory not found.")
        setattr(subcategory, SubCategory.name, subcategory_name)
        db.commit()
        db.refresh(subcategory)
        return Response(status_code=200, content=f"Subcategory {subcategory_name} successfully updated.")
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to update a subcategory.")

# Delete the subcategory with the given ID
@app.delete("/subcategories/{subcategory_id}")
def delete_category(subcategory_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete the subcategory of risk willingness corresponding to the given ID.
    """
    if current_user.role == "admin":
        subcategory = db.get(SubCategory, subcategory_id)
        if not subcategory:
            return HTTPException(status_code=404, detail="Subcategory not found.")
        db.delete(subcategory)
        db.commit()
        db.refresh(subcategory)
        return Response(status_code=204, content=f"Subcategory {subcategory} successfully deleted.")
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to delete a subcategory.")

# Gets all advice texts
@app.get("/advisorytexts/", response_model=List[AdvisoryTextResponse], tags=["Advisory Texts"])
def read_texts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Gets all advisory texts templates.
    """
    advisorytexts = db.query(AdvisoryText).all()
    if not advisorytexts:
        return HTTPException(status_code=404, detail="No advice texts found.")
    return advisorytexts

# Gets the advice text with the given composite ID's
@app.get("/advisorytexts/id={text_id}", response_model=AdvisoryTextResponse, tags=["Advisory Texts"])
def read_text(text_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Gets a specific advisory text template for a given ID.
    """
    advisorytext = db.query(AdvisoryText).filter(AdvisoryText.id == text_id).first()
    if not advisorytext:
        return HTTPException(status_code=404, detail="Advice text not found.")
    return advisorytext

# Create new advice text
@app.post("/advisorytexts/", tags=["Advisory Texts"])
def create_text(advice_text: str, category: str, subcategory: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Creates a new advisory text template.
    """
    if current_user.role == "admin":
        advice = db.query(AdvisoryText).filter(AdvisoryText.text == advice_text).first()
        if advice:
            raise HTTPException(status_code=400, detail="This text already exists.")
        new_advice = AdvisoryText(text=advice_text, category=category, sub_category=subcategory)
        db.add(new_advice)
        db.commit()
        db.refresh(new_advice)
        return Response(status_code=201, content=f"AdvisoryText {new_advice.text} successfully created.")
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to create an advisory text.")

# Edits the advice text with the given ID
@app.put("/advisorytexts/id={text_id}", tags=["Advisory Texts"])
def update_text(text_id: int, advice_text: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Updates an existing advisory text template for a given ID.
    """
    if current_user.role == "admin":
        advisorytext = db.query(AdvisoryText).filter(AdvisoryText.id == text_id).first()
        if not advisorytext:
            return HTTPException(status_code=404, detail="Advice text not found.")
        setattr(advisorytext, AdvisoryText.text, advice_text)
        db.commit()
        db.refresh(advisorytext)
        return Response(status_code=200, content=f"Advisory Text {advice_text} successfully updated.")
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to update an advisory text.")

# Deletes the advice text with the given ID
@app.delete("/advisorytexts/id={text_id}", tags=["Advisory Texts"])
def delete_text(text_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Deletes a specific advisory text template for a given ID.
    """
    if current_user.role == "admin":
        advisorytext = db.query(AdvisoryText).filter(AdvisoryText.id == text_id).first()
        if not advisorytext:
            return HTTPException(status_code=404, detail="Advice text not found.")
        db.delete(advisorytext)
        db.commit()
        db.refresh(advisorytext)
        return Response(status_code=204, content=f"Subcategory {advisorytext} successfully deleted.")
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to delete an advisory text.")
