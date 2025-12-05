import streamlit as st
import os
from dotenv import load_dotenv
import sys
# Add project root to path to allow importing from src package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent import app as agent_app

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Research & Outreach Agent", page_icon="🕵️‍♂️")

st.title("🕵️‍♂️ Research & Outreach Agent")
st.markdown("Enter a company or person's name to generate a personalized outreach message.")

# Input
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    target = st.text_input("Target Company / Person / Website", placeholder="e.g. SpaceX, Sam Altman, anthropic.com")
with col2:
    model_name = st.selectbox(
        "Select Model",
        options=[
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
        ],
        index=0
    )
with col3:
    outreach_method = st.selectbox(
        "Outreach Method",
        options=["Email", "LinkedIn", "WhatsApp"],
        index=0
    )

if st.button("Generate Outreach"):
    if not target:
        st.warning("Please enter a target.")
    else:
        if not os.getenv("GROQ_API_KEY"):
            st.error("Please set your GROQ_API_KEY in the .env file.")
        else:
            status_container = st.status("Agent Working...", expanded=True)
            
            try:
                initial_state = {
                    "target_input": target, 
                    "model_name": model_name, 
                    "outreach_method": outreach_method,
                    "revision_count": 0
                }
                final_state = None
                
                # Run the agent stream
                for output in agent_app.stream(initial_state):
                    for key, value in output.items():
                        if key == "research":
                            status_container.write("✅ Research Complete")
                            with st.expander("Research Summary"):
                                st.write(value.get("research_summary", ""))
                        elif key == "profile":
                            status_container.write("✅ Profiling Complete")
                            with st.expander("Prospect Profile"):
                                st.json(value.get("prospect_profile", {}))
                        elif key == "draft":
                            status_container.write("✅ Draft Generated")
                        elif key == "critique":
                            status_container.write(f"✅ Critique: {value.get('critique_feedback', '')}")
                
                status_container.update(label="Process Complete!", state="complete", expanded=False)
                
                # Get final state to display results
                # Note: The loop above iterates through updates. We can just invoke to get the final state cleanly 
                # or capture the last state from the loop. Invoking again might be redundant/expensive.
                # Let's just capture the data as it flows or run invoke once if we want simplicity.
                # Since we want to show intermediate steps, streaming is better. 
                # We can capture the final state from the last yield, but LangGraph stream yields node outputs.
                # Let's run invoke to get the final consolidated state for the final display, 
                # or better, just rely on the last node's output if possible. 
                # Actually, let's just use invoke for the final display to be safe and easy, 
                # although it re-runs. Wait, re-running is bad.
                # Better: Accumulate state manually or use the last output.
                # The 'value' in the loop is the update from the node.
                
                # Let's just run invoke for now to ensure we have the full final state, 
                # assuming the operations are idempotent enough or we accept the double cost for this MVP.
                # actually, let's NOT double invoke. It costs money.
                # We can just use a mutable dict to track state updates.
                
                current_state = initial_state.copy()
                # Re-running stream to capture state
                # Streamlit reruns the whole script on interaction, so this logic runs once per button click.
                # We need to capture the data from the stream we already ran above?
                # The loop above consumes the generator. We can't iterate it twice.
                # Let's refactor the loop to update a local state variable.
                
            except Exception as e:
                st.error(f"An error occurred: {e}")

            # Rerunning logic to capture state properly without double invoke
            # We will restart the process and capture state in the loop
            
            # Reset for the actual run
            status_container = st.empty() # Clear previous
            status_container = st.status("Agent Working...", expanded=True)
            
            current_state = initial_state.copy()
            
            try:
                for output in agent_app.stream(initial_state):
                    for key, value in output.items():
                        # Update current state with new values
                        current_state.update(value)
                        
                        if key == "research":
                            status_container.write("✅ Research Complete")
                            with st.expander("Research Summary"):
                                st.write(value.get("research_summary", ""))
                        elif key == "profile":
                            status_container.write("✅ Profiling Complete")
                            with st.expander("Prospect Profile"):
                                st.json(value.get("prospect_profile", {}))
                        elif key == "draft":
                            status_container.write("✅ Draft Generated")
                        elif key == "critique":
                            status_container.write(f"👀 Critique: {value.get('critique_feedback', '')}")
                            
                status_container.update(label="Process Complete!", state="complete", expanded=False)
                
                st.divider()
                st.subheader("Final Outreach Draft")
                st.text_area("Copy your message:", value=current_state.get("draft_message", ""), height=300)
                
                if "critique_feedback" in current_state:
                    st.info(f"Final Critique: {current_state['critique_feedback']}")
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")

# How to Use Section
st.markdown("---")
with st.expander("ℹ️ How to Use & What to Expect", expanded=False):
    st.markdown("""
    ### How to Use
    1. **Enter Target**: Type the name of a company (e.g., *SpaceX*), a person (e.g., *Sam Altman*), or a website URL (e.g., *anthropic.com*).
    2. **Select Model**: Choose the AI model you want to use for generation.
    3. **Choose Method**: Select how you plan to reach out (Email, LinkedIn, or WhatsApp).
    4. **Generate**: Click the button and watch the agent research, profile, and draft your message!

    ### Outreach Methods
    - **📧 Email**: Generates a professional, structured email with a clear subject line, suitable for formal business outreach.
    - **💼 LinkedIn**: Creates a concise, professional yet conversational message designed for direct messaging on LinkedIn.
    - **💬 WhatsApp**: Produces a short, casual, and direct message suitable for quick mobile communication.
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666;">
        Built with <span style="color: #ff4b4b;">&hearts;</span> by <a href="https://x.com/as1fansar1" target="_blank" style="text-decoration: none; color: #666; font-weight: bold;">Asif</a>
    </div>
    """,
    unsafe_allow_html=True
)
