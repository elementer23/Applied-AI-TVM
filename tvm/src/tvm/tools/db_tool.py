from crewai.tools import BaseTool
from sqlalchemy import create_engine, text
import os
from typing import Type
from pydantic import BaseModel, Field


class DatabaseQueryInput(BaseModel):
    """
    Input schema for database query.
    """
    category: str = Field(..., description="The category to search for")
    sub_category: str = Field(..., description="The sub_category to search for")


class CustomAdvisoryDatabaseTool(BaseTool):
    name: str = "Advisory Database Tool"
    description: str = (
        "Retrieves advisory text templates from the advisory_texts table based on category and sub_category. "
        "Returns the actual text content from the database."
    )
    args_schema: Type[BaseModel] = DatabaseQueryInput

    def _run(self, category: str, sub_category: str) -> str:
        """
        Execute database query to retrieve advisory text.
        """
        try:
            connection_string = os.getenv("SQL_CONNECTION")
            if not connection_string:
                return "Error: SQL_CONNECTION environment variable not found"

            engine = create_engine(connection_string)

            with engine.connect() as connection:
                query = text("""
                             SELECT text
                             FROM advisory_texts
                             WHERE category = :category
                               AND sub_category = :sub_category LIMIT 1
                             """)

                result = connection.execute(query, {
                    "category": category,
                    "sub_category": sub_category
                })
                row = result.fetchone()

                if row:
                    return row.text
                else:
                    return f"No advisory text found for category: '{category}', sub_category: '{sub_category}'"

        except Exception as e:
            return f"Error retrieving advisory text: {str(e)}"


advisory_db_tool = CustomAdvisoryDatabaseTool()