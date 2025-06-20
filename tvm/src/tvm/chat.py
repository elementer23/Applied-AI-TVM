from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from main import app
from db import get_db
from models import *
from authentication import get_current_user


@app.get("/conversations", response_model=List[ConversationResponse], tags=["Chat"])
async def get_user_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns all conversations of user
    """
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.created_at.desc()).all()

    if not conversations:
        raise HTTPException(status_code=404, detail="Geen gesprekken gevonden!")

    return conversations


@app.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse], tags=["Chat"])
async def get_conversation_messages(
        conversation_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Returns all messages of conversation
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Gesprek niet gevonden"
        )

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()

    if not messages:
        raise HTTPException(status_code=404, detail="Geen bericht(en) voor dit gesprek")

    return messages


@app.delete("/conversations/{conversation_id}", tags=["Chat"])
async def delete_conversation(
        conversation_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Deletes conversation
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Gesprek niet gevonden"
        )

    db.delete(conversation)
    db.commit()

    return {"message": f"Gesprek {conversation_id} succesvol verwijderd!"}


@app.post("/conversations", response_model=ConversationResponse, tags=["Chat"])
async def create_conversation(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Creates a conversation
    """
    new_conversation = Conversation(
        user_id=current_user.id,
        created_at=datetime.now(timezone.utc)
    )

    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)

    return new_conversation


@app.delete("/conversations", tags=["Chat"])
async def delete_all_conversations(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Deletes all conversations of user
    """
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).all()

    conversation_count = len(conversations)

    if conversation_count == 0:
        return {"message": "Geen gesprekken gevonden"}

    for conversation in conversations:
        db.delete(conversation)

    db.commit()

    return {
        "message": f"Alle {conversation_count} gesprekken succesvol verwijderd!",
    }