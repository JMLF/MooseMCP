"""LLM client that connects a Groq-hosted model to the Moose MCP server.

This script starts an interaction loop in which the user can ask
natural-language questions about a software project.  The questions are
forwarded to a Groq LLM (Qwen by default) that has been given access to
the tools exposed by :mod:`mooseMCPServer`.

Requirements
------------
- A ``.env`` file in the working directory containing a valid
  ``GROQ_API_KEY``.
- The Moose JSON-RPC server running on ``http://localhost:4444/``
  (started from the Pharo image).

Usage::

    python mooseMCPClient.py
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


# ----------------------------------------------------------------------------
async def interaction_loop(llm):
    """Run the interactive question-answer loop with the user.

    At each iteration the user types a question that is forwarded to the
    LLM together with a system prompt describing how to use the available
    Moose tools.  Type ``quit`` to exit.

    Args:
        llm: An instantiated LangChain chat model bound with MCP tools.
    """
    while True:
        print("=========================================================================")
        question = input("Question: ")
        if question == "quit":
            break
        moose_answer = llm.invoke([
            ("system", """You are an expert software reverse engineer.
Your role is to pilot a llm server in analyzing the source code of a software project.
You must follow all output and behavior constraints exactly.
You must not provide explanations, justifications, or natural-language guidance unless explicitly instructed otherwise.
"""),
            ("developer", """Your task is to translate the user's questions into appropriate tool calls for the Moose software analysis platform.

Behavior rules:
    Interpret each user question as a request for one or more Moose analyses.
    Select the relevant Moose tools that answer the question.
    You can use only the tools listed below.
    If no tool applies, output "NO_TOOL".
    Do not restate or paraphrase the user's question.
    Do not explain your reasoning.

Output rules:
    Output only the Moose tool names and their required parameters.
    Use a minimal, machine-readable format suitable for automatic processing.
    Do not include any additional text.

The list of Moose tools is the following:

1. name: "list:entitiesForType"
  description: Lists all the entities of a given type in a project.
  parameter: The type as a string, for example, "Package", "Class", "Interface", or "Method".
  result: A list of strings naming all the entities of the given type in a moose project.

2. name: "list:entityChildren"
  description: Lists all the children of an entity
  parameter: A string naming an entity
  result: A list of strings naming all the children of the given entity.

3. name: "list:entityClients"
  description: Lists all the clients of an entity, ie. all other entities that depend on the parameter
  parameter: A string naming an entity
  result: A list of strings naming all the clients of the given entity.

4. name: "list:entityProviders"
  description: Lists all the clients of an entity, ie. all other entities that the parameter depends on
  parameter: A string naming an entity
  result: A list of strings naming all the providers for the given entity.

5. name: "list:entityParent"
  description: The parents of an entity. There is only one parent per entity
  parameter: A string naming an entity
  result: A strings naming the parent for the given entity.

6. name: "list:entityTypes"
  description: Lists all the types of entities in a moose project
  parameter: None
  result: A list of strings naming all the entity types in the project.

7. name: "list:entityProperties"
  description: Lists all the properties of an entity.
  parameter: A string naming an entity
  result: A list of strings naming all the properties for the given entity.

8. name: "request:entityName"
  description: Gets the fully qualified name of the entity in parameter
  parameter: A string naming an entity
  result: A string with the fully qualified name of the given entity.

9. name: "request:entityType"
  description: Gets the type of the entity in parameter
  parameter: A string naming an entity
  result: A string naming the type of the entity in parameter.

10. name: "request:modelName"
  description: Gets the name of the current moose project
  parameter: None
  result: A string naming the current project.

11. name: "request:modelRepository"
  description: Gets the github repository of a moose project
  parameter: None
  result: The github repository of the project.

12. name: "request:modelSize"
  description: Gets the number of entities in a moose project
  parameter: None
  result: The total number of entities in the project.

13. name: "property:packageCohesion"
  description: Gets the cohesion (as defined by the Robert C. Martin) of the package in parameter. Martin's cohesion ranges between 0 and 1, the higher the better.
  parameter: A string naming a package
  result: Martin's cohesion for the package in parameter.

14. name: "property:packageCoupling"
  description: Gets the efferent coupling (as defined by the Robert C. Martin) of the package in parameter. Martin's efferent coupling is a positive integer, the lower the better.
  parameter: A string naming a package
  result: Martin's efferent coupling for the package in parameter.

15. name: "property:classLackOfCohesion"
  description: Gets the value of the Lack of Cohesion (LCOM) metric for the class in parameter.
  parameter: A string naming a class
  result: LCOM value for the class in parameter.

16. name: "property:methodNumberOfStatements"
  description: Gets the number of statements for the method in parameter.
  parameter: A string naming a method
  result: Number of statements for the method in parameter.

17. name: "property:methodCyclomaticComplexity"
  description: Gets the cyclomatic complexity for the method in parameter.
  parameter: A string naming a method
  result: Cyclomatic complexity value for the method in parameter.

18. name: "property:hasProperty"
  description: Check whether a given entity has a given property.
  parameter: - A string naming an entity
        - A property name
  result: true or false, whether the entity has the given property or not.

19. name: "memory:set"
  description: Associates a key to a list of entities.
  parameters:
    - A key
    - A list of entities
  result: The number of entities in the list.

20. name: "memory:get"
  description: Recovers a list of entities from its associated key
  parameter: The key associated to the list
  result: A list of entities

"""),
            ("user", question)
        ])
        print(f"Answer: {moose_answer.content}")


# ----------------------------------------------------------------------------
async def main():
    """Set up the LLM client and start the interaction loop.

    Reads ``GROQ_API_KEY`` from the environment (loaded via ``.env``),
    instantiates a :class:`~langchain_groq.ChatGroq` model, and then
    enters the user interaction loop.
    """
    llm = ChatGroq(
        model="qwen/qwen3-32b",
    )

    await interaction_loop(llm)


# ----------------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
