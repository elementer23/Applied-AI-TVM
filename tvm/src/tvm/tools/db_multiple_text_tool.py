from crewai.tools import BaseTool
from sqlalchemy import create_engine, text
import os
from typing import Type, List
from pydantic import BaseModel, Field


class AdvisoryPair(BaseModel):
    category: str = Field(..., description="The category to search for")
    sub_category: str = Field(..., description="The sub_category to search for")


class MultiDatabaseQueryInput(BaseModel):
    pairs: List[AdvisoryPair] = Field(
        ..., description="A list of category/sub_category pairs to retrieve advisory texts for"
    )


class MultiAdvisoryDatabaseTool(BaseTool):
    name: str = "Multi-Advisory Database Tool"
    description: str = (
        "Retrieves multiple advisory text templates from the advisory_texts table "
        "based on a list of category and sub_category pairs."
    )
    args_schema: Type[BaseModel] = MultiDatabaseQueryInput

    def _run(self, pairs: List[dict]) -> str:
        try:
            connection_string = os.getenv("SQL_CONNECTION")
            if not connection_string:
                return "Error: SQL_CONNECTION environment variable not found"

            if not pairs:
                return "No category/sub_category pairs provided."

            engine = create_engine(connection_string)

            # Build dynamic tuple list for SQL
            values_clause = ", ".join([
                f"('{p['category']}', '{p['sub_category']}')" for p in pairs
            ])

            sql = f"""
                SELECT text
                FROM advisory_texts
                WHERE (category, sub_category) IN ({values_clause})
            """

            with engine.connect() as connection:
                result = connection.execute(text(sql))
                rows = result.fetchall()

                if not rows:
                    return "No matching advisory texts found."

                output = [
                    {
                        "text": row.text
                    }
                    for row in rows
                ]

                return str(output)  # You could also return JSON

        except Exception as e:
            return f"Error retrieving advisory texts: {str(e)}"


multi_advisory_db_tool = MultiAdvisoryDatabaseTool()
