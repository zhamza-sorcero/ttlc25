import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory

def load_csv_data():
    try:
        with open('ttlc25.csv', 'r') as file:
            return file.read()
    except Exception as e:
        st.error(f"Error loading CSV data: {str(e)}")
        return None

def setup_language_model():
    try:
        return ChatOpenAI(temperature=0, model="gpt-4o-mini")
    except Exception as e:
        st.error(f"Error initializing language model: {str(e)}")
        return None

def create_agent(csv_string, llm):
    if csv_string is None or llm is None:
        return None
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    return initialize_agent(
        [], 
        llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        memory=st.session_state.memory,
        agent_kwargs={
            "system_message": f"You are an AI assistant that helps users analyze the following CSV data:\n\n{csv_string}\n\nAnswer user questions about this data."
        }
    )

def display_chat_interface(agent):
    st.title("Chat with TTLC Conference 2025 Data")
    
    # Custom CSS for chat interface
    st.markdown('''
        <style>
        .chat-message {
            padding: 0.8rem;
            border-radius: 0.8rem;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: flex-start;
            gap: 0.5rem;
        }
        .chat-message.user {
            background-color: #e3f2fd;
            margin-left: 1rem;
            margin-right: 0.5rem;
            border: 1px solid #bbdefb;
        }
        .chat-message.bot {
            background-color: #f5f5f5;
            margin-right: 1rem;
            margin-left: 0.5rem;
            border: 1px solid #e0e0e0;
        }
        .chat-message .avatar {
            width: 2.5rem;
            height: 2.5rem;
            flex-shrink: 0;
        }
        .chat-message .avatar img {
            width: 100%;
            height: 100%;
            border-radius: 0.4rem;
            object-fit: cover;
        }
        .chat-message .message {
            flex-grow: 1;
            padding: 0 0.2rem;
            color: #212121;
            line-height: 1.5;
            font-size: 0.95rem;
        }
        </style>
    ''', unsafe_allow_html=True)
    
    # HTML templates for chat messages
    bot_template = '''
    <div class="chat-message bot">
        <div class="avatar">
            <img src="https://i.ibb.co/jMf7sB0/idea.png" alt="Bot">
        </div>
        <div class="message">{{MSG}}</div>
    </div>
    '''

    user_template = '''
    <div class="chat-message user">
        <div class="avatar">
            <img src="https://i.ibb.co/TcgRhzg/question-mark.png" alt="User">
        </div>    
        <div class="message">{{MSG}}</div>
    </div>
    '''
    
    if agent is None:
        st.warning("Chat functionality is currently unavailable. Please check your configuration.")
        return
        
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(user_template.replace("{{MSG}}", message["content"]), unsafe_allow_html=True)
        else:
            st.markdown(bot_template.replace("{{MSG}}", message["content"]), unsafe_allow_html=True)

    # Handle new user input
    if prompt := st.chat_input("Ask a question about the TTLC Conference data"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(user_template.replace("{{MSG}}", prompt), unsafe_allow_html=True)

        response = agent.run(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.markdown(bot_template.replace("{{MSG}}", response), unsafe_allow_html=True)

def display_chat_tab():
    # Create sidebar
    with st.sidebar:
        st.title("Chat Info")
        st.markdown("""
        This chatbot helps you analyze:
        - Conference attendance
        - Session popularity
        - Speaker statistics
        - Attendee feedback
        - Event metrics
        
        Based on TTLC Conference 2025 data
        """)
        
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # Main content
    csv_string = load_csv_data()
    llm = setup_language_model()
    agent = create_agent(csv_string, llm)
    display_chat_interface(agent)
