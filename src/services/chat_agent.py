import streamlit as st
import json

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

from langchain_core.callbacks.base import Callbacks

from services.tools import _setup_tools


class SmartChatAgent:
    def __init__(self, prompt_template: str = None, input_variables=None):
        self.llm = self._setup_llm()
        self.tools = _setup_tools()
        self.prompt = self._setup_prompt(
            prompt_template=prompt_template, input_variables=input_variables
        )
        self.agent = self._setup_agent()
        self.executor = self._get_agent_executor()
        self.name = "Smart Chat Agent"

    # ------------------------
    # User facing methods
    # ------------------------

    def ask(
        self, query: str = "", input_data: dict = None, callbacks: Callbacks = None
    ) -> str:
        """Ask the agent a question."""

        # If input data is provided, update the agent's input variables
        _input = {"input": query}
        if input_data:
            for key, value in input_data.items():
                _input[key] = value

        # Check if query is empty
        if not query:
            return "Please provide a query to ask the agent."

        try:
            response = self.executor.invoke(_input, {"callbacks": callbacks})
            return response["output"]
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def invoke(self, input_data: dict) -> str:
        """Invoke the agent with input data and metadata."""
        try:
            response = self.executor.invoke(input_data)
            return response["output"]
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def clear_chat_history(self):
        """Clear the chat history and reinitialize the AgentExecutor."""
        self.executor.memory.clear()

    def chat_history(self) -> list[HumanMessage | SystemMessage]:
        """Get the chat history."""
        return self.executor.memory.chat_memory.messages

    def chat_history_to_json(self) -> list[dict]:
        """Export the chat history to a JSON file."""
        history = []
        for message in self.chat_history():
            history.append(
                {
                    "type": message.type,
                    "content": message.content,
                    "metadata": message.response_metadata,
                }
            )
        return json.dumps(history, indent=4)

    def has_chat_history(self) -> bool:
        """Check if the chat history is empty."""
        return bool(self.chat_history())

    # ------------------------
    # Set-up the LLM model
    # ------------------------

    def _setup_llm(self):
        """Set up the language model"""
        assert False, "Subclasses must implement this method"

    def _setup_agent(self):
        """Set up the agent"""
        return create_react_agent(llm=self.llm, tools=self.tools, prompt=self.prompt)

    def _get_agent_executor(self) -> AgentExecutor:
        """Get the agent executor from the session state"""
        if "agent_executor" not in st.session_state:
            msgs = StreamlitChatMessageHistory()
            memory = ConversationBufferMemory(
                chat_memory=msgs,
                input_key="input",
                return_messages=True,
                memory_key="history",
            )
            st.session_state.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                memory=memory,
                verbose=True,
                max_iterations=10,
                handle_parsing_errors=True,
            )
        return st.session_state.agent_executor

    def _setup_prompt(
        self, prompt_template: str = None, input_variables=None
    ) -> PromptTemplate:
        """
        Set up the prompt template for the agent.

        Args:
            prompt_template (str): The prompt template to use. If None, a default template will be used.

        Returns:
            PromptTemplate: The prompt template.
        """
        prompt_template = (
            prompt_template
            or """
        You are a helpful AI assistant tasked with analyzing a football match. 
        Your goal is to provide insights and perform analyses based on the {match_name} match's details.
        The match is identified by its unique database ID: {match_id}. 
        The competition ID: {competition_id}.
        The season ID: {season_id}.

        The task involves multiple aspects:
        1. Analyze match details such as date, location, competition, and result.
        2. Provide context about the match's importance (e.g., stage, rivalry, stakes).
        3. Analyze and comment on the starting XI of both teams, including key players, tactical insights, or notable absences.
        4. Perform any other relevant tasks requested by the user regarding the match.

        You have access to the following tools: {tool_names}.
        Descriptions of tools: {tools}.

        ### Tools and Usage Instructions:
        - Each tool has a specific purpose, such as retrieving match details, analyzing lineups, or generating summaries.
        - To use a tool, respond exactly in this format:

        Thought: [Your reasoning about what action to take next]
        Action: [The name of the tool to use] (NEVER reply with None or Stop)
        Action Input: [The input required by the tool, such as the match_id or specific data]
        Observation: [The output or result from the tool]
        
        NEVER reply with Action: None or Action: Stop.
        THIS IS SUPER IMPORTANT!

        Example:
            Thought: I need to retrieve the basic details of the match to provide an overview.
            Action: get_match_details
            Action Input: {{"match_id": "12345", "competition_id": "123", "season_id": "02"}}
            Observation: Do I have the match details? If not, I will use the tool to retrieve them.
                        Otherwise, I will proceed with the analysis.

        ### Observations and Next Steps:
        - First decide if really need to use a tool or if you can provide an answer directly.
        - Based on the tool's output, decide on the next action or provide your analysis.
        - If more data is needed, use another tool or refine your analysis.
        - If the task is complete, provide a final answer.
        - Avoid generating code when possible, try to get the data from the available tools or strings if possible.
        - If you need have a final answer jump to the stopping condition right away.
        
        ### Stopping Condition:
        - When the analysis is complete or you think you don't need any tools, respond in this format:
        
        Thought: I have completed the analysis. No further tools are required.
        Final Answer: [Your final answer]
        
        ## Chat History:
        {history}

        ### Current Task:
        {input}

        ### Agent's Workspace:
        {agent_scratchpad}
        """
        )

        # Allow custom input variables to be passed
        if input_variables:
            return PromptTemplate(
                template=prompt_template,
                input_variables=input_variables,
            )
        else:
            return PromptTemplate(
                template=prompt_template,
                input_variables=[
                    "input",
                    "match_id",
                    "match_name",
                    "competition_id",
                    "season_id",
                    "agent_scratchpad",
                    "tools",
                    "tool_names",
                    "history",
                ],
            )
