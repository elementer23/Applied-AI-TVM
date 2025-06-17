from fastapi import Depends, HTTPException, Response
from sqlalchemy.orm import Session
from main import app
from db import get_db
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
        raise HTTPException(status_code=404, detail="Geen categorieën gevonden.")
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
        raise HTTPException(status_code=404, detail="Categorie niet gevonden.")
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
        category = db.query(Category).filter_by(name=category_create.name).first()
        if category:
            raise HTTPException(status_code=400, detail="Deze categorie bestaat al.")
        new_category = Category(name=category_create.name)
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return Response(status_code=201, content=f"Categorie {new_category.name} succesvol gecreëerd.")
    else:
        raise HTTPException(status_code=403, detail="U bent niet gerechtigd om een categorie te creëren.")


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
            raise HTTPException(status_code=404, detail="Categorie niet gevonden.")
        old_category_name = category.name
        category.name  = category_update.name

        db.query(AdvisoryText).filter(AdvisoryText.category == old_category_name).update({"category": category.name})
        db.commit()
        db.refresh(category)
        return Response(status_code=200, content=f"Categorie {category.name} succesvol geüpdatet.")
    else:
        raise HTTPException(status_code=403, detail="U bent niet gerechtigd om een categorie te updaten.")


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
            raise HTTPException(status_code=404, detail="Categorie niet gevonden.")
        db.query(SubCategory).filter(SubCategory.category_id == category_id).delete()
        db.query(AdvisoryText).filter(AdvisoryText.category == category.name).delete()
        db.delete(category)
        db.commit()
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=403, detail="U bent niet gerechtigd om een categorie te verwijderen.")


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
        raise HTTPException(status_code=404, detail="Geen subcategorieën gevonden.")
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
        raise HTTPException(status_code=404, detail="Categorie niet gevonden.")

    subcategories = db.query(SubCategory).filter(SubCategory.category_id == category_id).all()
    if not subcategories:
        raise HTTPException(status_code=404, detail="Geen subcategorieën voor deze categorie gevonden.")

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
        raise HTTPException(status_code=404, detail="Subcategorie niet gevonden.")
    return subcategory


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
        raise HTTPException(status_code=404, detail="Geen adviesteksten gevonden.")
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
        raise HTTPException(status_code=404, detail="Adviestekst niet gevonden.")
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
        sub_category = db.query(SubCategory).filter(
            SubCategory.name == advisory_text_create.sub_category,
            SubCategory.category_id == advisory_text_create.category_id
        ).first()
        if advice:
            raise HTTPException(status_code=400, detail="De gegeven tekst bestaat al.")
        if sub_category:
            raise HTTPException(status_code=400, detail="De gegeven subcategorie bestaat al voor deze categorie.")
        new_advice = AdvisoryText(text=advisory_text_create.text, category=category.name, sub_category=advisory_text_create.sub_category)
        new_subcategory = SubCategory(name=advisory_text_create.sub_category, category_id=category.id)
        db.add(new_advice)
        db.add(new_subcategory)
        db.commit()
        db.refresh(new_advice)
        db.refresh(new_subcategory)
        return Response(status_code=201, content=f"Adviestekst {new_advice.text} succesvol gecreëerd.")
    else:
        raise HTTPException(status_code=403, detail="U bent niet gerechtigd om een adviestekst te creëren.")


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
            raise HTTPException(status_code=404, detail="Adviestekst niet gevonden.")
        advisorytext.text = advisory_text_update.text
        db.commit()
        db.refresh(advisorytext)
        return Response(status_code=200, content=f"Adviestekst {advisorytext.text} is succesvol geüpdatet.")
    else:
        raise HTTPException(status_code=403, detail="U bent niet gerechtigd om een adviestekst te updaten.")


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
            raise HTTPException(status_code=404, detail="Adviestekst niet gevonden.")
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

        return Response(status_code=204)
    else:
        raise HTTPException(status_code=403, detail="U bent niet gerechtigd om een adviestekst te verwijderen.")


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
        raise HTTPException(status_code=404, detail="Subcategorie niet gevonden.")

    category = db.get(Category, subcategory.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categorie niet gevonden.")

    advisorytext = db.query(AdvisoryText).filter(
        AdvisoryText.category == category.name,
        AdvisoryText.sub_category == subcategory.name
    ).first()

    if not advisorytext:
        raise HTTPException(status_code=404, detail="Geen adviestekst gevonden voor deze subcategorie.")

    return advisorytext
