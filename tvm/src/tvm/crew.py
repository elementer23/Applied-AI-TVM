from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from tools.db_tool import advisory_db_tool
from tools.category_tool import category_tool


@CrewBase
class Tvm():
    """Tvm crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def reader(self) -> Agent:
        return Agent(
            config=self.agents_config['reader'],
            verbose=True,
            tools=[category_tool]
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config['writer'],
            verbose=True,
        )

    @agent
    def db_specialist(self) -> Agent:
        """Gespecialiseerde agent voor database operaties"""
        return Agent(
            role="Database Specialist",
            goal="Retrieve exact advisory text templates from the advisory_texts table using category and sub_category fields",
            backstory="""You are an expert at database operations. You work with the advisory_texts table which has these exact columns:
            - id (Integer, primary key)
            - category (String 255)
            - sub_category (String 255) 
            - text (Text)

            You always retrieve the actual text content from the database, never SQL statements. You understand this table structure perfectly.""",
            verbose=True,
            tools=[advisory_db_tool],
        )

    def manager(self) -> Agent:
        return Agent(
            config=self.agents_config['manager'],
            verbose=True,
            allow_delegation=True,
        )

    @task
    def get_available_categories(self) -> Task:
        """Simple task to get all available categories and subcategories"""
        return Task(
            description="""
                Use the Category Tool to get all available categories and subcategories from the database.

                This will provide you with the current list of all available categories and their 
                associated subcategories that exist in the system.
                """,
            expected_output="A JSON structure containing all categories and their subcategories from the database.",
            agent=self.reader()
        )
    @task
    def research(self) -> Task:
        return Task(
            description="Read the entire input and extract the necessary data for the writer. Look at {input}",
            expected_output="""Inventaris
            Per category, welk soort advies.
            Eigen risico
            Verzekerd bedrag
            Advies wordt opgevolgd
            Reden dat advies niet wordt opgevolgd indien van toepassing
            Overige context""",
            agent=self.reader(),
            context=[self.get_available_categories()]
        )

    @task
    def decide_template_category(self) -> Task:
        return Task(
            description="""
                Analyze the research context and available categories to determine which advisory 
                text(s) best fits the client's needs.

                Steps:
                1. Review the available categories and subcategories from the previous task
                2. Analyze the research context to understand the client's situation
                3. For every category, decide which sub-category is most appropriate, if any.

                Per category, output EXACTLY this JSON format:
                {
                    "category": "exact_category_name_from_database",
                    "sub_category": "exact_sub_category_name_from_database"
                }

                if you can't find an appropriate sub-category for a category, fill in null instead.

                Make sure the values match exactly what was retrieved from the database.
                """,
            expected_output="A JSON object with 'category' and 'sub_category' fields containing exact database values.",
            agent=self.reader(),
            context=[self.research(), self.get_available_categories()]
        )

    @task
    def fetch_template_from_db(self) -> Task:
        return Task(
            description="""
                Use the Advisory Database Tool to retrieve the ACTUAL advisory text from the advisory_texts table.

                STEP-BY-STEP PROCESS:
                1. Parse the JSON from the previous task to extract category and sub_category
                2. Use the Advisory Database Tool with these EXACT parameters
                3. The tool will query: SELECT text FROM advisory_texts WHERE category = ? AND sub_category = ?
                4. Return the complete text content from the database

                CRITICAL: 
                - You MUST return the actual text content, not SQL statements
                - If no exact match found, the tool will show available alternatives
                - Handle any partial matches appropriately
                - If a sub_category is marked as null, do NOT try to run the tool.
                """,
            expected_output="The complete Dutch advisory text template(s) from the advisory_texts.text column.",
            agent=self.db_specialist(),
            context=[self.decide_template_category()]
        )

    @task
    def fill_in_template(self) -> Task:
        return Task(
            description="""
                Fill in the advisory template(s) with specific information from the research context.

                PROCESS:
                1. Take the template text(s) retrieved from the database
                2. Look for placeholder variables (marked as '[variable_name]') and replace them with the appropriate value.
                3. Areas in parenthesis '()' are a choice, the options being seperated by a '/' character. You must keep ONLY the text before OR after the slash within the area in parenthesis.
                4. Replace placeholders with appropriate values from research context
                5. Ensure proper Dutch grammar and sentence structure
                6. Maintain the original template format and structure

                If the template has no placeholders, adapt the content to be relevant to the specific client situation while keeping the template's core message.

                CRITICAL:
                - If a category is missing a template, fill in: 'Over dit deel is geen advies gegeven.'
                - When encountering an area in parenthesis, ONLY CARE ABOUT THE SLASH when deciding what to keep. You must delete either everything before or after the slash, within parenthesis
                - if [volgt_advies_op] is true, replace with: 'mijn advies opvolgt.'
                - if [volgt_advies_op] is false, replace with: 'niet mijn advies opvolgt, omdat u (reden_niet_opvolgen). Wij willen u erop wijzen dat het accepteren van dit risico mogelijke gevolgen kan hebben voor uw financiële reserves. In het ergste geval zou uw bedrijfscontinuïteit in gevaar kunnen komen. U bent zich hiervan bewust en accepteert deze risico's.'.
                REQUIREMENTS:
                - Mark every template by the category it belongs to.
                - Output must be in Dutch
                - Must use the database template as the foundation
                - All placeholders must be replaced with realistic values
                - Grammar and spelling must be correct
                """,
            expected_output="Een volledig ingevuld Nederlands adviessjabloon, gebaseerd op de database template, met alle variabelen vervangen door relevante informatie uit de research context.",
            agent=self.writer(),
            context=[self.research(), self.fetch_template_from_db()]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Tvm crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            verbose=True,
            manager_agent=self.manager()
        )