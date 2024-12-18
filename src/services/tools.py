import os

from langchain.agents import Tool
from langchain_community.utilities import WikipediaAPIWrapper, GoogleSerperAPIWrapper
from tools.football import (
    get_specialist_comments_tool,
    get_match_details_tool,
    get_match_stats_tool,
    get_player_stats_tool,
    get_match_score_details_tool,
)


def _setup_tools() -> list[Tool]:
    """Set up the tools for the chat agent."""

    search = GoogleSerperAPIWrapper(
        serper_api_key=os.getenv("SERPER_API_KEY"), gl="us", hl="en", k=5
    )

    wikipedia = WikipediaAPIWrapper()

    return [
        get_match_details_tool,
        get_player_stats_tool,
        get_specialist_comments_tool,
        get_match_stats_tool,
        get_match_score_details_tool,
        Tool(
            name="SearchTeamInformation",
            func=search.run,
            description="""
            Useful for when you want to search for information
            about a specific team or player.
            """,
        ),
        Tool(
            name="Search",
            func=search.run,
            description="""
            A tool to answer complicated questions.  
            Useful for when you need to answer questions
            competition events like matches, or team
            details. Input should be a question.          
            """,
        ),
        Tool(
            name="Wikipedia",
            func=wikipedia.run,
            description="""
            A wrapper around Wikipedia. Useful for when you need
            to answer general questions about people, players, teams,
            competitions, stadiums (the stadium history and
            capacity), cities, events or other subjects.
            Input should be a search query.
            """,
        ),
    ]
