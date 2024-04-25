import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

llm=ChatOpenAI(
    model="llama3-70b-8192",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"])


def create_crewai_setup():
    # Define Agents
    product_manager = Agent(
        role="Product Manager",
        goal=f"""Suggest product design for a given feature""",
        backstory="""You're a Former engineer turner product manager,
        who leverages her knack for innovation to lead product development 
        and transforming ideas into market-ready solutions. Ex Tesla, Microsoft employee.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        max_iter=10,

    )
    
    developer = Agent(
        role="Developer",
        goal=f"Suggest technical structure for given product design",
        backstory=f"""Experienced Software engineer with proven track record of 
        crafting robust and scalable solutions.Proficient in multiple programming languages including
        Python, Java and Javascript.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        max_iter=10
    )
    
    project_lead = Agent(
        role="Project lead",
        goal=f"""Finalize the final product and technical structure""",
        backstory=f"""CTO of the company who has 20 years of experience leading others in the project""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        max_iter=10
    )


    # Define Tasks
    task1 = Task(
        description=f"""Product flow for adding new feature: Face recognition login for XYZ app.""",
        expected_output="Detailed bullet points",
        agent=product_manager,
    )
    
    task2 = Task(
        description=f"""Using the insights provided, decide tech stack, estimate time for development and code flow""",
        expected_output="Short bullet points",
        agent=developer,
    )
    
    task3 = Task(
        description=f"""Using the insights provided in the previous 2 tasks, decide the final report about the feature and technicalities.
        Remove features that aren't urgent to save on proposed timeline by the developer""",
        expected_output="Detailed report",
        agent=project_lead,
    )

    # Create and Run the Crew
    product_crew = Crew(
        agents=[product_manager, developer, project_lead],
        tasks=[task1, task2, task3],
        verbose=2,
        process=Process.sequential,
    )
    
    crew_result = product_crew.kickoff()
    return crew_result

result=create_crewai_setup()

print(result)