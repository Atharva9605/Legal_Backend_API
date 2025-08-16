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
    count_tool_visits = sum(isinstance(item, ToolMessage) for item in state["messages"])
    num_iterations = count_tool_visits
    if num_iterations > MAX_ITERATIONS:
        return END
    return "execute_tools"

graph.add_conditional_edges("revisor", event_loop)
graph.set_entry_point("draft")

app = graph.compile()

# Remove or comment out the test execution:
# print(app.get_graph().draw_mermaid())
# response = app.invoke({"messages": ["test case..."]})
# print(response["messages"][-1].tool_calls[0]["args"]["answer"])