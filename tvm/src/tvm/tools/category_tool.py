from crewai.tools import BaseTool
from sqlalchemy import create_engine, text
import json
import os


class CategoryTool(BaseTool):
    name: str = "Category Tool"
    description: str = """
    Simple tool to retrieve all available categories and subcategories from the MySQL database.
    Returns a JSON structure with all categories and their associated subcategories.
    """

    def _run(self) -> str:
        """
        Retrieve all categories and their subcategories from the MySQL database
        Only returns categories that have subcategories
        """
        try:
            connection_string = os.getenv("SQL_CONNECTION")
            if not connection_string:
                return "Error: SQL_CONNECTION environment variable not found"

            engine = create_engine(connection_string)

            with engine.connect() as connection:
                # Query to get categories with their subcategories
                query = text("""
                             SELECT c.name  as category_name,
                                    sc.name as subcategory_name
                             FROM categories c
                                      INNER JOIN sub_categories sc ON c.id = sc.category_id
                             ORDER BY c.name, sc.name
                             """)

                result = connection.execute(query)
                rows = result.fetchall()

                # Structure the data
                categories_dict = {}
                for row in rows:
                    category_name = row.category_name
                    subcategory_name = row.subcategory_name

                    if category_name not in categories_dict:
                        categories_dict[category_name] = []

                    # Add subcategory
                    categories_dict[category_name].append(subcategory_name)

                return json.dumps(categories_dict, indent=2, ensure_ascii=False)

        except Exception as e:
            return f"Error retrieving categories from MySQL: {str(e)}"


# Create tool instance
category_tool = CategoryTool()
