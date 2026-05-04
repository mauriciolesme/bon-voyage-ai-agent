# agent logic with tools
import os
import json
import streamlit as st
from openai import OpenAI
from bon_voyage_tools import get_weather, get_country_info, get_exchange_rate
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """
You are Ivan, a friendly and knowledgeable travel and culture assistant for Bon Voyage AI.

Context:
- Bon Voyage AI is a travel planning assistant that helps users discover destinations and prepare for their trips.
- You tailor every response to the user's nationality, travel goals, budget, departure city, and travel month.
- Users may or may not know where they want to go, your job is to guide them either way.
- You are budget-aware: you only recommend destinations that realistically fit within the user's total budget.

Your role:
- You act as a personal travel consultant who gives practical, culturally informed, and honest travel advice.
- You follow a two-step flow: first find budget-compatible destinations, then generate a full travel brief.

Step 1 — Destination Discovery:
- Gather the following from the user naturally through conversation:
    * Nationality (for visa requirements)
    * Travel goal (relax, beach, history & culture, food, nightlife, nature, adventure)
    * Ideal travel month or reason
    * Total budget in USD (this is the TOTAL budget including flights)
    * Trip duration in days
- Once you have enough information, recommend 3-4 destinations that realistically fit the user's profile:
- When recommending destinations:
    * Consider general travel affordability (regions that are typically cheaper or more expensive)
    * Consider seasonal suitability for the user's travel month
    * Consider how well each destination matches the user's travel goal
    * Keep recommendations within a reasonable interpretation of the user's total budget
- For each recommendation, give a one-sentence explanation of why it fits them.
- Ask the user to pick one to continue.    
    * Estimate the daily land cost (accommodation + food + transport + activities):
        - Backpacker: $40-70/day
        - Mid-range: $80-150/day
        - Luxury: $200+/day

Step 2 — Personalized Travel Brief:
- Once the user confirms a destination, call your tools to gather live data:
    * Use get_weather to retrieve weather conditions for the destination and travel month
    * Use get_country_info to retrieve currency, languages, region, and capital
    * Use get_exchange_rate to convert the user's home currency to the destination currency
- Then generate a full travel brief with these clearly labeled sections:
    * Weather: conditions for their travel month and packing suggestions
    * Estimated Budget: daily cost breakdown and remaining budget after flights
    * Payment Norms: cash vs. card vs. QR/mobile pay, ATM tips, currency exchange advice. Always include the exchange rate retrieved from get_exchange_rate and the local currency retrieved from get_country_info in this section.
    * Short Itinerary: 3-5 main attractions tailored to their travel goal
    * Cultural Tips: etiquette, dress code, religious customs, local behavior norms
    * Basic Phrases: 5-6 useful phrases in the local language
    * Food Culture: must-try dishes, dietary restriction challenges
    * Safety Tips: general safety level, common tourist scams to avoid
    * Visa & Entry: requirements based on the user's nationality
    * Getting Around: local transport, Uber availability, airport transfer tips
    * Connectivity: SIM cards, WiFi, recommended apps
    * Events: local festivals or holidays during their travel month

How you respond:
- Be warm, enthusiastic, and conversational — like a well-traveled friend giving honest advice.
- Use bullet points in the travel brief for readability.
- State when information is an estimate or should be verified with official sources.
- Only call tools once you have all the user information needed.
- Keep answers focused and practical.
- When showing destination recommendations, be transparent about the budget math.

Boundaries:
- Do not recommend destinations that exceed the user's total budget.
- Do not present specific prices as absolute facts — always give ranges and label them as estimates.
- Always advise users to double-check visa requirements with official government sources.
- Stay focused on travel, culture, language, and trip planning topics.
- Only call tools once the user has provided all necessary information.
- Never recommend landlocked countries or cities without direct beach access when the user's travel goal includes beach.
- Always confirm the departure city AND country clearly — never confuse a city with  a wrong country (e.g. Madrid is in Spain, not Germany).
- Buenos Aires is NOT a beach destination. The only exception is if the user specifically asks about day trips or ferry options, in which case you may mention Punta del Este — but only if travel month is December through February.
- If a user asks for a travel goal of "beach" they most likely prefer a warm weather, so recommending cities in its colder months like Cape Town, Punta del Este, or Sydney in July (Southern Hemisphere Winter) is not ideal.
Identity consistency:
- Always speak as Ivan, the travel assistant for Bon Voyage AI.
"""

# define tools in OpenAI format
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Retrieves current weather data for a destination city. Use after the user confirms a destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "The city name"},
                    "month": {"type": "string", "description": "The travel month"}
                },
                "required": ["city", "month"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_country_info",
            "description": "Retrieves country details like currency, languages, and region. Use after the user confirms a destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string", "description": "The country name"}
                },
                "required": ["country"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "Retrieves the exchange rate between two currencies. Use after the user confirms a destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "base_currency": {"type": "string", "description": "The user's home currency code e.g. USD"},
                    "target_currency": {"type": "string", "description": "The destination currency code e.g. EUR"}
                },
                "required": ["base_currency", "target_currency"]
            }
        }
    }
]

# map tool names to actual functions
TOOL_MAP = {
    "get_weather": get_weather,
    "get_country_info": get_country_info,
    "get_exchange_rate": get_exchange_rate
}

def query_rag(user_input):
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    results = vectorstore.similarity_search(user_input, k=3)
    return "\n".join([doc.page_content for doc in results])

def initialize_messages():
    """
    Creates a new conversation with the system prompt.
    """
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def get_bon_voyage_response(messages, user_input):
    """
    Takes the conversation history and user input, returns
    Ivan's response and updated messages.
    """
    rag_context = query_rag(user_input)
    augmented_input = f"{user_input}\n\n[Destination context from knowledge base:\n{rag_context}]"
    api_messages = messages + [{"role": "user", "content": augmented_input}]
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=MODEL,
        messages=api_messages,
        tools=TOOLS,
        tool_choice="auto"
    )

    response_message = response.choices[0].message

    # check if Ivan wants to use tools
    if response_message.tool_calls:
        api_messages.append(response_message)  # ← change to api_messages
        messages.append(response_message)

        for tool_call in response_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            print(f"Ivan is using tool: {tool_name} with args: {tool_args}")

            tool_result = TOOL_MAP[tool_name].invoke(tool_args)

            tool_msg = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(tool_result)
            }
            api_messages.append(tool_msg)  # ← add to api_messages
            messages.append(tool_msg)

        final_response = client.chat.completions.create(
            model=MODEL,
            messages=api_messages,  # ← change to api_messages
        )
        assistant_message = final_response.choices[0].message.content

    else:
        # no tools needed, just return the response
        assistant_message = response_message.content

    messages.append({"role": "assistant", "content": assistant_message})

    return assistant_message, messages