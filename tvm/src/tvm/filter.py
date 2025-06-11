from crewai import Agent, Task, Crew, LLM
import os


class InsuranceFilterService:
    """Simple service to filter queries for insurance-related content using AI"""

    OPEN_API_BASE = os.environ.get("OPENAI_API_BASE")
    OPEN_API_KEY = os.environ.get("OPENAI_API_KEY")
    DEFAULT_LLM = os.environ.get("DEFAULT_LLM")

    def default_llm(self) -> LLM:
        return LLM(
            model=self.DEFAULT_LLM,
            temperature=0.3,
            api_base=self.OPEN_API_BASE,
            api_key=self.OPEN_API_KEY,
        )

    def __init__(self):
        self.screener_agent = Agent(
            role="Insurance Query Screener",
            goal="Determine if a query is about insurance or financial advisory",
            backstory="You are an expert who can quickly identify insurance-related topics.",
            llm=self.default_llm(),
            verbose=True
        )

    def screen_query(self, query: str) -> bool:
        try:
            filter_task = Task(
                description=f"""
                Is this query about insurance, financial advisory, or business risk management?

                Query: "{query}"

                Answer with only "YES" or "NO".
                """,
                expected_output="A single word: YES or NO",
                agent=self.screener_agent
            )

            screening_crew = Crew(
                agents=[self.screener_agent],
                tasks=[filter_task],
                verbose=False
            )

            result = screening_crew.kickoff()

            return "YES" in str(result).upper()

        except Exception as e:
            print(f"Filter failed: {e}")
            return True


filter_service = InsuranceFilterService()