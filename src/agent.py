from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from .state import AgentState
from .nodes import research_node, profile_node, draft_node, critique_node

def should_revise(state: AgentState):
    """
    Determine if the draft needs revision.
    """
    feedback = state.get("critique_feedback", "")
    count = state.get("revision_count", 0)
    
    # If approved or max revisions reached, end
    if "Approve" in feedback or count >= 3:
        return "end"
    return "revise"

# Build the Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("research", research_node)
workflow.add_node("profile", profile_node)
workflow.add_node("draft", draft_node)
workflow.add_node("critique", critique_node)

# Add Edges
workflow.set_entry_point("research")
workflow.add_edge("research", "profile")
workflow.add_edge("profile", "draft")
workflow.add_edge("draft", "critique")

# Conditional Edge
workflow.add_conditional_edges(
    "critique",
    should_revise,
    {
        "end": END,
        "revise": "draft"
    }
)

# Compile
app = workflow.compile()

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = "Google DeepMind"
        
    print(f"Starting agent for target: {target}")
    
    initial_state = {"target_input": target, "revision_count": 0}
    
    for output in app.stream(initial_state):
        for key, value in output.items():
            print(f"Finished Node: {key}")
            # print(f"Output: {value}") # Optional: print full state updates
            
    print("\n--- FINAL OUTPUT ---")
    # We need to get the final state. Since stream yields updates, we might want to invoke it or capture the last state.
    # For simplicity in this script, we'll just run it.
    # To get the final result, we can use app.invoke
    final_state = app.invoke(initial_state)
    print(f"Draft Message:\n{final_state['draft_message']}")
    print(f"Critique: {final_state['critique_feedback']}")
