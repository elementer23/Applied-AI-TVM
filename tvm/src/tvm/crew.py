from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Dict, Any



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
        )

    @task
    def research(self) -> Task:
        return Task(
            config=self.tasks_config['research'],
            agent=self.reader()
        )

    @task
    def decide_and_execute_rewrite(self) -> Task:

        rewrite_configs = {
            'minrisk_damage_to_third_parties': self.tasks_config['rewrite_task_minrisk_damage_to_third_parties'],
            'risk_in_euros_damage_to_third_parties': self.tasks_config[
                'rewrite_task_risk_in_euros_damage_to_third_parties'],
            'deviate_from_identification_damage_to_third_parties': self.tasks_config[
                'rewrite_task_deviate_from_identification_damage_to_third_parties'],
            'identify_by_risk_damage_to_third_parties': self.tasks_config[
                'rewrite_task_identify_by_risk_damage_to_third_parties'],
            'minrisk_damage_by_standstill': self.tasks_config['rewrite_task_minrisk_damage_by_standstill'],
            'risk_in_euros_damage_by_standstill': self.tasks_config['rewrite_task_risk_in_euros_damage_by_standstill'],
            'deviate_from_identification_damage_by_standstill': self.tasks_config[
                'rewrite_task_deviate_from_identification_damage_by_standstill'],
            'identify_by_risk_damage_by_standstill': self.tasks_config[
                'rewrite_task_identify_by_risk_damage_by_standstill'],
            'minrisk_loss_of_personal_items': self.tasks_config['rewrite_task_minrisk_loss_of_personal_items'],
            'risk_in_euros_loss_of_personal_items': self.tasks_config[
                'rewrite_task_risk_in_euros_loss_of_personal_items'],
            'deviate_from_identification_loss_of_personal_items': self.tasks_config[
                'rewrite_task_deviate_from_identification_loss_of_personal_items'],
            'identify_by_risk_loss_of_personal_items': self.tasks_config[
                'rewrite_task_identify_by_risk_loss_of_personal_items'],
            'minrisk_damage_to_passengers': self.tasks_config['rewrite_task_minrisk_damage_to_passengers'],
            'risk_in_euros_damage_to_passengers': self.tasks_config['rewrite_task_risk_in_euros_damage_to_passengers'],
            'deviate_from_identification_damage_to_passengers': self.tasks_config[
                'rewrite_task_deviate_from_identification_damage_to_passengers'],
            'identify_by_risk_damage_to_passengers': self.tasks_config[
                'rewrite_task_identify_by_risk_damage_to_passengers'],
            'customer_declines_advice': self.tasks_config['rewrite_task_customer_declines_advice'],
        }

        combined_description = f"""
        Based on the research results, analyze the client's needs and determine which ONE rewrite task to execute, then execute it.

        STEP 1: DECISION LOGIC
        - If client wants to minimize ALL risks + third party damage → select minrisk_damage_to_third_parties
        - If client has euro risk tolerance + third party damage → select risk_in_euros_damage_to_third_parties
        - If client wants higher risk than assessed + third party damage → select deviate_from_identification_damage_to_third_parties
        - If client wants per-risk assessment + third party damage → select identify_by_risk_damage_to_third_parties
        - If client wants to minimize ALL risks + standstill → select minrisk_damage_by_standstill
        - If client has euro risk tolerance + standstill → select risk_in_euros_damage_by_standstill
        - If client wants higher risk than assessed + standstill → select deviate_from_identification_damage_by_standstill
        - If client wants per-risk assessment + standstill → select identify_by_risk_damage_by_standstill
        - If client wants to minimize ALL risks + personal items → select minrisk_loss_of_personal_items
        - If client has euro risk tolerance + personal items → select risk_in_euros_loss_of_personal_items
        - If client wants higher risk than assessed + personal items → select deviate_from_identification_loss_of_personal_items
        - If client wants per-risk assessment + personal items → select identify_by_risk_loss_of_personal_items
        - If client wants to minimize ALL risks + passengers → select minrisk_damage_to_passengers
        - If client has euro risk tolerance + passengers → select risk_in_euros_damage_to_passengers
        - If client wants higher risk than assessed + passengers → select deviate_from_identification_damage_to_passengers
        - If client wants per-risk assessment + passengers → select identify_by_risk_damage_to_passengers
        - If client explicitly declines advice → select customer_declines_advice

        STEP 2: EXECUTE THE SELECTED TASK
        Once you determine which task to use, execute it exactly according to its specific instructions:

        Available tasks and their instructions:
        """

        for task_name, config in rewrite_configs.items():
            combined_description += f"\n\n**{task_name}:**\n{config['description']}\n"

        return Task(
            description=combined_description,
            expected_output="Een complete Nederlandse alinea volgens de geselecteerde rewrite task, met alle parameters correct ingevuld uit de research data.",
            agent=self.writer(),
            context=[self.research()]
        )

    @task
    def rewrite_task_eigenrisico(self) -> Task:
        return Task(
            config=self.tasks_config['rewrite_task_eigenrisico'], # type: ignore[index]
        )


    @crew
    def crew(self) -> Crew:
        """Creates the Tvm crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

