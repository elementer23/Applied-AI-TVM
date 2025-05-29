from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Dict, Any
from crewai_tools import MySQLSearchTool

sql_search = MySQLSearchTool(
    db_uri = 'mysql://root:admin@localhost:3306/tvm',
    table_name='advisory_texts'
)


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
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config['writer'],
            verbose=True,
            tools=[sql_search],
        )

    @task
    def research(self) -> Task:
        return Task(
            config=self.tasks_config['research'],
            agent=self.reader()
        )

    # @task
    # def decide_and_execute_rewrite(self) -> Task:
    #
    #     rewrite_configs = {
    #         'minrisk_damage_to_third_parties': self.tasks_config['rewrite_task_minrisk_damage_to_third_parties'],
    #         'risk_in_euros_damage_to_third_parties': self.tasks_config[
    #             'rewrite_task_risk_in_euros_damage_to_third_parties'],
    #         'deviate_from_identification_damage_to_third_parties': self.tasks_config[
    #             'rewrite_task_deviate_from_identification_damage_to_third_parties'],
    #         'identify_by_risk_damage_to_third_parties': self.tasks_config[
    #             'rewrite_task_identify_by_risk_damage_to_third_parties'],
    #         'minrisk_damage_by_standstill': self.tasks_config['rewrite_task_minrisk_damage_by_standstill'],
    #         'risk_in_euros_damage_by_standstill': self.tasks_config['rewrite_task_risk_in_euros_damage_by_standstill'],
    #         'deviate_from_identification_damage_by_standstill': self.tasks_config[
    #             'rewrite_task_deviate_from_identification_damage_by_standstill'],
    #         'identify_by_risk_damage_by_standstill': self.tasks_config[
    #             'rewrite_task_identify_by_risk_damage_by_standstill'],
    #         'minrisk_loss_of_personal_items': self.tasks_config['rewrite_task_minrisk_loss_of_personal_items'],
    #         'risk_in_euros_loss_of_personal_items': self.tasks_config[
    #             'rewrite_task_risk_in_euros_loss_of_personal_items'],
    #         'deviate_from_identification_loss_of_personal_items': self.tasks_config[
    #             'rewrite_task_deviate_from_identification_loss_of_personal_items'],
    #         'identify_by_risk_loss_of_personal_items': self.tasks_config[
    #             'rewrite_task_identify_by_risk_loss_of_personal_items'],
    #         'minrisk_damage_to_passengers': self.tasks_config['rewrite_task_minrisk_damage_to_passengers'],
    #         'risk_in_euros_damage_to_passengers': self.tasks_config['rewrite_task_risk_in_euros_damage_to_passengers'],
    #         'deviate_from_identification_damage_to_passengers': self.tasks_config[
    #             'rewrite_task_deviate_from_identification_damage_to_passengers'],
    #         'identify_by_risk_damage_to_passengers': self.tasks_config[
    #             'rewrite_task_identify_by_risk_damage_to_passengers'],
    #         'customer_declines_advice': self.tasks_config['rewrite_task_customer_declines_advice'],
    #     }
    #
    #     combined_description = f"""
    #     Based on the research results, analyze the client's needs and determine which ONE rewrite task to execute, then execute it.
    #
    #     STEP 1: DECISION LOGIC
    #     - If client wants to minimize ALL risks + third party damage → select minrisk_damage_to_third_parties
    #     - If client has euro risk tolerance + third party damage → select risk_in_euros_damage_to_third_parties
    #     - If client wants higher risk than assessed + third party damage → select deviate_from_identification_damage_to_third_parties
    #     - If client wants per-risk assessment + third party damage → select identify_by_risk_damage_to_third_parties
    #     - If client wants to minimize ALL risks + standstill → select minrisk_damage_by_standstill
    #     - If client has euro risk tolerance + standstill → select risk_in_euros_damage_by_standstill
    #     - If client wants higher risk than assessed + standstill → select deviate_from_identification_damage_by_standstill
    #     - If client wants per-risk assessment + standstill → select identify_by_risk_damage_by_standstill
    #     - If client wants to minimize ALL risks + personal items → select minrisk_loss_of_personal_items
    #     - If client has euro risk tolerance + personal items → select risk_in_euros_loss_of_personal_items
    #     - If client wants higher risk than assessed + personal items → select deviate_from_identification_loss_of_personal_items
    #     - If client wants per-risk assessment + personal items → select identify_by_risk_loss_of_personal_items
    #     - If client wants to minimize ALL risks + passengers → select minrisk_damage_to_passengers
    #     - If client has euro risk tolerance + passengers → select risk_in_euros_damage_to_passengers
    #     - If client wants higher risk than assessed + passengers → select deviate_from_identification_damage_to_passengers
    #     - If client wants per-risk assessment + passengers → select identify_by_risk_damage_to_passengers
    #     - If client explicitly declines advice → select customer_declines_advice
    #
    #     STEP 2: EXECUTE THE SELECTED TASK
    #     Once you determine which task to use, execute it exactly according to its specific instructions:
    #
    #     Available tasks and their instructions:
    #     """
    #
    #     for task_name, config in rewrite_configs.items():
    #         combined_description += f"\n\n**{task_name}:**\n{config['description']}\n"
    #
    #     return Task(
    #         description=combined_description,
    #         expected_output="Een complete Nederlandse alinea volgens de geselecteerde rewrite task, met alle parameters correct ingevuld uit de research data.",
    #         agent=self.writer(),
    #         context=[self.research()]
    #     )
    @task
    def formulate_template_query(self) -> Task:
        return Task(
            description="""
            Based on the client’s needs and the research data, generate a concise natural-language query
            that would help retrieve the most relevant rewrite template from the SQL database.

            Make sure the query reflects the type of risk (third parties, passengers, etc.)
            and the risk strategy (minimize risk, risk in euros, etc.).
            """,
            expected_output="An SQL statement along the following lines(fill in CATEGORY_NAME & SUB_CATEGORY_NAME):SELECT at.text FROM advisory_texts at JOIN categories c ON at.category_id = c.id JOIN sub_categories sc ON at.sub_category_id = sc.id WHERE c.name = 'CATEGORY_NAME' AND sc.name = 'SUB_CATEGORY_NAME';",
            agent=self.reader(),
            context=[self.research()]
        )

    @task
    def query_advisory_template(self) -> Task:
        return Task(
            description="""
                You are given research findings about a client's risk preferences and situations.

                Your task is to:
                1. Determine the most appropriate **category** and **subcategory** based on the client's needs.
                   - For example, if the client is concerned with third-party damage and wants to minimize risk, the category may be "damage to third parties" and the subcategory may be "minimize all risks".
                2. Use the `Search a database's table content` tool to search for an advisory text.
                   - You must query using a **natural language phrase** that semantically describes the category and subcategory.
                   - Example search query: "minimize all risks for damage to third parties"
                   - Use this query with the tool in the format:
                     ```json
                     { "search_query": "..." }
                     ```

                ⚠️ Do **not** use SQL — this tool accepts only natural language search queries.

                Once you retrieve the advisory text:
                - Rewrite it into a **single, complete Dutch paragraph**.
                - Ensure the paragraph uses correct and formal Dutch.
                - Fill in any parameters using the research context.

                Your final output should be:
                - A single rewritten Dutch paragraph tailored to the client's needs.
                """,
            expected_output="Een volledige, herschreven Nederlandse paragraaf gebaseerd op het gevonden advies, correct afgestemd op de onderzoekscontext.",
            agent=self.writer(),  # assuming `self.writer()` returns your writer agent
            context=[self.research()],
            tools=[sql_search]
        )

    @task
    def generate_rewrite(self) -> Task:
        return Task(
            description="""
            Using the template retrieved from the database and the research context, write a complete
            Dutch paragraph that rewrites the client's situation according to the provided template.

            Fill in any template parameters using information from the research data.
            """,
            expected_output="Een complete Nederlandse alinea op basis van het template en de onderzoeksdata.",
            agent=self.writer(),
            context=[self.research()]
        )

    # @task
    # def rewrite_task_eigenrisico(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['rewrite_task_eigenrisico'], # type: ignore[index]
    #     )


    @crew
    def crew(self) -> Crew:
        """Creates the Tvm crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

