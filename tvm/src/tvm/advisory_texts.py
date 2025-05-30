from fastapi import Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from main import app, get_db
from models import *
from authentication import get_current_user
from typing import List


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
