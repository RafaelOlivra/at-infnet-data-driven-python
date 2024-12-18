import os

from langchain.agents import Tool
from langchain_community.utilities import WikipediaAPIWrapper, GoogleSerperAPIWrapper
from tools.football import get_specialist_comments, get_match_details, get_match_stats


def _setup_tools() -> list[Tool]:
    """Set up the tools for the chat agent."""

    search = GoogleSerperAPIWrapper(
        serper_api_key=os.getenv("SERPER_API_KEY"), gl="us", hl="en", k=5
    )

    wikipedia = WikipediaAPIWrapper()

    return [
        get_match_details,
        get_specialist_comments,
        get_match_stats,
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
