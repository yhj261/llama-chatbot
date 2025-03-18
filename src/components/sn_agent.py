import streamlit as st
import pandas as pd
import json
import os
import tempfile


def process_csv_data(csv_path, ticker_name, start_date, end_date):
    """
    Process CSV data according to specified parameters:
    1. Read data from CSV file
    2. Set the "date" column as index
    3. Select a specific column based on ticker_name
    4. Rename that column to "value"
    5. Filter data between start_date and end_date

    Args:
        csv_path (str): Path to the CSV file
        ticker_name (str): Name of the column to select
        start_date (str): Start date for filtering in YYYY-MM-DD format
        end_date (str): End date for filtering in YYYY-MM-DD format

    Returns:
        pandas.DataFrame: Processed DataFrame
    """
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)

        # Convert date column to datetime and set as index
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)

        # Select the specified column and rename it
        df = df[[ticker_name]].rename(columns={ticker_name: "value"})

        # Filter data between start and end dates
        df = df.loc[start_date:end_date]

        return df
    except Exception as e:
        st.error(f"Error processing CSV: {str(e)}")
        return None


def render_sn_agent_interface():
    """
    Render the SN Agent interface with two columns:
    1. First column: Text area and multiselect list
    2. Second column: Space for JSON/DataFrame display
    """
    st.title("SN Agent")
    st.write("Select parameters and analyze data")

    # Initialize ticker options in session state if not present
    if "sn_ticker_options" not in st.session_state:
        st.session_state.sn_ticker_options = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "META",
            "TSLA",
            "NVDA",
            "JPM",
            "BAC",
            "V",
        ]

    # Create two columns for the main layout
    col1, col2 = st.columns(2)

    # First column - Input controls
    with col1:
        st.subheader("Input Parameters")

        # Add a large text area at the top for notes, queries, etc.
        notes = st.text_area(
            "Notes/Query",
            height=150,
            placeholder="Enter your notes, queries, or additional information here...",
            help="Use this area for any notes, analysis instructions, or additional context",
        )

        if "sn_notes" not in st.session_state or st.session_state.sn_notes != notes:
            st.session_state.sn_notes = notes

        # Add a separator
        st.markdown("---")

        # Select all / Deselect all buttons
        button_col1, button_col2 = st.columns(2)
        with button_col1:
            if st.button("Select All"):
                st.session_state.selected_tickers = (
                    st.session_state.sn_ticker_options.copy()
                )
                st.rerun()
        with button_col2:
            if st.button("Deselect All"):
                st.session_state.selected_tickers = []
                st.rerun()

        # Ticker selection with multiselect - default to all selected
        if "selected_tickers" not in st.session_state:
            st.session_state.selected_tickers = (
                st.session_state.sn_ticker_options.copy()
            )

        selected_tickers = st.multiselect(
            "Select Tickers",
            st.session_state.sn_ticker_options,
            default=st.session_state.selected_tickers,
        )
        st.session_state.selected_tickers = selected_tickers

        # Option to add custom tickers - no nested columns
        add_ticker_col1, add_ticker_col2 = st.columns([3, 1])

        with add_ticker_col1:
            custom_ticker = st.text_input(
                "Add Custom Ticker", placeholder="Enter ticker symbol"
            )

        with add_ticker_col2:
            if custom_ticker and st.button("Add", key="add_ticker_btn"):
                if custom_ticker not in st.session_state.sn_ticker_options:
                    st.session_state.sn_ticker_options.append(custom_ticker)
                    # Also select the newly added ticker
                    if "selected_tickers" not in st.session_state:
                        st.session_state.selected_tickers = []
                    st.session_state.selected_tickers.append(custom_ticker)
                    st.rerun()
                else:
                    st.warning(f"Ticker '{custom_ticker}' already exists!")

        # Section to manage custom tickers
        if (
            len(st.session_state.sn_ticker_options) > 10
        ):  # Only show if custom tickers have been added
            st.subheader("Manage Custom Tickers")

            # Get only the custom tickers (those beyond the original 10)
            custom_tickers = st.session_state.sn_ticker_options[10:]

            if custom_tickers:
                # Create a selection for tickers to remove
                tickers_to_remove = st.multiselect(
                    "Select custom tickers to remove", custom_tickers
                )

                if tickers_to_remove and st.button("Remove Selected Tickers"):
                    for ticker in tickers_to_remove:
                        if ticker in st.session_state.sn_ticker_options:
                            st.session_state.sn_ticker_options.remove(ticker)
                            # Also remove from selected tickers if present
                            if ticker in st.session_state.selected_tickers:
                                st.session_state.selected_tickers.remove(ticker)
                    st.rerun()

        # Date range selection - use columns with no nesting
        date_col1, date_col2 = st.columns(2)
        with date_col1:
            start_date = st.date_input("Start Date")
        with date_col2:
            end_date = st.date_input("End Date")

        # Incorporate the notes into the processing if needed
        if st.button("Process Data", type="primary"):
            file_to_process = None

            # Get file path from session state (set in sidebar)
            if "sn_file_path" in st.session_state:
                file_to_process = st.session_state.sn_file_path

            if (
                file_to_process
                and st.session_state.selected_tickers
                and start_date
                and end_date
            ):
                try:
                    # Create empty dataframe to hold all processed ticker data
                    all_data = pd.DataFrame()

                    # If there are notes, you might want to display them or use them
                    if st.session_state.sn_notes:
                        st.info(f"Processing with notes: {st.session_state.sn_notes}")

                    for ticker in st.session_state.selected_tickers:
                        # Process each ticker
                        ticker_data = process_csv_data(
                            file_to_process,
                            ticker,
                            start_date.strftime("%Y-%m-%d"),
                            end_date.strftime("%Y-%m-%d"),
                        )

                        if ticker_data is not None:
                            # Rename value column to ticker name for clarity
                            ticker_data = ticker_data.rename(columns={"value": ticker})

                            # Add to all_data dataframe
                            if all_data.empty:
                                all_data = ticker_data
                            else:
                                all_data = pd.concat([all_data, ticker_data], axis=1)

                    if not all_data.empty:
                        # Store the result in session state so it can be displayed in column 2
                        st.session_state.sn_result_df = all_data
                        st.session_state.sn_result_json = all_data.to_json(
                            orient="records", date_format="iso"
                        )
                    else:
                        st.error(
                            "No data was processed. Please check your file path and parameters."
                        )

                    # Clean up temp file if used
                    if "sn_temp_file" in st.session_state and os.path.exists(
                        st.session_state.sn_temp_file
                    ):
                        os.unlink(st.session_state.sn_temp_file)
                        st.session_state.sn_temp_file = None

                except Exception as e:
                    st.error(f"Error processing data: {str(e)}")
            else:
                st.warning("Please fill in all required fields and provide a CSV file")

    # Second column - Results display
    with col2:
        st.subheader("Results")

        # You might want to display the notes here as well for reference
        if "sn_notes" in st.session_state and st.session_state.sn_notes:
            with st.expander("View Notes", expanded=False):
                st.markdown(st.session_state.sn_notes)

        # Display tabs for different output formats
        tab1, tab2, tab3 = st.tabs(["DataFrame", "JSON", "Chart"])

        with tab1:
            if "sn_result_df" in st.session_state:
                st.dataframe(st.session_state.sn_result_df)
            else:
                st.info("Process data to see results here")

        with tab2:
            if "sn_result_json" in st.session_state:
                st.json(json.loads(st.session_state.sn_result_json))
            else:
                st.info("Process data to see JSON here")

        with tab3:
            if (
                "sn_result_df" in st.session_state
                and not st.session_state.sn_result_df.empty
            ):
                st.line_chart(st.session_state.sn_result_df)
            else:
                st.info("Process data to see chart here")


def create_sample_data(tickers, start_date, end_date):
    """Create sample data for demonstration purposes"""
    # Convert dates to pandas datetime
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    # Create a date range
    date_range = pd.date_range(start=start, end=end, freq="D")

    # Create empty dataframe with date as index
    df = pd.DataFrame(index=date_range)
    df.index.name = "date"

    # Add data for each selected ticker
    import numpy as np

    for ticker in tickers:
        # Generate random data for demonstration
        df[ticker] = np.random.normal(100, 10, len(date_range)).cumsum()

    return df
