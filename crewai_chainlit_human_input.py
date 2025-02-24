import asyncio

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
import chainlit as cl
from chainlit import run_sync

load_dotenv(override=True)

class CrewInput(BaseModel):
    initial_message: str = Field(..., description="Initial message from the person")

class PersonalInformationOutput(BaseModel):
    first_name: str = Field(default="UNKNOWN", description="Person's first name")
    last_name: str = Field(default="UNKNOWN", description="Person's last name")
    country: str = Field(default="UNKNOWN", description="Person's country of residence")
    city: str = Field(default="UNKNOWN", description="Person's city of residence")

def ask_human(question: str) -> str:
    human_response  = run_sync(cl.AskUserMessage(content=f"{question}").send())
    if human_response:
        return human_response["output"]

class HumanInputContextTool(BaseTool):
    name: str = "Ask Human follow up questions to get additonal context"
    description: str = "Use this tool to ask follow-up questions to the human in case additional context is needed"
    
    def _run(self, question: str) -> str:
        return ask_human(question)

human_tool = HumanInputContextTool()

information_collector = Agent(
    role="Information collector",
    goal="You communicate with the user until you collect all the required information. "
         "You ask clear questions and maintain a friendly but professional tone throughout the interaction. ",
    tools=[human_tool],
    verbose=True,
    backstory=(
        "You are an experienced information gatherer with excellent "
        "communication skills and attention to detail. You excel at "
        "structuring conversations to efficiently collect information "
        "while keeping users engaged and comfortable. You're known for "
        "your ability to ask the right questions in the right order "
        "and ensure all necessary details are captured accurately."
    )
)

information_summarizer = Agent(
   role="Information Summarizer", 
   goal="You take the collected information and transform it into clear, natural language summaries "
        "that capture all key details in an engaging and easy-to-read format. You ensure no important "
        "information is lost while making the summary flow naturally.",
   tools=[],
   verbose=True,
   backstory=(
       "You are a skilled writer with a talent for synthesizing "
       "information into compelling narratives. Your greatest strength "
       "is taking raw data and details and weaving them into clear, "
       "natural language that anyone can understand. You pride yourself "
       "on never losing important details while making information "
       "accessible and engaging."
   )
)

collector_task = Task(
    name="Collect Personal Project Information",
    description=(
        "Based on the initial message '{initial_message}', collect detailed information about the person by: "
        "\nFinding out their first name and last name their location, meaning country and city "
        "\nAsk questions in a natural way. "
        "\nStore all collected information in a structured format."
    ),
    expected_output="All required fields of person. None can be missing.",
    output_json=PersonalInformationOutput,
    agent=information_collector,
    human_input=False
)

summarizer_task = Task(
   name="Create Person Summary",
   description=(
       "Transform the collected personal information into a natural introduction by: "
       "\n1. Reading through the collected name and location details "
       "\n2. Creating a natural language introduction about the person "
   ),
   expected_output=(
       "A brief, natural sentence introduction that presents the person's "
       "name and location."
   ),
   agent=information_summarizer,
   context=[collector_task],
)

my_crew = Crew(
    agents=[information_collector, information_summarizer],
    tasks=[collector_task, summarizer_task],
    verbose=True,
    memory=True
)

if __name__ == "__main__":
    input_data = CrewInput(initial_message="Hi I am James")
    result = my_crew.kickoff(inputs=input_data.model_dump())
    print(result)


@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="Hello I am your personal Assistant. How can I help?").send()
    

@cl.on_message
async def on_message(message: cl.Message):
    # This function will be called when user sends their first and subsequent messages
    input_data = CrewInput(initial_message=message.content)    
    result = await asyncio.to_thread(lambda: my_crew.kickoff(inputs=input_data.model_dump()))

    await cl.Message(content=str(result)).send()