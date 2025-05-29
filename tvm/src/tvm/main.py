#!/usr/bin/env python
import sys
import warnings
from fastapi import FastAPI
from tvm.models import Base, InputData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.engine.url import make_url
import embedchain.loaders.mysql as mysql_loader_module

_original_init = mysql_loader_module.MySQLLoader.__init__


def patched_init(self, config):
    url = config.get("url")
    if url:
        parsed_url = make_url(url)
        config = {
            "host": parsed_url.host,
            "user": parsed_url.username,
            "password": parsed_url.password,
            "port": parsed_url.port,
            "database": parsed_url.database,
        }

    _original_init(self, config)


mysql_loader_module.MySQLLoader.__init__ = patched_init
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ORIGINS_CALL"),
    allow_methods=["*"],
)

@app.post("/run")
def run(data: InputData, current_user: User = Depends(get_current_user)):
    """
    Run the crew.
    """
    inputs = {
        'input': data.input,
    }

    try:
        result = Tvm().crew().kickoff(inputs=inputs)
        # result = Tvm().crew().kickoff()
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

    return {"output": result.raw}


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