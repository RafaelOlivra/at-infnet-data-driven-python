import json
import streamlit as st

from langchain_community.callbacks.streamlit import StreamlitCallbackHandler

from dotenv import load_dotenv
from stats.competitions import get_competitions, get_matches
from stats.matches import get_match_df, get_match_score_details, get_match_stats_summary
from tools.football import (
    get_specialist_comments_about_match,
    get_lineups,
    retrieve_match_details_action,
    retrieve_match_details,
)
from services.gemini_agent import GeminiAgent as AiFootballAgent

# Load environment variables
load_dotenv()

# ------------------------
# Page layout and setup
# ------------------------

APP_TITLE = "AI Football Match Analyzer"

# Set page title
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="⚽️",
    layout="centered",
    initial_sidebar_state="expanded",
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

    st.sidebar.title("⚽️ " + APP_TITLE)

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

        # Visualizations
        st.sidebar.header("📊 Match Visualizations")

        options = ["🤖 Expert Chat", "🎙️ Match Commentator", "🔎 Data Explorer"]
        visualization = st.sidebar.radio("Select a visualization to display:", options)
        set_state("selected_visualization", visualization)


# ------------------------
# Main app
# ------------------------
def Main():

    visualization = get_state("selected_visualization")

    # Get the current state
    competition_id = get_state("selected_competition_id")
    season_id = get_state("selected_season_id")
    match_id = get_state("selected_match_id")
    match_title = get_state("selected_match_title")
    home_team = get_state("selected_home_team")
    alway_team = get_state("selected_alway_team")
    match_df = get_match_df(match_id)

    col1, col2, col3 = st.columns([5, 2, 2])
    col1.subheader(visualization)
    if not match_id:
        st.title(visualization)
        st.write(
            "Use the sidebar to select a competition, then a match, and start a conversation."
        )
        return

    # ------------------------
    # 🤖 Expert Chat
    # ------------------------
    if visualization == "🤖 Expert Chat":

        # Set up the agent
        agent = get_state("agent")
        if not agent:
            agent = AiFootballAgent()
            set_state("agent", agent)

        # Clear chat history if the match changes
        if get_state("previous_match_id") != match_id:
            agent.clear_chat_history()
            set_state("previous_match_id", match_id)

        # Clear chat history
        disable_btns = not agent.has_chat_history()
        with col2:
            if st.button(
                "Clear Chat 🗑", use_container_width=True, disabled=disable_btns
            ):
                agent.clear_chat_history()
                st.rerun()

        # Export chat history to JSON
        with col3:
            json = agent.chat_history_to_json()
            st.download_button(
                "Export Chat ⬇️",
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
        col1, col2 = st.columns([8, 2])
        col1.write("#### Chat")

        # Clear the streaming leftover after we get the complete response
        CLEAR_STREAMING_THOUGHTS = False
        with col2:
            # Show streaming thoughts
            CLEAR_STREAMING_THOUGHTS = not st.checkbox(
                "Keep Thoughts", key="clear-streaming-thoughts"
            )

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

    # ------------------------
    # 🎙️ Match Commentator
    # ------------------------
    if visualization == "🎙️ Match Commentator":

        # Set up the agent
        agent = get_state("agent")
        if not agent:
            agent = AiFootballAgent()
            set_state("agent", agent)

        display_match_score(competition_id, season_id, match_id)

        # Narration style selection
        narration_style = st.selectbox(
            "Select a narration style",
            ["Formal", "Funny", "Technical"],
            placeholder="...",
        )

        # Get the specialist comments
        # We convert this to a string so we take advantage of the ai tool we
        # already have developed
        match_details = retrieve_match_details(competition_id, season_id, match_id)
        lineups = get_lineups(match_id)
        if st.button(
            "Generate Match Commentary", type="primary", use_container_width=True
        ):
            with st.spinner("The commentator is getting ready..."):
                specialist_comments = get_specialist_comments_about_match(
                    match_details=match_details,
                    lineups=lineups,
                    style=narration_style.lower(),
                )

                st.markdown(specialist_comments)

    # ------------------------
    # 🔎 Data Explorer
    # ------------------------
    if visualization == "🔎 Data Explorer":

        display_match_score(competition_id, season_id, match_id)

        st.write("##### Filter and Explore Match Data")

        # Make a multiselect for selecting the columns to display
        columns = st.multiselect(
            "Columns",
            match_df.columns.tolist(),
            default=["player", "shot_outcome"],
        )
        df = match_df[columns]

        # Allow user to filter the displayed data with a search_filter box
        search_filter = st.text_input("Filter Contents", "Goal")
        if search_filter:
            df = df[
                df.astype(str)
                .apply(lambda x: x.str.contains(search_filter, case=False, na=False))
                .any(axis=1)
            ]

        # Show the data in a dataframe
        st.dataframe(df, use_container_width=True)

        # Show a bar graph of the data
        st.write("##### Data Visualization")

        # Count events by player
        if "player" in df.columns:
            # Drop null values
            df = df.dropna()
            player_counts = df["player"].value_counts()
            st.bar_chart(player_counts)
        else:
            st.info(
                """Select the 'player' column and 'shot_outcome' to display a bar chart. You can also use the 'Filter Contents' field to filter the displayed data."""
            )

        # Download the filtered data
        st.write("##### Download Data")
        st.write("Click the button below to download the filtered data as a CSV file.")
        csv_content = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_content,
            file_name=f"football-match-{match_id}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary",
        )


if __name__ == "__main__":
    Sidebar()
    Main()
