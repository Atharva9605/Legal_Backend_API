from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime
import traceback
import json
from typing import List, Dict, Any

# Import your existing components
from reflexion_graph import app as legal_agent_app
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from schema import AnswerQuestion, ReviseAnswer

# Initialize Flask app
app = Flask(__name__)

# Configure CORS for your frontend
CORS(app, origins=[
    "http://localhost:3000",  # Local development
    "https://your-frontend-domain.vercel.app",  # Production frontend
    "*"  # Allow all for now, restrict in production
])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store chat sessions (use Redis/Database in production)
chat_sessions = {}

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Legal Advisor API",
        "timestamp": datetime.now().isoformat(),
        "agent_status": "ready",
        "version": "1.0.0"
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint - compatible with your existing frontend"""
    try:
        # Get message from request (handle both string and JSON)
        data = request.get_json() if request.is_json else None
        
        if data is None:
            # Try to get raw text
            message = request.data.decode('utf-8')
        elif isinstance(data, str):
            message = data
        elif isinstance(data, dict):
            message = data.get('message', data.get('text', ''))
        else:
            return jsonify({"error": "Invalid input format"}), 400

        if not message:
            return jsonify({"error": "No message provided"}), 400

        logger.info(f"Received chat message: {message[:100]}...")

        # Get session ID
        session_id = 'default'
        if isinstance(data, dict):
            session_id = data.get('session_id', 'default')
        
        # Initialize session if not exists
        if session_id not in chat_sessions:
            chat_sessions[session_id] = {
                "messages": [],
                "created_at": datetime.now().isoformat()
            }

        # Add user message to session
        user_message = {
            "text": message,
            "sender": "user",
            "timestamp": datetime.now().isoformat()
        }
        chat_sessions[session_id]["messages"].append(user_message)

        # Invoke your LangGraph agent
        logger.info("Invoking LangGraph legal advisor agent...")
        response = legal_agent_app.invoke(message)
        
        # Extract the final answer from the response
        ai_response = extract_final_answer(response)
        
        # Add AI response to session
        ai_message = {
            "text": ai_response,
            "sender": "ai",
            "timestamp": datetime.now().isoformat(),
            "iteration": 1
        }
        chat_sessions[session_id]["messages"].append(ai_message)

        logger.info("Successfully generated legal analysis")
        
        # Return response in format expected by frontend
        return jsonify({
            "response": ai_response,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Internal server error", 
            "message": "Failed to process legal query"
        }), 500

@app.route('/revise', methods=['POST'])
def revise():
    """Revision endpoint - compatible with your existing frontend"""
    try:
        # Get the revision request
        data = request.get_json() if request.is_json else None
        
        if data is None:
            revision_input = request.data.decode('utf-8')
        elif isinstance(data, str):
            revision_input = data
        elif isinstance(data, dict):
            revision_input = data.get('message', data.get('text', ''))
        else:
            return jsonify({"error": "Invalid input format"}), 400

        if not revision_input:
            return jsonify({"error": "No revision input provided"}), 400

        logger.info(f"Received revision request: {revision_input[:100]}...")

        # Parse the original message and critique
        # Expected format: "original_message\nCritique: critique_text"
        if "Critique:" in revision_input:
            parts = revision_input.split("Critique:")
            original_message = parts[0].strip()
            critique = parts[1].strip()
        else:
            original_message = revision_input
            critique = "Please improve and enhance the response"

        # Create revision prompt
        revision_prompt = f"""Original legal query: {original_message}

User feedback for improvement: {critique}

Please revise your previous legal analysis based on this feedback, maintaining the comprehensive format but addressing the specific concerns raised."""

        # Invoke your LangGraph agent for revision
        logger.info("Invoking LangGraph agent for revision...")
        response = legal_agent_app.invoke(revision_prompt)
        
        # Extract the revised answer
        revised_response = extract_final_answer(response)
        
        logger.info("Successfully generated revised legal analysis")
        
        # Return response in format expected by frontend
        return jsonify({
            "response": revised_response,
            "original": original_message,
            "critique": critique,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in revise endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Internal server error",
            "message": "Failed to process revision request"
        }), 500

@app.route('/sessions', methods=['GET'])
def get_sessions():
    """Get all chat sessions"""
    return jsonify({
        "sessions": {k: {"message_count": len(v["messages"]), "created_at": v["created_at"]} 
                    for k, v in chat_sessions.items()}
    })

@app.route('/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get specific chat session"""
    if session_id not in chat_sessions:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify({
        "session_id": session_id,
        "messages": chat_sessions[session_id]["messages"],
        "created_at": chat_sessions[session_id]["created_at"]
    })

@app.route('/export-chat', methods=['POST'])
def export_chat():
    """Export chat transcript"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        
        if session_id not in chat_sessions:
            return jsonify({"error": "Session not found"}), 404
        
        session = chat_sessions[session_id]
        
        # Create formatted transcript
        transcript = f"Legal Advisor Chat Session\nDate: {session['created_at']}\n\n"
        
        for msg in session['messages']:
            sender = "You" if msg['sender'] == 'user' else "Legal Advisor AI"
            transcript += f"[{msg['timestamp']}] {sender}:\n{msg['text']}\n\n"
        
        return jsonify({
            "transcript": transcript,
            "session_id": session_id,
            "message_count": len(session['messages'])
        })
    
    except Exception as e:
        logger.error(f"Error in export endpoint: {str(e)}")
        return jsonify({"error": "Failed to export chat"}), 500

def extract_final_answer(response: List[BaseMessage]) -> str:
    """Extract the final answer from LangGraph response"""
    try:
        # Get the last AI message
        last_message = response[-1]
        
        # Check if it has tool calls (AnswerQuestion or ReviseAnswer)
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            tool_call = last_message.tool_calls[0]
            if tool_call['name'] in ['AnswerQuestion', 'ReviseAnswer']:
                return tool_call['args']['answer']
        
        # Fallback to message content
        return last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    except Exception as e:
        logger.error(f"Error extracting answer: {str(e)}")
        return "I apologize, but I encountered an error processing your legal query. Please try again."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)