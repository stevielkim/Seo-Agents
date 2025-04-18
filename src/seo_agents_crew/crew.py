import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, WebsiteSearchTool, SpiderTool,DirectoryReadTool, FileReadTool, FileWriterTool
from crewai.tasks.conditional_task import ConditionalTask
from crewai.tasks.task_output import TaskOutput

load_dotenv()

# Set up tools
file_writer_tool = FileWriterTool()
file_read_tool = FileReadTool()
directory_read_tool = DirectoryReadTool()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
os.environ["SERPER_API_KEY"]
# os.environ["SPIDER_API_KEY"]
spider_scraper = SpiderTool(
	depth=0, 
	metadata=True, 
	subdomain=True, 
	store_data=True, 
	gpt_config="gpt-4o", 
	return_format='raw',
	run_in_background=True,
	full_resource=True,
	api_key=os.environ["SPIDER_API_KEY"])

serper_tool = SerperDevTool()
web_search_tool = WebsiteSearchTool()

llm = LLM(
    model="gpt-4o",
    temperature=0.4,
	timeout=150,
	api_key=OPENAI_API_KEY
)

# def is_task_done(output: TaskOutput) -> bool:
# 	"""Check if the files a"""


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

	# @agent
	# def manager(self) -> Agent:
	# 	"""Manages the crew execution."""
	# 	return Agent(
	# 		config=self.agents_config['manager'],
	# 		llm=llm,
	# 		tools=[file_writer_tool, file_read_tool, directory_read_tool],
	# 		allow_delegation=True,
	# 		verbose=True
	# 	)


	@agent
	def scraper(self) -> Agent:
		"""
		Scrapes the web for blog posts on Medium.

		Returns:
			Agent: An agent configured for web scraping.
		Outputs:
			- blog_posts/*.md
		"""
		return Agent(
			config=self.agents_config['scraper'],
			llm=llm,
			tools=[
				web_search_tool, #might not need check later
				file_writer_tool,
				spider_scraper,
				directory_read_tool #might not need check later
			],
			allow_delegation=True,
			allow_code_execution=True,
			verbose=True
		)

	@agent
	def researcher(self) -> Agent:
		"""
		Searches the web for a given topic, writes an analysis report, and asynchronously scrapes the blog, 
		returning multiple files.

		Returns:
			Agent: An agent configured for web research and blog scraping.
		Outputs:
			- reports/seo_report.md
			- reports/blog_posts.md
		"""
		return Agent(
			config=self.agents_config['researcher'],
			llm=llm,
			tools=[
				serper_tool,
				web_search_tool,
				file_writer_tool,
				directory_read_tool
				],
			allow_delegation=True,
			allow_code_execution=True,
			verbose=True
		)

	@agent
	def reporting_analyst(self) -> Agent:
		'''Controls the optimization of blog posts based on the evaluation report.
		Evaluation Task:
			Dependencies:
				- reports/blog_posts (from scraper_task)
			Outputs:
				- reports/suggested_blog_post_changes_1, _2, _3, etc.
		Reporting Task:
			Dependencies:
				- reports/suggested_blog_posts_changes_1, _2, _3, etc.
			Outputs:
				- optimized_blog_posts/*.md
		Returns:
			Agent: An agent configured to control the Evaluation Task and Reporting Task.
		'''
		return Agent(
			config=self.agents_config['reporting_analyst'],
			llm=llm,
			tools=[
				directory_read_tool, 
				file_writer_tool, 
				file_read_tool
				],
			allow_delegation=True,
			verbose=True
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def research_task(self) -> Task:
		"""Task to research a topic and create an SEO report."""
		return Task(
			config=self.tasks_config['research_task'],
			output_file='reports/seo_report.md', # Report used for evaluation_task
			# create_directory=True
		)

	@task
	def scraper_task(self) -> Task:
		"""Task to scrape blog posts.
		Dependencies:
			None
		Outputs:
			- reports/blog_posts.md
		"""
		return Task(
			config=self.tasks_config['scraper_task'] 
		)

	
	@task
	def evaluation_task(self) -> Task:
		"""Task to evaluate the scraped blog posts against the SEO report.
		Output:	Suggested changes to each blog post.
		Dependencies:
			- reports/seo_report.md
			- reports/blog_posts.md
		"""
		return Task(
			config=self.tasks_config['evaluation_task']
		)
	
	@task
	def decision_task(self) -> Task:
		"""Task to make a decision based on the evaluation report.
		Returns: Task
		"""
		return Task(
			config=self.tasks_config['decision_task']
		)


	@task
	def writing_task(self) -> Task:
		"""Task to rewrite multiple blog posts based on the suggested changes in evaluation_task.
		Dependencies:
			- reports/suggested_blog_posts_changes_1, _2, _3, etc.
		Outputs: optimized_reports/*.md
		Returns: Task
		"""
		return Task(
			config=self.tasks_config['writing_task']
		)
	

	@crew
	def crew(self) -> Crew:
		"""Creates the SeoAgentsCrew crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			# process=Process.se
			# manager_llm = LLM("gpt-4o"),
			process=Process.sequential,
			verbose=True,
			memory=True,
			planning=True,
			output_log_file="crew_log.log",
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)

