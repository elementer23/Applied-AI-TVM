from crewai.tools import BaseTool
import mysql.connector
from mysql.connector import Error
import os
from typing import Type, Optional
from pydantic import BaseModel, Field
from urllib.parse import urlparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseQueryInput(BaseModel):
    """Input schema for database query."""
    category: str = Field(..., description="The category to search for (e.g., damage_to_third_parties)")
    sub_category: str = Field(..., description="The sub_category to search for (e.g., minrisk)")


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

        Args:
            category: The main category
            sub_category: The subcategory

        Returns:
            The advisory text content or error message
        """
        connection = None
        cursor = None

        try:
            logger.info(f"Searching advisory_texts table for category: '{category}', sub_category: '{sub_category}'")

            # Get database connection
            connection = self._get_database_connection()
            cursor = connection.cursor(dictionary=True)

            # Execute query with exact match
            query = """
                    SELECT id, category, sub_category, text
                    FROM advisory_texts
                    WHERE category = %s \
                      AND sub_category = %s LIMIT 1 \
                    """

            cursor.execute(query, (category, sub_category))
            result = cursor.fetchone()

            if result:
                logger.info(f"Found advisory text with ID: {result['id']}")
                logger.info(f"Text length: {len(result['text'])} characters")
                return result['text']
            else:
                # Try with partial matching if exact match fails
                logger.warning(f"No exact match found for '{category}' + '{sub_category}', trying alternatives...")
                return self._try_find_alternatives(cursor, category, sub_category)

        except Error as e:
            error_msg = f"MySQL Database error: {str(e)}"
            logger.error(error_msg)
            return error_msg

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return error_msg

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
                logger.info("Database connection closed")

    def _try_find_alternatives(self, cursor, category: str, sub_category: str) -> str:
        """Try to find alternatives if exact match fails."""
        try:
            # First: Check what categories actually exist
            logger.info("Checking available categories and subcategories...")

            query_available = """
                              SELECT DISTINCT category, sub_category, id
                              FROM advisory_texts
                              ORDER BY category, sub_category \
                              """

            cursor.execute(query_available)
            available_options = cursor.fetchall()

            if not available_options:
                return "No advisory texts found in database. The advisory_texts table appears to be empty."

            # Log available options for debugging
            logger.info(f"Found {len(available_options)} available combinations")
            for option in available_options[:5]:  # Log first 5
                logger.info(f"Available: category='{option['category']}', sub_category='{option['sub_category']}'")

            # Try partial category match
            category_matches = [opt for opt in available_options if category.lower() in opt['category'].lower()]
            if category_matches:
                logger.info(f"Found {len(category_matches)} partial category matches")
                best_match = category_matches[0]

                # Get the text for the best match
                query_text = "SELECT text FROM advisory_texts WHERE id = %s"
                cursor.execute(query_text, (best_match['id'],))
                text_result = cursor.fetchone()

                if text_result:
                    return f"CLOSE MATCH FOUND (requested: '{category}'/'{sub_category}'):\nActual: '{best_match['category']}'/'{best_match['sub_category']}'\n\nText:\n{text_result['text']}"

            # Try subcategory match
            subcategory_matches = [opt for opt in available_options if
                                   sub_category.lower() in opt['sub_category'].lower()]
            if subcategory_matches:
                logger.info(f"Found {len(subcategory_matches)} partial subcategory matches")
                best_match = subcategory_matches[0]

                # Get the text for the best match
                query_text = "SELECT text FROM advisory_texts WHERE id = %s"
                cursor.execute(query_text, (best_match['id'],))
                text_result = cursor.fetchone()

                if text_result:
                    return f"SUBCATEGORY MATCH FOUND (requested: '{category}'/'{sub_category}'):\nActual: '{best_match['category']}'/'{best_match['sub_category']}'\n\nText:\n{text_result['text']}"

            # Return available options
            options_text = f"No match found for category: '{category}', sub_category: '{sub_category}'.\n\nAvailable options in database:\n"
            for option in available_options:
                options_text += f"• Category: '{option['category']}', Sub-category: '{option['sub_category']}'\n"

            return options_text

        except Exception as e:
            return f"Error while searching for alternatives: {str(e)}"

    def _get_database_connection(self):
        """Create and return database connection."""
        db_uri = os.getenv("SQL_CONNECTION")

        if not db_uri:
            raise ValueError("SQL_CONNECTION environment variable not found")

        # Parse the database URI
        connection_params = self._parse_db_uri(db_uri)

        logger.info(f"Connecting to database: {connection_params.get('host')}:{connection_params.get('port')}")

        # Create connection with better error handling
        try:
            connection = mysql.connector.connect(**connection_params)

            if not connection.is_connected():
                raise Error("Failed to establish database connection")

            # Test the connection with a simple query
            test_cursor = connection.cursor()
            test_cursor.execute("SELECT COUNT(*) FROM advisory_texts")
            count = test_cursor.fetchone()[0]
            test_cursor.close()

            logger.info(f"Successfully connected. Found {count} records in advisory_texts table")
            return connection

        except Error as e:
            logger.error(f"MySQL connection failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected connection error: {str(e)}")
            raise

    def _parse_db_uri(self, uri: str) -> dict:
        """
        Parse database URI into connection parameters.
        """
        try:
            parsed = urlparse(uri)

            if not parsed.scheme.startswith('mysql'):
                raise ValueError(f"Unsupported database scheme: {parsed.scheme}")

            connection_params = {
                'host': parsed.hostname or 'localhost',
                'port': parsed.port or 3306,
                'user': parsed.username,
                'password': parsed.password,
                'database': parsed.path.lstrip('/') if parsed.path else None,
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci',
                'autocommit': True,
                'raise_on_warnings': False,  # Changed to False for better compatibility
                'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'
            }

            # Remove None values
            connection_params = {k: v for k, v in connection_params.items() if v is not None}

            # Validate required params
            if not connection_params.get('database'):
                raise ValueError("Database name is required in connection URI")

            logger.info(f"Parsed connection for database: {connection_params['database']}")
            return connection_params

        except Exception as e:
            raise ValueError(f"Invalid database URI format: {str(e)}")


advisory_db_tool = CustomAdvisoryDatabaseTool()