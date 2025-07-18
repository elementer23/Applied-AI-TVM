#!/usr/bin/env python
import sys
import warnings
from fastapi import FastAPI
from db import get_db
from filter import filter_service
from filter_input_util import input_filter
from starlette.middleware.cors import CORSMiddleware
from crew import Tvm

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

tags_metadata = [
    {
        "name": "Authentication",
        "description": "All authentication endpoints",
    },
    {
        "name": "Chat",
        "description": "All endpoints for managing conversations and messages",
    },
    {
        "name": "Advisory Texts",
        "description": "All endpoints for managing the advisory text templates."
    }
]

app = FastAPI(openapi_tags=tags_metadata,
              title="TVM AI",
              version="0.0.1", )

from authentication import *
from chat import *
from advisory_texts import *

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ORIGINS_CALL"),
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)


@app.post("/run", tags=["Chat"])
def run(
        data: InputData,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Send a message and run the crew.
    """

    filtered_input = input_filter.filter_input(data.input)
    inputs = {
        "input": filtered_input,
    }

    # Check if the input is insurance related using the filter service
    is_insurance_related = filter_service.screen_query(data.input)

    if not is_insurance_related:
        ai_response = "Sorry, ik kan alleen helpen bij het omzetten van adviesteksten. Stuur alstublieft alleen een adviestekst die u wilt omzetten."
    else:
        try:
            result = Tvm().crew().kickoff(inputs=inputs)
            ai_response = result.raw
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")

    conversation = None
    conversation_created = False

    # If conversation is specified in input
    if data.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == data.conversation_id,
            Conversation.user_id == current_user.id
        ).first()

    # If no conversation was found, create a new one
    if not conversation:
        conversation = Conversation(
            user_id=current_user.id,
            created_at=datetime.now(timezone.utc)
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        conversation_created = True

    # Add the user message to the conversation
    user_message = Message(
        conversation_id=conversation.id,
        content=data.input,
        is_user_message=True,
        created_at=datetime.now(timezone.utc)
    )
    db.add(user_message)

    # Add the AI response to the conversation
    ai_message = Message(
        conversation_id=conversation.id,
        content=ai_response,
        is_user_message=False,
        created_at=datetime.now(timezone.utc)
    )
    db.add(ai_message)

    db.commit()
    db.refresh(user_message)
    db.refresh(ai_message)

    return {
        "output": ai_response,
        "conversation_id": conversation.id,
        "conversation_created": conversation_created,
        "user_message_id": user_message.id,
        "ai_message_id": ai_message.id
    }
