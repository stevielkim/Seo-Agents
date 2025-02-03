import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, WebsiteSearchTool, SpiderTool
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
os.environ["SERPER_API_KEY"]
os.environ["SPIDER_API_KEY"]
spider_scraper = SpiderTool()
serper_tool = SerperDevTool()
web_search_tool = WebsiteSearchTool()



llm = LLM(
    model="gpt-4o",
    temperature=0.4,
	timeout=150,
	api_key=OPENAI_API_KEY
)

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class SeoAgentsCrew():
	"""SeoAgentsCrew crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			llm=llm,
			tools=[serper_tool,web_search_tool,spider_scraper],
			allow_delegation=True,
			verbose=True
		)

	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			llm=llm,
			verbose=True
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
			output_file='reports/seo_report.md'
		)
	@task
	def scraper_task(self) -> Task:
		return Task(
			config=self.tasks_config['scraper_task'],
			output_file='reports/analysis_report.md'
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
			output_file='reports/blog_post_rewrite.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the SeoAgentsCrew crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			memory=True,
			planning=True
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
