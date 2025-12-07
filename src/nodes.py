from langchain_community.tools.tavily_search import TavilySearchResults

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
import json
import os
from .state import AgentState

from langchain_groq import ChatGroq

# Initialize LLM Helper
def get_llm(model_name: str = "llama-3.3-70b-versatile"):
    return ChatGroq(
        model=model_name,
        api_key=os.getenv("GROQ_API_KEY")
    )

def research_node(state: AgentState):
    """
    Research the target using Tavily Search.
    """
    target = state["target_input"]
    model_name = state.get("model_name", "llama-3.3-70b-versatile")
    llm = get_llm(model_name)
    
    print(f"--- RESEARCHING: {target} ---")
    
    # Auto-detect if input is a website
    is_website = False
    if "http" in target or "www." in target or any(target.endswith(ext) for ext in [".com", ".org", ".net", ".io", ".ai", ".co"]):
        is_website = True
        
    search_query = target
    if is_website:
        search_query = f"site:{target} OR {target}"
    
    search = TavilySearchResults(max_results=3)
    search_results = search.invoke(search_query)
    
    # Simple synthesis of results
    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a lead researcher. Summarize the following search results for {target}. Focus on recent news, key decision makers, and company mission."),
        ("user", "Search Results: {results}")
    ])
    
    chain = summary_prompt | llm
    summary = chain.invoke({"target": target, "results": search_results})
    
    return {"research_summary": summary.content}

def profile_node(state: AgentState):
    """
    Create a structured profile from the research summary.
    """
    print(f"--- PROFILING ---")
    research_summary = state["research_summary"]
    model_name = state.get("model_name", "llama-3.3-70b-versatile")
    llm = get_llm(model_name)
    
    profile_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert profiler. Extract key information from the research summary into a JSON format with keys: 'company_name', 'industry', 'key_contacts', 'pain_points', 'achievements', 'hooks'."),
        ("user", "Research Summary: {summary}")
    ])
    
    chain = profile_prompt | llm
    response = chain.invoke({"summary": research_summary})
    
    # Clean up the response to ensure it's valid JSON if the LLM wraps it in markdown
    content = response.content.strip()
    if content.startswith("```json"):
        content = content[7:-3]
    elif content.startswith("```"):
        content = content[3:-3]
        
    try:
        profile = json.loads(content)
    except json.JSONDecodeError:
        profile = {"raw_profile": content}
        
    return {"prospect_profile": profile}

def draft_node(state: AgentState):
    """
    Draft an outreach message.
    """
    print(f"--- DRAFTING ---")
    profile = state["prospect_profile"]
    model_name = state.get("model_name", "llama-3.3-70b-versatile")
    outreach_method = state.get("outreach_method", "Email")
    custom_instructions = state.get("custom_instructions", "")
    llm = get_llm(model_name)
    
    # Method specific guidelines
    guidelines = {
        "LinkedIn": "Keep it professional but conversational. Limit to 3-4 sentences. Focus on mutual interests or professional synergy.",
        "WhatsApp": "Keep it short, direct, and casual. No formal salutations (e.g. Dear X). Use emojis sparingly.",
        "Email": "Use a standard professional email format with a clear subject line. Keep it under 200 words."
    }
    
    method_instruction = guidelines.get(outreach_method, guidelines["Email"])
    
    # Build custom instructions section
    custom_section = ""
    if custom_instructions and custom_instructions.strip():
        custom_section = f"\n\nAdditional User Instructions: {custom_instructions}"
    
    draft_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a top-tier copywriter. Write a personalized {outreach_method} message to a key contact at the company. Use the 'hooks' from the profile to make it relevant. \n\nGuidelines: {method_instruction}{custom_section}"),
        ("user", "Prospect Profile: {profile}")
    ])
    
    chain = draft_prompt | llm
    draft = chain.invoke({"profile": json.dumps(profile), "outreach_method": outreach_method, "method_instruction": method_instruction, "custom_section": custom_section})
    
    return {"draft_message": draft.content, "revision_count": state.get("revision_count", 0) + 1}

def critique_node(state: AgentState):
    """
    Critique the draft message.
    """
    print(f"--- CRITIQUING ---")
    draft = state["draft_message"]
    profile = state["prospect_profile"]
    model_name = state.get("model_name", "llama-3.3-70b-versatile")
    llm = get_llm(model_name)
    
    critique_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a strict editor. Review the draft email. Does it mention specific research? Is it concise? If it's good, respond with 'Approve'. If not, provide specific feedback for improvement."),
        ("user", "Draft: {draft}\n\nProfile: {profile}")
    ])
    
    chain = critique_prompt | llm
    feedback = chain.invoke({"draft": draft, "profile": json.dumps(profile)})
    
    return {"critique_feedback": feedback.content}
