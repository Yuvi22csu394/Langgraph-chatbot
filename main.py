# main.py
# Project: LangGraph Chatbot with Working Memory and MCP Protocol Support

import os
import streamlit as st
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
import uuid

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage

# ---------------------------
# Load environment variables
# ---------------------------
# Try to load .env file (for local development)
try:
    load_dotenv()
except:
    pass  # .env file not required for Streamlit Cloud

# Get API key from environment or Streamlit secrets
groq_api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not groq_api_key:
    st.error("🔑 **API Key Required!**")
    st.write("Please set your Groq API key in one of these ways:")
    st.write("1. **Streamlit Cloud**: Add `GROQ_API_KEY` in App Settings → Secrets")
    st.write("2. **Local Development**: Create `.env` file with `GROQ_API_KEY=your_key`")
    st.write("3. **Get API Key**: Visit [Groq Console](https://console.groq.com/)")
    st.stop()

# Set the API key in environment
os.environ["GROQ_API_KEY"] = groq_api_key

# Initialize LLM (Groq)
try:
    llm = init_chat_model("groq:llama-3.1-8b-instant")
except Exception as e:
    st.error(f"Failed to initialize LLM: {e}")
    st.write("**Possible solutions:**")
    st.write("- Verify your Groq API key is correct")
    st.write("- Check your internet connection")
    st.write("- Try refreshing the page")
    st.stop()

# ---------------------------
# Define State
# ---------------------------
class State(TypedDict):
    messages: Annotated[list, add_messages]

# ---------------------------
# Node functions
# ---------------------------
def chatbot_node(state: State):
    """Main chatbot node that processes messages and generates responses"""
    try:
        # Get the current messages from state
        messages = state["messages"]
        
        # Invoke the LLM with all messages (maintains context)
        response = llm.invoke(messages)
        
        # Return the response as part of the state
        return {"messages": [response]}
    except Exception as e:
        error_msg = f"Error in chatbot processing: {str(e)}"
        return {"messages": [AIMessage(content=error_msg)]}

# ---------------------------
# Graph setup with MemorySaver
# ---------------------------
def create_graph():
    """Create and compile the LangGraph with memory"""
    graph_builder = StateGraph(State)
    
    # Add nodes
    graph_builder.add_node("chatbot", chatbot_node)
    
    # Add edges
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    
    # Compile with memory
    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)
    
    return graph

# Initialize graph
if "graph" not in st.session_state:
    st.session_state.graph = create_graph()

# ---------------------------
# MCP Protocol Support Functions
# ---------------------------
def get_conversation_history(thread_id: str):
    """Retrieve conversation history for MCP protocol"""
    try:
        config = {"configurable": {"thread_id": thread_id}}
        # Get the current state from memory
        current_state = st.session_state.graph.get_state(config)
        if current_state and current_state.values:
            return current_state.values.get("messages", [])
        return []
    except Exception as e:
        st.error(f"Error retrieving history: {e}")
        return []

def export_conversation(thread_id: str):
    """Export conversation in MCP-compatible format"""
    history = get_conversation_history(thread_id)
    conversation_data = {
        "thread_id": thread_id,
        "messages": [
            {
                "role": "human" if isinstance(msg, HumanMessage) else "assistant",
                "content": msg.content,
                "timestamp": getattr(msg, 'timestamp', None)
            }
            for msg in history
        ]
    }
    return conversation_data

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(
    page_title="LangGraph Chatbot", 
    page_icon="🤖", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    st.write("**LangGraph Chatbot**")
    st.markdown("---")
    
    # Thread management
    st.subheader("🧵 Conversation Management")
    
    # Display current thread ID
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    
    st.write(f"**Current Thread:** `{st.session_state.thread_id[:8]}...`")
    
    # New conversation button
    if st.button("🆕 New Conversation"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.display_history = []
        st.rerun()
    
    # Clear current conversation
    if st.button("🗑️ Clear Current Chat"):
        st.session_state.display_history = []
        st.rerun()
    
    st.markdown("---")
    
    # Memory info
    st.subheader("🧠 Memory Status")
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    try:
        current_state = st.session_state.graph.get_state(config)
        if current_state and current_state.values:
            msg_count = len(current_state.values.get("messages", []))
            st.success(f"✅ Memory Active: {msg_count} messages stored")
        else:
            st.info("📝 New conversation - no memory yet")
    except Exception as e:
        st.error(f"❌ Memory Error: {str(e)}")
    
    st.markdown("---")
    
    # MCP Protocol section
    st.subheader("🔗 MCP Protocol")
    if st.button("📥 Export Conversation"):
        try:
            conv_data = export_conversation(st.session_state.thread_id)
            st.json(conv_data)
        except Exception as e:
            st.error(f"Export failed: {e}")
    
    st.info("💡 **Features:**\n- Persistent memory across sessions\n- Thread-based conversations\n- MCP protocol support\n- Real-time memory status")

# Main title
st.markdown(
    """
    <div style='text-align: center; padding: 1rem;'>
        <h1 style='color: #4CAF50; margin-bottom: 0;'>🤖 LangGraph Chatbot</h1>
        <p style='color: #666; margin-top: 0;'>Built with LangGraph • Groq • Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Initialize display history
if "display_history" not in st.session_state:
    st.session_state.display_history = []

# Configuration for this thread
config = {"configurable": {"thread_id": st.session_state.thread_id}}

# Load existing conversation history on startup
if not st.session_state.display_history:
    try:
        existing_messages = get_conversation_history(st.session_state.thread_id)
        for msg in existing_messages:
            if isinstance(msg, HumanMessage):
                st.session_state.display_history.append(("user", msg.content))
            elif isinstance(msg, AIMessage):
                st.session_state.display_history.append(("assistant", msg.content))
    except Exception as e:
        st.error(f"Error loading conversation history: {e}")

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to display
    st.session_state.display_history.append(("user", user_input))
    
    try:
        # Create HumanMessage
        human_message = HumanMessage(content=user_input)
        
        # Get current state to retrieve existing conversation
        current_state = st.session_state.graph.get_state(config)
        existing_messages = []
        if current_state and current_state.values:
            existing_messages = current_state.values.get("messages", [])
        
        # Invoke graph with the new message
        # The graph will automatically add to existing messages due to add_messages annotation
        response = st.session_state.graph.invoke(
            {"messages": [human_message]}, 
            config=config
        )
        
        # Extract bot response
        if response and "messages" in response:
            bot_reply = response["messages"][-1].content
            st.session_state.display_history.append(("assistant", bot_reply))
        else:
            st.error("No response received from the chatbot")
            
    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        st.error(error_msg)
        st.session_state.display_history.append(("assistant", error_msg))

# Display chat messages
chat_container = st.container()
with chat_container:
    for role, message in st.session_state.display_history:
        if role == "user":
            with st.chat_message("user"):
                st.markdown(f"**You:** {message}")
        else:
            with st.chat_message("assistant"):
                st.markdown(f"**Assistant:** {message}")

# Footer with memory status
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💬 Messages", len(st.session_state.display_history))

with col2:
    try:
        current_state = st.session_state.graph.get_state(config)
        if current_state and current_state.values:
            memory_count = len(current_state.values.get("messages", []))
            st.metric("🧠 Memory", memory_count)
        else:
            st.metric("🧠 Memory", 0)
    except:
        st.metric("🧠 Memory", "Error")

with col3:
    st.metric("🧵 Thread", st.session_state.thread_id[:8] + "...")

# Debug section (optional - can be removed in production)
if st.checkbox("🔍 Debug Memory State"):
    try:
        current_state = st.session_state.graph.get_state(config)
        if current_state:
            st.json({
                "thread_id": st.session_state.thread_id,
                "state_values": str(current_state.values) if current_state.values else "None",
                "checkpoint_available": current_state is not None
            })
        else:
            st.write("No state found for current thread")
    except Exception as e:
        st.error(f"Debug error: {e}")
