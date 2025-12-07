from typing import TypedDict, Optional

class AgentState(TypedDict):
    target_input: str
    model_name: str
    research_summary: Optional[str]
    prospect_profile: Optional[dict]
    draft_message: Optional[str]
    critique_feedback: Optional[str]
    revision_count: int
    outreach_method: str
    website: Optional[str]
    custom_instructions: Optional[str]
