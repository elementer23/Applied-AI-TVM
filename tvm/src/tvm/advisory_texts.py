from fastapi import Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from main import app, get_db
from models import *
from authentication import get_current_user
from typing import List


# Get all categories
@app.get("/categories/", response_model=List[CategoryResponse], tags=["Advisory Texts"])
def read_categories(
        db: Session = Depends(get_db)
):
    """
    Get all categories of risks.
    """
    categories = db.query(Category).all()
    if not categories:
        raise HTTPException(status_code=404, detail="No categories found.")
    return categories

# Get the category with the given ID
@app.get("/categories/{category_id}", response_model=CategoryResponse, tags=["Advisory Texts"])
def read_category(
        category_id: int,
        db: Session = Depends(get_db)
):
    """
    Get a specific category of risk for the given ID.
    """
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")
    return category

# Create a new category
@app.post("/categories/", tags=["Advisory Texts"])
def create_category(
        category_create: CategoryModel,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Create a new category of risk.
    """
    if current_user.role == "admin":
        category = db.get(Category, category_create.name)
        if category:
            raise HTTPException(status_code=400, detail="This category already exists.")
        new_category = Category(name=category_create.name)
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return Response(status_code=201, content=f"Category {new_category.name} successfully created.")
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to create a category.")

# Update the category with the given ID
@app.put("/categories/{category_id}", tags=["Advisory Texts"])
def update_category(
        category_id: int,
        category_update: CategoryModel,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Update a specific category of risk for the given ID.
    """
    if current_user.role == "admin":
        category = db.get(Category, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found.")
        category.name = category_update.name
        db.commit()
        db.refresh(category)
        return Response(status_code=200, content=f"Category {category.name} successfully updated.")
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to update a category.")

# Delete the category with the given ID
@app.delete("/categories/{category_id}", tags=["Advisory Texts"])
def delete_category(
        category_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Delete the category of risk corresponding to the given ID.
    """
    if current_user.role == "admin":
        category = db.get(Category, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found.")
        db.delete(category)
        db.commit()
        db.refresh(category)
        return Response(status_code=204, content=f"Category {category} successfully deleted.")
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to delete a category.")

# Get all subcategories
@app.get("/subcategories/", response_model=List[SubCategoryResponse], tags=["Advisory Texts"])
def read_subcategories(
        db: Session = Depends(get_db)
):
    """
    Gets all subcategories of risk willingness.
    """
    subcategories = db.query(SubCategory).all()
    if not subcategories:
        raise HTTPException(status_code=404, detail="No subcategories found.")
    return subcategories


# Get all subcategories by category ID
@app.get("/categories/{category_id}/subcategories", response_model=List[SubCategoryResponse], tags=["Advisory Texts"])
def read_subcategories_by_category(
        category_id: int,
        db: Session = Depends(get_db)
):
    """
    Gets all subcategories for a specific category ID.
    """
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")

    subcategories = db.query(SubCategory).filter(SubCategory.category_id == category_id).all()
    if not subcategories:
        raise HTTPException(status_code=404, detail="No subcategories found for this category.")

    return subcategories


# Get the subcategory with the given ID
@app.get("/subcategories/{subcategory_id}", response_model=SubCategoryResponse, tags=["Advisory Texts"])
def read_subcategory(
        subcategory_id: int,
        db: Session = Depends(get_db)
):
    """
    Gets a specific subcategory of risk willingness corresponding to the given ID.
    """
    subcategory = db.query(SubCategory).filter(SubCategory.id == subcategory_id).first()
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found.")
    return subcategory

# Create a new subcategory (Currently disabled, as it isn't supposed to be used)
# @app.post("/subcategories/", tags=["Advisory Texts"])
# def create_subcategory(
#         subcategory_create: SubCategoryModel,
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user)
# ):
#     """
#     Creates a new subcategory of risk willingness.
#     """
#     if current_user.role == "admin":
#         subcategory = db.get(SubCategory, subcategory_create.name)
#         if subcategory:
#             raise HTTPException(status_code=400, detail="This subcategory already exists.")
#         new_subcategory = SubCategory(name=subcategory_create.name)
#         db.add(new_subcategory)
#         db.commit()
#         db.refresh(new_subcategory)
#         return Response(status_code=201, content=f"Subcategory {new_subcategory.name} successfully created.")
#     else:
#         raise HTTPException(status_code=403, detail="You are not allowed to create a subcategory.")

# Update the subcategory with the given ID
# @app.put("/subcategories/{subcategory_id}", tags=["Advisory Texts"])
# def update_subcategory(
#         subcategory_id: int,
#         subcategory_update: SubCategoryModel,
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user)
# ):
#     """
#     Update a specific subcategory of risk willingness for the given ID.
#     """
#     if current_user.role == "admin":
#         subcategory = db.get(SubCategory, subcategory_id)
#         if not subcategory:
#             return HTTPException(status_code=404, detail="Subcategory not found.")
#         subcategory.name = subcategory_update.name
#         db.commit()
#         db.refresh(subcategory)
#         return Response(status_code=200, content=f"Subcategory {subcategory.name} successfully updated.")
#     else:
#         raise HTTPException(status_code=403, detail="You are not allowed to update a subcategory.")

# Delete the subcategory with the given ID
# @app.delete("/subcategories/{subcategory_id}", tags=["Advisory Texts"])
# def delete_category(
#         subcategory_id: int,
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user)
# ):
#     """
#     Delete the subcategory of risk willingness corresponding to the given ID.
#     """
#     if current_user.role == "admin":
#         subcategory = db.get(SubCategory, subcategory_id)
#         if not subcategory:
#             return HTTPException(status_code=404, detail="Subcategory not found.")
#         db.delete(subcategory)
#         db.commit()
#         db.refresh(subcategory)
#         return Response(status_code=204, content=f"Subcategory {subcategory} successfully deleted.")
#     else:
#         raise HTTPException(status_code=403, detail="You are not allowed to delete a subcategory.")

# Gets all advice texts
@app.get("/advisorytexts/", response_model=List[AdvisoryTextResponse], tags=["Advisory Texts"])
def read_texts(
        db: Session = Depends(get_db)
):
    """
    Gets all advisory texts templates.
    """
    advisorytexts = db.query(AdvisoryText).all()
    if not advisorytexts:
        raise HTTPException(status_code=404, detail="No advice texts found.")
    return advisorytexts

# Gets the advice text with the given composite ID's
@app.get("/advisorytexts/id={text_id}", response_model=AdvisoryTextResponse, tags=["Advisory Texts"])
def read_text(
        text_id: int,
        db: Session = Depends(get_db)
):
    """
    Gets a specific advisory text template for a given ID.
    """
    advisorytext = db.query(AdvisoryText).filter(AdvisoryText.id == text_id).first()
    if not advisorytext:
        raise HTTPException(status_code=404, detail="Advice text not found.")
    return advisorytext

# Create new advice text
@app.post("/advisorytexts/", tags=["Advisory Texts"])
def create_text(
        advisory_text_create: AdvisoryTextModel,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Creates a new advisory text template.
    """
    if current_user.role == "admin":
        advice = db.query(AdvisoryText).filter(AdvisoryText.text == advisory_text_create.text).first()
        category = db.query(Category).filter(Category.id == advisory_text_create.category_id).first()
        if advice:
            raise HTTPException(status_code=400, detail="This text already exists.")
        new_advice = AdvisoryText(text=advisory_text_create.text, category=category.name, sub_category=advisory_text_create.sub_category)
        new_subcategory = SubCategory(name=advisory_text_create.sub_category, category_id=category.id)
        db.add(new_advice)
        db.add(new_subcategory)
        db.commit()
        db.refresh(new_advice)
        db.refresh(new_subcategory)
        return Response(status_code=201, content=f"AdvisoryText {new_advice.text} successfully created.")
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to create an advisory text.")

# Edits the advice text with the given ID
@app.put("/advisorytexts/id={text_id}", tags=["Advisory Texts"])
def update_text(
        text_id: int,
        advisory_text_update: AdvisoryTextUpdateModel,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Updates an existing advisory text template for a given ID.
    """
    if current_user.role == "admin":
        advisorytext = db.query(AdvisoryText).filter(AdvisoryText.id == text_id).first()
        if not advisorytext:
            raise HTTPException(status_code=404, detail="Advice text not found.")
        advisorytext.text = advisory_text_update.text
        db.commit()
        db.refresh(advisorytext)
        return Response(status_code=200, content=f"Advisory Text {advisorytext.text} successfully updated.")
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to update an advisory text.")

# Deletes the advice text with the given ID
@app.delete("/advisorytexts/id={text_id}", tags=["Advisory Texts"])
def delete_text(
        text_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Deletes a specific advisory text template for a given ID.
    """
    if current_user.role == "admin":
        advisorytext = db.query(AdvisoryText).filter(AdvisoryText.id == text_id).first()
        if not advisorytext:
            raise HTTPException(status_code=404, detail="Advice text not found.")

        category = db.query(Category).filter(Category.name == advisorytext.category).first()
        if category:
            subcategory = db.query(SubCategory).filter(
                SubCategory.name == advisorytext.sub_category,
                SubCategory.category_id == category.id
            ).first()
            if subcategory:
                db.delete(subcategory)

        db.delete(advisorytext)
        db.commit()

        return Response(status_code=200, content=f"Advisory text and corresponding subcategory successfully deleted.")
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to delete an advisory text.")


@app.get("/advisorytexts/subcategory/{subcategory_id}", response_model=AdvisoryTextResponse, tags=["Advisory Texts"])
def read_text_by_subcategory(
        subcategory_id: int,
        db: Session = Depends(get_db)
):
    """
    Gets the advisory text for a specific subcategory ID.
    """
    subcategory = db.query(SubCategory).filter(SubCategory.id == subcategory_id).first()
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found.")

    category = db.get(Category, subcategory.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")

    advisorytext = db.query(AdvisoryText).filter(
        AdvisoryText.category == category.name,
        AdvisoryText.sub_category == subcategory.name
    ).first()

    if not advisorytext:
        raise HTTPException(status_code=404, detail="No advisory text found for this subcategory.")

    return advisorytext
