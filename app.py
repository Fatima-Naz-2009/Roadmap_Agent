import re
import os

import streamlit as st
from fpdf import FPDF
from agents import (
    Agent,
    Runner,
    set_default_openai_client,
    set_default_openai_api,
    OpenAIChatCompletionsModel
)
from openai import AsyncOpenAI
from dotenv import load_dotenv


# Load the API keys from the .env file
load_dotenv()

GEMINI_KEY_1 = os.getenv("GEMINI_API_KEY")
GEMINI_KEY_2 = os.getenv("GEMINI_API_KEY_2")


# Create the roadmap agent
def build_agent(api_key, model_name="gemini-3.6-flash"):
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    set_default_openai_client(client)
    set_default_openai_api("chat_completions")

    model = OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=client
    )

    agent = Agent(
        name="Roadmap Agent",
        instructions="""You are a learning roadmap specialist.

Take a student's learning goal, available days, and study time per day.

Break the learning goal into logical topics.
Arrange the topics from foundational concepts to more advanced concepts.
Create a realistic day-by-day roadmap that fits within the student's available days and study time.

Do not ignore the student's timeline.
Do not create a roadmap longer than the number of days provided.
Make the amount of learning realistic for the available study time.

Return only the day-by-day roadmap in a clear and neat format.
""",
        model=model
    )

    return agent


# Create the primary agent if the API key is available
roadmap_agent = None

if GEMINI_KEY_1:
    roadmap_agent = build_agent(GEMINI_KEY_1)


# Generate a PDF containing the roadmap
def generate_pdf(roadmap_text, goal):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", size=16)
    pdf.multi_cell(
        0,
        10,
        "Your Learning Roadmap",
        align="C"
    )

    pdf.ln(5)

    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(
        0,
        8,
        f"Goal: {goal}"
    )

    pdf.ln(5)

    pdf.set_font("Helvetica", size=11)

    safe_text = (
        roadmap_text
        .encode("latin-1", "replace")
        .decode("latin-1")
    )

    pdf.multi_cell(
        0,
        7,
        safe_text
    )

    pdf_output = pdf.output(dest="S")

    if isinstance(pdf_output, str):
        return pdf_output.encode("latin-1")

    return bytes(pdf_output)


# Convert the generated roadmap text into separate days
def parse_roadmap_into_days(roadmap_text):
    days_dict = {}
    current_day = None

    for line in roadmap_text.splitlines():
        line = line.strip()

        if not line:
            continue

        match = re.match(
            r"^Day\s+(\d+):\s*(.*)$",
            line,
            re.IGNORECASE
        )

        if match:
            day_num = match.group(1)
            day_title = match.group(2).strip()

            current_day = f"Day {day_num}: {day_title}"
            days_dict[current_day] = []

        elif current_day and line.startswith("-"):
            task = line.lstrip("- ").strip()

            if task:
                days_dict[current_day].append(task)

    return days_dict


# Configure the Streamlit page
st.set_page_config(
    page_title="Learning Roadmap Generator",
    page_icon="🗺️",
    layout="centered",
    initial_sidebar_state="collapsed"
)


st.title("Your Learning Roadmap")


# Take the student's learning information
goal = st.text_input(
    "What do you want to learn?"
)

days = st.number_input(
    "How many days you want to learn that topic",
    min_value=1,
    step=1
)

hours = st.number_input(
    "How many hours you will study a day?",
    min_value=0.5,
    step=0.5
)

generate = st.button("Generate Roadmap")


# Generate the roadmap when the button is clicked
if generate:

    if not goal.strip():
        st.error("Please enter something you want to learn.")

    elif not GEMINI_KEY_1:
        st.error(
            "GEMINI_API_KEY was not found in your .env file."
        )

    else:

        prompt = f"""
Student's learning goal:
{goal}

Number of days available:
{days} days

Available study time per day:
{hours} hours

Your task:

1. Identify the 4-8 core subtopics required to achieve this goal, ordered from foundational to advanced.

2. Distribute these subtopics across exactly {days} days.
If a subtopic is large, split it across multiple consecutive days rather than rushing it.

If {days} is small, combine only closely related subtopics on the same day.
Never skip a subtopic entirely.

3. For each day, list 2-4 specific, concrete tasks.

Do not use vague phrases like:
"learn the basics"

Instead, name the actual concepts, terms, techniques, or skills that should be studied that day.

4. Make sure the total workload per day is realistic for {hours} hours.

Do not pack more into a day than {hours} hours can reasonably cover.

5. Every core subtopic from step 1 must appear somewhere in the final roadmap.

Do not omit a subtopic just because the number of days is small.
Instead, adjust the depth of the topic.

IMPORTANT FORMATTING RULES:

Output ONLY the day-by-day plan.

Do not add an introduction.

Do not add a summary.

Do not add closing remarks.

Each day MUST start on its own line in exactly this format:

Day 1: Short Title

Immediately after each day title, list that day's tasks as plain bullet points starting with "- ".

Example:

Day 1: Introduction to Python
- Understand variables and data types
- Learn arithmetic operators
- Practice basic input and output

Do not use markdown headers.

Do not use bold formatting.

Do not use numbering before the day titles.

Do not add anything before Day 1 or after the final day.
"""

        # Run the agent and return its final answer
        def try_generate(agent):
            result = Runner.run_sync(
                agent,
                prompt
            )

            return result.final_output

        # Try the primary API key first
        try:
            roadmap_output = try_generate(roadmap_agent)

            st.session_state["roadmap_text"] = roadmap_output
            st.session_state["roadmap_goal"] = goal

        except Exception as e:

            err_str = str(e)

            # If the first key reaches its quota, use the second key
            if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:

                if GEMINI_KEY_2:
                    st.info(
                        "First key's quota is used up — trying the backup key..."
                    )

                    try:
                        backup_agent = build_agent(GEMINI_KEY_2)

                        roadmap_output = try_generate(
                            backup_agent
                        )

                        st.session_state["roadmap_text"] = roadmap_output
                        st.session_state["roadmap_goal"] = goal

                    except Exception:
                        st.error(
                            "Both API keys have used up today's free quota. "
                            "Please try again later."
                        )

                else:
                    st.error(
                        "Daily free quota for the AI model has been used up. "
                        "Please try again later."
                    )

            # If the model is unavailable, try the lighter fallback model
            elif "UNAVAILABLE" in err_str or "503" in err_str:

                st.info(
                    "The main model is busy — trying a backup model..."
                )

                try:
                    fallback_agent = build_agent(
                        GEMINI_KEY_1,
                        model_name="gemini-3.1-flash-lite"
                    )

                    roadmap_output = try_generate(
                        fallback_agent
                    )

                    st.session_state["roadmap_text"] = roadmap_output
                    st.session_state["roadmap_goal"] = goal

                except Exception:
                    st.error(
                        "The AI models are busy right now. "
                        "Please click 'Generate Roadmap' again in a moment."
                    )

            # Handle unexpected errors
            else:
                st.error(
                    "Something went wrong. Please try again."
                )


# Display the roadmap after it has been generated
if "roadmap_text" in st.session_state:

    st.write(
        "Your goal:",
        st.session_state["roadmap_goal"]
    )

    days_dict = parse_roadmap_into_days(
        st.session_state["roadmap_text"]
    )

    # Show each day inside an expandable section
    if days_dict:

        for day_title, tasks in days_dict.items():

            with st.expander(
                f"📘 {day_title}"
            ):

                for task in tasks:
                    st.markdown(
                        f"- {task}"
                    )

    else:
        st.write(
            st.session_state["roadmap_text"]
        )

    # Let the user choose the PDF file name
    file_name_input = st.text_input(
        "Name your roadmap file (without .pdf)",
        value="learning_roadmap"
    )

    # FIX: hyphen moved to the end of the character class so it is
    # treated as a literal "-" and not as a range (the old "_- " was
    # an invalid range from "_" down to a space).
    safe_name = re.sub(
        r"[^A-Za-z0-9_ -]",
        "",
        file_name_input
    ).strip()

    if not safe_name:
        safe_name = "learning_roadmap"

    # Generate the PDF
    pdf_bytes = generate_pdf(
        st.session_state["roadmap_text"],
        st.session_state["roadmap_goal"]
    )

    # Provide the PDF download button
    st.download_button(
        label="📄 Download Roadmap as PDF",
        data=pdf_bytes,
        file_name=f"{safe_name}.pdf",
        mime="application/pdf"
    )