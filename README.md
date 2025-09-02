# LangGraph Chatbot Deployment Guide

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment Variables
1. Create a `.env` file in your project root
2. Get your Groq API key from [Groq Console](https://console.groq.com/)
3. Add your API key to `.env`:
```
GROQ_API_KEY=your_actual_groq_api_key_here
```

### 3. Run Locally
```bash
streamlit run main.py
```

## 🛠️ Key Memory Fixes Applied

### Problem 1: Memory Not Persisting
**Solution:** 
- Added proper state retrieval using `graph.get_state(config)`
- Load existing conversation history on app startup
- Maintain thread-based memory separation

### Problem 2: Messages Not Being Stored in Memory
**Solution:**
- Pass messages correctly to the graph with proper config
- Use `add_messages` annotation properly in State
- Ensure HumanMessage objects are created correctly

### Problem 3: State Management Issues
**Solution:**
- Separate display history (Streamlit) from graph memory (LangGraph)
- Load memory state into display on startup
- Proper error handling for memory operations

## 🏗️ LangGraph Components Explained

### **Nodes**
- `chatbot_node`: Processes user input and generates AI responses
- Each node is a function that takes state and returns modified state

### **Edges**
- `START → chatbot → END`: Linear flow for simple chat
- Edges define the execution path through the graph

### **State**
- `TypedDict` with `messages` field
- `add_messages` annotation automatically appends new messages
- Maintains conversation context across interactions

### **Memory (MemorySaver)**
- Persists state between graph invocations
- Thread-based isolation using `thread_id`
- Automatic checkpointing after each node execution

## 🔗 MCP Protocol Integration

### Current Features:
- **Thread Management**: Each conversation has a unique thread ID
- **State Persistence**: Conversation history is maintained in memory
- **Export Functionality**: Conversations can be exported in structured format
- **Memory Inspection**: Debug view shows current memory state

### MCP Protocol Benefits:
- **Interoperability**: Standard format for AI conversation management
- **Persistence**: Conversations survive app restarts
- **Debugging**: Clear visibility into memory state
- **Extensibility**: Easy to add more MCP features

## 🌐 Streamlit Cloud Deployment

### Option 1: Streamlit Community Cloud
1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Set environment variables in the app settings:
   - `GROQ_API_KEY`: Your Groq API key
5. Deploy!

### Option 2: Local Development
```bash
# Clone and setup
git clone <your-repo>
cd langgraph-chatbot
pip install -r requirements.txt

# Add your .env file with API keys
# Run the app
streamlit run main.py
```

## 🐛 Troubleshooting Memory Issues

### If Memory Still Not Working:

1. **Check API Key**: Ensure Groq API key is correctly set
2. **Verify Thread ID**: Each conversation should have a unique thread_id
3. **Debug Mode**: Enable the debug checkbox to inspect memory state
4. **Check Logs**: Look for error messages in the Streamlit console

### Debug Commands:
```python
# Check if state exists
current_state = graph.get_state(config)
print(f"State exists: {current_state is not None}")

# Check message count
if current_state and current_state.values:
    print(f"Messages in memory: {len(current_state.values.get('messages', []))}")
```

## 📋 Project Structure
```
langgraph-chatbot/
├── main.py              # Main application
├── requirements.txt     # Dependencies
├── .env                # Environment variables (create this)
├── README.md           # This guide
└── .gitignore          # Git ignore file
```

## 🔧 Advanced Configuration

### Custom Memory Backends
Replace `MemorySaver()` with other checkpointers:
- `SqliteSaver()` for SQLite persistence
- `PostgresSaver()` for PostgreSQL
- Custom checkpointer implementations

### Enhanced MCP Features
- Add conversation search
- Implement conversation branching
- Add metadata tracking
- Export to different formats

## 🚨 Important Notes

- **Thread Isolation**: Each thread_id maintains separate conversation history
- **Memory Persistence**: Memory survives app restarts when using proper checkpointers
- **Error Handling**: Comprehensive error handling prevents crashes
- **State Management**: Clear separation between Streamlit state and LangGraph state

## 🎯 Success Verification

Your chatbot memory is working correctly when:
1. ✅ Previous messages appear when you refresh the page
2. ✅ Bot references earlier parts of the conversation
3. ✅ Memory metrics show increasing message counts
4. ✅ Debug view shows stored messages
5. ✅ New conversations start fresh with different thread IDs