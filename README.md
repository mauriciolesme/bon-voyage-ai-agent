# Bon Voyage AI ✈️

A conversational AI travel assistant built with Streamlit and GPT-4o-mini. Bon Voyage AI helps users plan trips by recommending destinations based on their budget, nationality, travel goals, and travel month, then generating a personalized travel brief with live data.

## What It Does

Bon Voyage AI follows a two-step conversation flow:

**Step 1 — Destination Discovery:** The user provides their nationality, travel goal, budget, travel month, and trip duration. Ivan (the AI assistant) recommends 3-4 budget-compatible destinations and asks the user to pick one.

**Step 2 — Personalized Travel Brief:** Once a destination is confirmed, Ivan calls live APIs to retrieve weather, country info, and exchange rates, then generates a full travel brief covering weather, budget breakdown, payment norms, itinerary, cultural tips, basic phrases, food culture, safety tips, visa requirements, transportation, connectivity, and local events.

## Tech Stack

- **Frontend:** Streamlit
- **LLM:** GPT-4o-mini via OpenAI API
- **RAG:** FAISS vector database with LangChain and OpenAI embeddings
- **Tools:**
  - `get_weather` — OpenWeatherMap API
  - `get_country_info` — REST Countries API (free, no key needed)
  - `get_exchange_rate` — ExchangeRate API

## RAG System

The app uses a Retrieval-Augmented Generation (RAG) system to enhance Ivan's responses with curated destination knowledge that goes beyond the LLM's general training data.

**What's stored in RAG:**
- Destination mini-profiles (~10 per region) covering must-try food, neighborhoods, local transportation, activities, and budget context
- Safety tips and scam warnings specific to each destination

**Regions covered:** North America, Canada, Mexico, South America, Africa, Europe, Asia, Oceania

The FAISS index is built by running `build_faiss_index.py`, which loads JSON files from the `rag_files/` folder, flattens them into text chunks, embeds them using OpenAI embeddings, and saves the index locally.

## Project Structure

```
bon-voyage-ai-agent/
├── app.py                  # Streamlit frontend
├── bon_voyage_step3.py     # Agent logic, tools, RAG integration
├── bon_voyage_tools.py     # Tool definitions (weather, country info, exchange rate)
├── build_faiss_index.py    # Script to build the FAISS index from JSON files
├── faiss_index/            # Saved FAISS vector index
├── rag_files/              # Destination JSON knowledge base
├── images/                 # UI images (background, logo, icon)
├── requirements.txt
└── .streamlit/
    └── secrets.toml        # API keys (not committed to GitHub)
```

## Setup & Running Locally

1. Clone the repository
2. Create a virtual environment and install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_key
   OPENWEATHERMAP_API_KEY=your_key
   EXCHANGERATE_API_KEY=your_key
   ```
4. Build the FAISS index (run once):
   ```
   python build_faiss_index.py
   ```
5. Launch the app:
   ```
   streamlit run app.py
   ```

## APIs Used

| API | Purpose | Free Tier |
|-----|---------|-----------|
| OpenAI | LLM + embeddings | Pay per use |
| OpenWeatherMap | Live weather data | Yes |
| REST Countries | Country info | Yes (no key needed) |
| ExchangeRate-API | Currency exchange rates | Yes |
