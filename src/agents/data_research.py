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
    """Get random time series data for a specified date range.

    Args:
        start_date: The start date for the time series data (format: 'YYYY-MM-DD')
        end_date: The end date for the time series data (format: 'YYYY-MM-DD')

    Returns:
        str: A JSON string containing the time series data with two keys:
            - 'date': List of dates between start_date and end_date
            - 'value': List of random values generated from standard normal distribution

    Example:
        >>> data = get_time_series_data('2024-01-01', '2024-01-10')
        >>> # Returns JSON string like:
        >>> # {"date": ["2024-01-01", "2024-01-02", ...], "value": [-0.5, 1.2, ...]}
    """
    # generate random time series data between start_date and end_date
    df = pd.DataFrame(
        {"date": pd.date_range(start_date, end_date), "value": np.random.randn(10)}
    )
    data_dict = df.to_dict(orient="list")
    json_data = json.dumps(data_dict, default=str)
    return json_data


@tool
def plot_time_series_data(data: str) -> str:
    """Plot time series data and save it as a PNG image.

    Args:
        data: JSON string containing time series data with two required keys:
            - 'date': List of dates in string format ('YYYY-MM-DD')
            - 'value': List of numerical values corresponding to each date

    Returns:
        str: Image file path: <plot>/path_to_plots/</plot>

    Example:
        >>> data = '{"date": ["2024-01-01", "2024-01-02"], "value": [1.2, -0.5]}'
        >>> path = plot_time_series_data(data)
        >>> # Returns something like: 'Image file path:<plot>/path/to/plots/plot_20240315_143022.png</plot>'

    Notes:
        - The plot is saved in a 'plots' directory relative to the current working directory
        - The filename includes a timestamp to ensure uniqueness
        - The plot includes a title, x-label (Date), and y-label (Value)
        - Figure dimensions are set to 10x6 inches
    """
    # plot time series data
    print("!!!!!plotting...")
    json_data = json.loads(data)
    df = pd.DataFrame(json_data)

    # Create plot
    plt.figure(figsize=(10, 6))
    df.plot(x="date", y="value")
    plt.title("Time Series Data")
    plt.xlabel("Date")
    plt.ylabel("Value")

    # Create plots directory if it doesn't exist
    plots_dir = os.path.abspath("./plots")
    os.makedirs(plots_dir, exist_ok=True)

    # Generate unique filename using timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"plot_{timestamp}.png"
    filepath = os.path.join(plots_dir, filename)

    print(f"Saving plot to {filepath}")
    # Save plot to file
    plt.savefig(filepath)
    plt.close()

    return f"Image file path:<plot>{filepath}</plot>"


def get_graph(llm_client):
    graph_builder = StateGraph(State)
    tools = [get_time_series_data, plot_time_series_data]
    llm_with_tools = llm_client.bind_tools(tools)

    def chatbot(state: State):
        message = llm_with_tools.invoke(state["messages"])
        # assert len(message.tool_calls) <= 1
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
