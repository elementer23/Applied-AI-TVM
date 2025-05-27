#!/usr/bin/env python
import sys
import warnings
from fastapi import FastAPI
from tvm.models import Base, InputData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from starlette.middleware.cors import CORSMiddleware

from crew import Tvm

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

app = FastAPI()

SQLALCHEMY_DATABASE_URL = "sqlite:///./db.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from authentication import *
from chat import *

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ORIGINS_CALL"),
    allow_methods=["*"],
)


@app.post("/run")
def run(data: InputData, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Run the crew.
    """
    inputs = {
        'input': data.input,
    }

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
            created_at=datetime.utcnow()
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
        created_at=datetime.utcnow()
    )
    db.add(user_message)

    # Add the AI response to the conversation
    ai_message = Message(
        conversation_id=conversation.id,
        content=ai_response,
        is_user_message=False,
        created_at=datetime.utcnow()
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


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        Tvm().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Tvm().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        Tvm().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")