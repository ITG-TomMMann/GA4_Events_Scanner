import asyncio

from agents import Agent, ItemHelpers, MessageOutputItem, Runner, trace
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from pydantic import BaseModel


template = """Analyse the {{data_type}} data from {{time_period}} 
            and identify the top {{ number }} examples from {{ field }}."""

template2 = """Analyse the {{data_type}} data from {{time_period}} 
            and identify the top {{ number }} examples from {{ field }}.
            
            {% if rag_analysis_retrieved %} Analyse the RAG results in context of the sql analysis
            """


# 1. accept different types of Data 
# 2. adjust eh analayiss depth based on requirements
# 3. provide formatted ouput for different audieences


"""
This example shows the agents-as-tools pattern. The frontline agent receives a user message and
then picks which agents to call, as tools. In this case, it picks from a set of translation
agents.
"""

nl2sql_agent = Agent(
    name="nl2sql_agent",
    instructions="You generate sql code from the natural language query by using tools and guidance provided",
    handoff_description="Generate sql code according to user's query",
)

rag_agent = Agent(
    name="rag_agent",
    instructions="You retrieve relevant information from the Vector Database using appropriate tools to answer the query",
    handoff_description="Find whether the Vector Database has information corresponding to user's query",
)

analysis_agent = Agent(
    name="analysis_agent",
    instructions="You take a csv produced, analyse the schema, transform that data and output analysis of the user's original query",
    handoff_description="An english to italian translator",
)

orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=(
        "You are a data analyst agent. You use the tools given to you to answer user query with analysis."
        "If asked for multiple analysises, you call the relevant tools in order."
        "You never analyse on your own, you always use the provided tools."
    ),
    tools=[
        nl2sql_agent.as_tool(
            tool_name="generate_sql",
            tool_description="Translate the user's message to sql",
        ),
        rag_agent.as_tool(
            tool_name="retrieve_query",
            tool_description="Retrieve info from Vector Database with user's message",
        ),
        analysis_agent.as_tool(
            tool_name="translate_to_italian",
            tool_description="Translate the user's message to Italian",
        ),
    ],
)

synthesizer_agent = Agent(
    name="synthesizer_agent",
    instructions="You inspect the analysis, combine the findings into a unified analysis piece, correct them if needed, and produce a final concatenated analysis piece .",
)


async def main():
    msg = input("Hi! I want to find total number of visitors in 2025? ")

    # Run the entire orchestration in a single trace
    with trace("Orchestrator evaluator"):
        orchestrator_result = await Runner.run(orchestrator_agent, msg)

        for item in orchestrator_result.new_items:
            if isinstance(item, MessageOutputItem):
                text = ItemHelpers.text_message_output(item)
                if text:
                    print(f"  - Translation step: {text}")

        synthesizer_result = await Runner.run(
            synthesizer_agent, orchestrator_result.to_input_list()
        )

    print(f"\n\nFinal response:\n{synthesizer_result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())