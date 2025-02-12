from typing import Annotated

from langchain_core.tools import tool
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import os
import tempfile
from datetime import datetime


class State(TypedDict):
    messages: Annotated[list, add_messages]


@tool
def get_time_series_data(start_date, end_date) -> str:
    """Get time series data."""
    # generate random time series data between start_date and end_date
    df = pd.DataFrame(
        {"date": pd.date_range(start_date, end_date), "value": np.random.randn(10)}
    )
    data_dict = df.to_dict(orient="list")
    json_data = json.dumps(data_dict, default=str)
    return json_data


@tool
def plot_time_series_data(data: str) -> str:
    """Plot time series data. return a image in format of base64.
    Args:
        data: The data to plot.
    Returns:
        a message in markdown format, showing the plot of the time series data.
    """
    # plot time series data
    json_data = json.loads(data)
    df = pd.DataFrame(json_data)

    # Create plot
    plt.figure(figsize=(10, 6))
    df.plot(x="date", y="value")
    plt.title("Time Series Data")
    plt.xlabel("Date")
    plt.ylabel("Value")

    # Create temp directory if it doesn't exist
    temp_dir = os.path.join("./plots", "time_series_plots")
    os.makedirs(temp_dir, exist_ok=True)

    # Generate unique filename using timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"time_series_plot_{timestamp}.png"
    filepath = os.path.join(temp_dir, filename)

    # Save the plot
    plt.savefig(filepath)
    plt.close()

    return f"![Time Series Plot]({filepath})"


def get_graph(llm_client):
    graph_builder = StateGraph(State)
    tools = [get_time_series_data, plot_time_series_data]
    llm_with_tools = llm_client.bind_tools(tools)

    def chatbot(state: State):
        message = llm_with_tools.invoke(state["messages"])
        assert len(message.tool_calls) <= 1
        return {"messages": [message]}

    graph_builder.add_node("chatbot", chatbot)

    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")

    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)
    return graph
