# Research & Outreach Agent

A LangGraph-powered agent that researches prospects and generates personalized outreach messages.

## Tech Stack

- **LLM**: Groq (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`)
- **Search**: Tavily Search API
- **Framework**: LangGraph for agent orchestration
- **Frontend**: Streamlit

## Project Structure

```
src/
├── agent.py    # LangGraph workflow definition
├── nodes.py    # Node implementations (research, profile, draft, critique)
├── state.py    # AgentState TypedDict definition
└── app.py      # Streamlit UI
```

## Agent Flow

```
research → profile → draft → critique
                       ↑         │
                       └─────────┘ (revise if not approved, max 3 iterations)
```

## Environment Variables

- `GROQ_API_KEY` - Groq API key
- `TAVILY_API_KEY` - Tavily search API key

## Running the App

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run src/app.py
```

## Key Components

### State (`state.py`)
`AgentState` TypedDict with fields: `target_input`, `model_name`, `research_summary`, `prospect_profile`, `draft_message`, `critique_feedback`, `revision_count`, `outreach_method`, `website`, `custom_instructions`.

### Nodes (`nodes.py`)
- `research_node`: Tavily search + LLM summary
- `profile_node`: Extracts structured JSON profile
- `draft_node`: Generates outreach message (Email/LinkedIn/WhatsApp)
- `critique_node`: Reviews draft, approves or requests revision

### Workflow (`agent.py`)
Linear flow with conditional edge from `critique` back to `draft` for revisions.
