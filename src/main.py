import json
import streamlit as st

from langchain_community.callbacks.streamlit import StreamlitCallbackHandler

from dotenv import load_dotenv
from stats.competitions import get_competitions, get_matches
from stats.matches import get_match_df, get_match_score_details, get_match_stats_summary
from services.gemini_agent import GeminiAgent as AiFootballAgent

# from services.openai_agent import OpenAIAgent as AiFootballAgent

# Load environment variables
load_dotenv()

# ------------------------
# Page layout and setup
# ------------------------

APP_TITLE = "⚽️ AI Football Match Analyzer"

# Set page title
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="⚽️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ------------------------
# State Management
# ------------------------
def set_state(key, value):
    st.session_state[key] = value


def get_state(key):
    return st.session_state.get(key, None)


# ------------------------
# Load data
# ------------------------


def load_competitions():
    """
    Simulates loading competitions from your function.
    Replace this with the actual call to fetch competitions.
    """
    return json.loads(get_competitions())


def load_matches(competition_id, season_id):
    """
    Simulates loading matches for a specific competition.
    Replace this with the actual call to fetch matches for a competition.
    """
    return json.loads(get_matches(competition_id, season_id))


# ------------------------
# Display functions
# ------------------------


def display_match_score(competition_id, season_id, match_id):
    with st.container(border=True):
        score_dict = get_match_score_details(competition_id, season_id, match_id)
        col1, col2, col3 = st.columns([5, 2, 5])
        with col1:
            st.markdown(
                f"<h5 style='text-align: center; padding: 0;'>{score_dict['home_team_name']}</h5>",
                unsafe_allow_html=True,
            )
            if score_dict["home_team_penalty"]:
                st.markdown(
                    f"<h1 style='text-align: center;'>{score_dict['home_team_open_play']} ({score_dict['home_team_penalty']})</h1>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<h1 style='text-align: center;'>{score_dict['home_team_open_play']}</h1>",
                    unsafe_allow_html=True,
                )
            st.markdown(
                f"<p style='text-align: center; font-size: 12px;'>{score_dict['home_team_player_goals']}</p>",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"<h1 style='text-align: center;'>x</h1>",
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"<h5 style='text-align: center; padding: 0;'>{score_dict['alway_team_name']}</h5>",
                unsafe_allow_html=True,
            )
            if score_dict["alway_team_penalty"]:
                st.markdown(
                    f"<h1 style='text-align: center;'>{score_dict['alway_team_open_play']} ({score_dict['alway_team_penalty']})</h1>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<h1 style='text-align: center;'>{score_dict['alway_team_open_play']}</h1>",
                    unsafe_allow_html=True,
                )
            st.markdown(
                f"<p style='text-align: center; font-size: 12px;'>{score_dict['alway_team_player_goals']}</p>",
                unsafe_allow_html=True,
            )


def display_overall_match_stats(match_id: int, home_team: str, alway_team: str):
    stats = get_match_stats_summary(match_id)
    with st.expander("Match Stats", expanded=True):
        col1, col2, col3 = st.columns([5, 2, 5])
        stats_names = list(stats[home_team].keys())
        with col1:
            for stat_name in stats_names:
                st.markdown(
                    f"<p style='text-align: center;'>{stats[home_team][stat_name]}</p>",
                    unsafe_allow_html=True,
                )
        with col2:
            for stat_name in stats_names:
                st.markdown(
                    f"<p style='text-align: center; font-weight: bold;'>{stat_name}</p>",
                    unsafe_allow_html=True,
                )
        with col3:
            for stat_name in stats_names:
                st.markdown(
                    f"<p style='text-align: center;'>{stats[alway_team][stat_name]}</p>",
                    unsafe_allow_html=True,
                )


def center_align(content):
    """Center align the content"""
    return f"<div style='text-align: center;'>{content}</div>"


# ------------------------
# Sidebar
# ------------------------


def Sidebar():

    st.sidebar.title(APP_TITLE)

    # Step 1: Select a Competition
    selected_competition = None
    selected_season = None
    selected_match = None
    match_id = None
    match_details = None
    specialist_comments = None

    st.sidebar.header("1️⃣ Select a Competition")
    competitions = load_competitions()
    competition_names = sorted(set([comp["competition_name"] for comp in competitions]))
    selected_competition = st.sidebar.selectbox(
        "Choose a Competition", competition_names
    )
    if selected_competition:
        # Step 2: Select a Season
        st.sidebar.header("2️⃣ Select a Season")
        seasons = set(
            comp["season_name"]
            for comp in competitions
            if comp["competition_name"] == selected_competition
        )
        selected_season = st.sidebar.selectbox("Choose a Season", sorted(seasons))

    if selected_season:
        # Get the selected competition ID
        competition_id = next(
            (
                comp["competition_id"]
                for comp in competitions
                if comp["competition_name"] == selected_competition
            ),
            None,
        )
        season_id = next(
            (
                comp["season_id"]
                for comp in competitions
                if comp["season_name"] == selected_season
                and comp["competition_name"] == selected_competition
            ),
            None,
        )
        # Step 2: Select a Match
        st.sidebar.header("3️⃣ Select a Match")
        matches = load_matches(competition_id, season_id)
        match_names = sorted(
            [f"{match['home_team']} vs {match['away_team']}" for match in matches]
        )

        if selected_match := st.sidebar.selectbox("Choose a Match", match_names):
            # Get the selected match ID
            match_details = next(
                (
                    match
                    for match in matches
                    if f"{match['home_team']} vs {match['away_team']}" == selected_match
                ),
                None,
            )
            match_id = match_details["match_id"]

        # Set states
        set_state("selected_competition", selected_competition)
        set_state("selected_competition_id", competition_id)
        set_state("selected_season_id", season_id)
        set_state("selected_match_id", match_id)
        set_state("selected_match_title", selected_match)
        set_state("selected_home_team", match_details["home_team"])
        set_state("selected_alway_team", match_details["away_team"])


# ------------------------
# Main app
# ------------------------
def Main():

    # Get the current state
    competition_id = get_state("selected_competition_id")
    season_id = get_state("selected_season_id")
    match_id = get_state("selected_match_id")
    match_title = get_state("selected_match_title")
    home_team = get_state("selected_home_team")
    alway_team = get_state("selected_alway_team")
    match_df = get_match_df(match_id)

    if not match_id:
        st.title(APP_TITLE)
        st.write(
            "Use the sidebar to select a competition, then a match, and start a conversation."
        )
        return

    col1, col2, col3 = st.columns([5, 2, 2])

    col1.subheader("🤖 Match Chat")

    # Set up the agent
    agent = get_state("agent")
    if not agent:
        agent = AiFootballAgent()
        set_state("agent", agent)

    # Clear chat history if the match changes
    if get_state("previous_match_id") != match_id:
        agent.clear_chat_history()
        set_state("previous_match_id", match_id)

    # Clear the streaming leftover after we get the complete response
    CLEAR_STREAMING_THOUGHTS = False

    # Clear chat history
    disable_btns = not agent.has_chat_history()
    with col2:
        if st.button("Clean 🗑", use_container_width=True, disabled=disable_btns):
            agent.clear_chat_history()
            st.rerun()

    # Export chat history to JSON
    with col3:
        json = agent.chat_history_to_json()
        st.download_button(
            "Export ⬇️",
            json,
            "football-ai-chat-history.json",
            "application/json",
            key="export-chat",
            use_container_width=True,
            disabled=disable_btns,
        )

    # Match details
    display_match_score(competition_id, season_id, match_id)
    display_overall_match_stats(match_id, home_team, alway_team)

    # Display chat messages from history on app rerun
    st.write("#### Chat")

    chat_history = agent.chat_history()
    if not chat_history:
        st.warning(
            """
            Ask a question to begin!  

            - "Who made the most passes in the match?"
            - "Which player had the most shots in the first half?"
            """
        )

    st.write(" ")
    for message in chat_history:
        with st.chat_message(message.type):
            st.markdown(message.content)

    # Accept user input
    if user_input := st.chat_input("Em que posso ajudar?"):
        with st.chat_message("human"):
            st.markdown(user_input)

        # Get response from agent
        try:
            streaming_callback = StreamlitCallbackHandler(
                st.container(), max_thought_containers=2
            )

            # Prepare input for the agent
            input_data = {
                "match_id": match_id,
                "match_name": match_title,
                "input": user_input,
                "competition_id": competition_id,
                "season_id": season_id,
            }

            # Ask the agent
            st.markdown(
                agent.ask(
                    query=user_input,
                    input_data=input_data,
                    callbacks=[streaming_callback],
                )
            )
        except Exception as e:
            st.error(e)

        # Clear the streaming output and show the final response
        if CLEAR_STREAMING_THOUGHTS:
            st.rerun()


if __name__ == "__main__":
    Sidebar()
    Main()
