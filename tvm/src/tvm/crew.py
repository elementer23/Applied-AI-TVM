import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, llm
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from tools.db_tool import advisory_db_tool
from tools.category_tool import category_tool


@CrewBase
class Tvm():
    """Tvm crew"""

    OPEN_API_BASE = os.environ.get("OPENAI_API_BASE")
    OPEN_API_KEY = os.environ.get("OPENAI_API_KEY")
    DEFAULT_LLM = os.environ.get("DEFAULT_LLM")
    REASONING_LLM = os.environ.get("REASONING_LLM")
    agents: List[BaseAgent]
    tasks: List[Task]

    @llm
    def default_crew_llm(self) -> LLM:
        return LLM(
            model=self.DEFAULT_LLM,
            temperature=0.5,
            api_base=self.OPEN_API_BASE,
            api_key=self.OPEN_API_KEY
        )

    @llm
    def reasoning_llm(self) -> LLM:
        return LLM(
            model=self.REASONING_LLM,
            temperature=0.5,
            api_base=self.OPEN_API_BASE,
            api_key=self.OPEN_API_KEY
        )

    @agent
    def reader(self) -> Agent:
        return Agent(
            config=self.agents_config['reader'],
            verbose=True,
            llm=self.reasoning_llm(),
            tools=[category_tool],
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config['writer'],
            verbose=True,
            llm=self.reasoning_llm(),
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
            llm=self.default_crew_llm(),
            tools=[advisory_db_tool],
        )

    def manager(self) -> Agent:
        return Agent(
            config=self.agents_config['manager'],
            verbose=True,
            allow_delegation=True,
            llm=self.reasoning_llm()
        )

    @task
    def research(self) -> Task:
        return Task(
            config=self.tasks_config['research'],
            agent=self.reader()
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
    def decide_template_category(self) -> Task:
        return Task(
            description="""
                Analyze the research context and available categories to determine which advisory 
                text best fits the client's needs.

                Steps:
                1. Review the available categories and subcategories from the previous task
                2. Analyze the research context to understand the client's situation
                3. Choose the most appropriate category and subcategory combination

                Output EXACTLY this JSON format:
                {
                    "category": "exact_category_name_from_database",
                    "sub_category": "exact_sub_category_name_from_database"
                }

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
                """,
            expected_output="The complete Dutch advisory text template from the advisory_texts.text column.",
            agent=self.db_specialist(),
            context=[self.decide_template_category()]
        )

    @task
    def analyze_template_requirements(self) -> Task:
        """Analyze the template for missing options and placeholders that cannot be determined"""
        return Task(
            description="""
                Analyze the retrieved template to identify any placeholders or choice options that cannot be clearly determined from: {input}

                ANALYSIS PROCESS:
                1. Examine the template text for all placeholders marked as '[variable_name]'
                2. Look for choice areas in parenthesis '()' with options separated by '/'
                3. Cross-reference with the research context to see what can be definitively filled in
                4. Apply specific rules for common placeholders to minimize false positives
                5. Only mark as missing if truly ambiguous after applying specific placeholder rules

                SPECIFIC PLACEHOLDER RULES (to minimize false positives):
                - [beleid_klant]: Look for any mention of risk amounts (euros) or risk minimization approach - if found, can be filled
                - [eigen_risico]: Look for any mention of deductible amounts (euros) - there might be multiple so mention them all
                - [verzekering_soort]: Look for "WA", "wettelijke aansprakelijkheid" or similar liability insurance terms - if found, can be filled
                - [basis_verzekerd_bedrag]: Look for any monetary amounts mentioned (material damage, person damage, etc.) - if found, can be filled
                - [volgt_advies_op]: Look for acceptation or rejection of advice, this is always "U heeft aangegeven dat u mijn advies opvolgt." or "U heeft aangegeven dat u mijn advies niet opvolgt, omdat ...". If not clear or its simply not there, mark as missing

                WHAT TO IDENTIFY AS MISSING:
                - Template placeholders where NO relevant information exists in context (after applying specific rules)
                - Choice areas where the correct option cannot be determined even with flexible interpretation
                - Any template variable that requires a specific choice but context provides no guidance whatsoever
                - Boolean choices where there's absolutely no indication of direction

                STRICT RULE - MINIMIZE FALSE POSITIVES:
                - Apply the specific placeholder rules first before marking as missing
                - Look for partial matches or related information that could fill placeholders
                - If research context has ANY relevant information for a placeholder, mark as "can be filled"
                - Only mark as missing if there's truly NO relevant information available
                - Be generous in interpretation - if there's a reasonable connection, don't mark as missing

                WHAT NOT TO IDENTIFY AS MISSING:
                - Standard client details that can use generic terms ("de klant", "uw bedrijf")
                - Information that has reasonable defaults in professional contexts
                - Placeholders where context provides related/relevant information (even if not exact match)

                OUTPUT FORMAT:
                {
                    "missing_template_options": [
                        {
                            "placeholder": "[placeholder_name]",
                            "description": "wat exact onduidelijk is - welke keuze moet gemaakt worden",
                            "options": "beschrijf de beschikbare opties indien van toepassing"
                        }
                    ],
                    "can_proceed": true,
                    "notes": "Extra opmerkingen over template analyse"
                }
                """,
            expected_output="Een JSON analyse van alleen de werkelijk onduidelijke template opties waar absoluut geen relevante informatie voor beschikbaar is.",
            agent=self.reader(),
            context=[self.research(), self.fetch_template_from_db()]
        )

    @task
    def fill_in_template(self) -> Task:
        return Task(
            description="""
                Fill in the advisory template with specific information from the research context.

                PROCESS:
                1. Take the template text retrieved from the database
                2. Review the template analysis for any missing template options
                3. Look for placeholder variables (marked as '[variable_name]') and replace them with appropriate values
                4. Areas in parenthesis '()' are choices with options separated by '/'. You must keep ONLY the text before OR after the slash
                5. Replace placeholders ONLY with information that is explicitly available from research context
                6. For missing client information, use generic professional terms like "de klant", "uw bedrijf", "de situatie"
                7. For template options marked as missing in the analysis, use: [ONTBREEKT: specifieke beschrijving uit analyse]
                8. DO NOT make assumptions about choices - follow the analysis strictly
                9. Ensure proper Dutch grammar and sentence structure
                10. Maintain the original template format and structure

                STRICT RULE - NO ASSUMPTIONS:
                - If the analysis marked something as missing, mark it as [ONTBREEKT: ...] 
                - Do not guess or assume what choice should be made
                - Only fill in what is explicitly clear from the context
                - When in doubt, mark as missing rather than assume

                HANDLING MISSING TEMPLATE OPTIONS:
                - Use the exact descriptions from the template analysis
                - At the end, add "ONTBREKENDE TEMPLATE OPTIES:" section if analysis found missing options
                - List each missing option with its description and available choices

                CRITICAL TEMPLATE RULES:
                - Parenthesis areas: keep ONLY text before OR after the slash, delete the other option and parentheses
                - [volgt_advies_op] true: replace with 'mijn advies opvolgt.'
                - [volgt_advies_op] false: replace with 'niet mijn advies opvolgt, omdat u (reden_niet_opvolgen). Wij willen u erop wijzen dat het accepteren van dit risico mogelijke gevolgen kan hebben voor uw financiële reserves. In het ergste geval zou uw bedrijfscontinuïteit in gevaar kunnen komen. U bent zich hiervan bewust en accepteert deze risico's.'
                - If [volgt_advies_op] is unclear from context, mark as [ONTBREEKT: keuze wel/niet advies opvolgen]

                REQUIREMENTS:
                - Output must be in Dutch
                - Must use the database template as the foundation
                - Follow template analysis recommendations strictly
                - No assumptions about unclear choices
                - Professional language throughout
                - Grammar and spelling must be correct
                """,
            expected_output="Een Nederlands adviessjabloon waarbij alleen expliciete informatie is ingevuld en onduidelijke template keuzes zijn gemarkeerd als [ONTBREEKT: ...] met onderaan een overzicht van wat nog bepaald moet worden.",
            agent=self.writer(),
            context=[self.research(), self.fetch_template_from_db(), self.analyze_template_requirements()]
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