from typing import List, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, ToolMessage
from langgraph.graph import END, StateGraph

from chains import revisor_chain, first_responder_chain
from execute_tools import execute_tools

load_dotenv()

class GraphState(TypedDict):
    messages: List[BaseMessage]

graph = StateGraph(GraphState)
MAX_ITERATIONS = 3

graph.add_node("draft", first_responder_chain)
graph.add_node("execute_tools", execute_tools)
graph.add_node("revisor", revisor_chain)

graph.add_edge("draft", "execute_tools")
graph.add_edge("execute_tools", "revisor")

def event_loop(state: GraphState) -> str:
    """
    Determine the next step in the graph execution.
    
    Args:
        state: Current graph state containing messages
        
    Returns:
        Next node to execute or END to terminate
    """
    messages = state.get("messages", [])
    
    if not messages:
        return END
    
    # Count tool messages to track iterations
    tool_messages = [msg for msg in messages if isinstance(msg, ToolMessage)]
    num_iterations = len(tool_messages)
    
    # Check if we've reached the maximum iterations
    if num_iterations >= MAX_ITERATIONS:
        return END
    
    # Check if the last message has tool calls that need processing
    last_message = messages[-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        # If there are tool calls, continue to execute_tools
        return "execute_tools"
    else:
        # If no tool calls, we're done
        return END

graph.add_conditional_edges("revisor", event_loop)
graph.set_entry_point("draft")

app = graph.compile()

# Test the graph structure
if __name__ == "__main__":
    print("🔍 Testing Graph Structure...")
    try:
        graph_structure = app.get_graph()
        print(f"✅ Graph compiled successfully")
        print(f"✅ Nodes: {list(graph_structure.nodes.keys())}")
        print(f"✅ Entry point: {graph_structure.entry_point}")
        print(f"✅ Conditional edges: {graph_structure.conditional_edges}")
    except Exception as e:
        print(f"❌ Graph compilation failed: {e}")
        import traceback
        traceback.print_exc()
