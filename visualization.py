import pandas as pd
import plotly.express as px
import pandasql as psql

def execute_and_plot(json_config: dict, df: pd.DataFrame):
    """
    Takes the JSON dict from Gemini, runs the SQL via pandasql,
    and returns (fig, insight_text, result_df).
    """
    sql_query = json_config.get("sql", "ERROR")
    insight = json_config.get("insight", "")
    chart_type = json_config.get("chart_type", "none")
    x_axis = json_config.get("x_axis", "")
    y_axis = json_config.get("y_axis", "")

    # 1. Handle Gemini saying the query is unanswerable
    if sql_query == "ERROR":
        return None, insight, None

    # 2. Execute SQL
    try:
        # Pass only the specific dataframe context to avoid leaking locals() variables
        result_df = psql.sqldf(sql_query, {'df': df})
    except Exception as e:
        error_msg = f"⚠️ Could not execute SQL query. Error: {e}\n\nQuery was: `{sql_query}`"
        return None, error_msg, None

    # 3. Handle Visualization
    fig = None
    if chart_type != "none" and not result_df.empty:
        try:
            if chart_type == "bar":
                fig = px.bar(result_df, x=x_axis, y=y_axis)
            elif chart_type == "line":
                fig = px.line(result_df, x=x_axis, y=y_axis)
            elif chart_type == "scatter":
                fig = px.scatter(result_df, x=x_axis, y=y_axis)
            elif chart_type == "pie":
                # For pie charts, Plotly uses 'names' and 'values' instead of x/y
                fig = px.pie(result_df, names=x_axis, values=y_axis)
                
            # Apply our dark theme styling to the chart if created
            if fig is not None:
                # Premium Orange Stylings
                fig.update_traces(marker_color='#F97316')
                if chart_type == "bar":
                    fig.update_traces(
                        text=result_df[y_axis], 
                        textposition='auto',
                        marker_line_color='#FFB26B', 
                        marker_line_width=1, 
                        opacity=0.85
                    )
                elif chart_type == "line":
                    fig.update_traces(
                        mode='lines+markers+text',
                        text=result_df[y_axis], 
                        textposition='top center',
                        line=dict(width=3, color='#F97316')
                    )
                elif chart_type == "scatter":
                    fig.update_traces(
                        text=result_df[y_axis], 
                        textposition='top center'
                    )
                elif chart_type == "pie":
                    fig.update_traces(textinfo='percent+label')
                
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#A8A8A8", family='JetBrains Mono', size=11),
                    margin=dict(l=40, r=40, t=60, b=40), # Increased top margin for labels
                    xaxis=dict(showgrid=True, gridcolor='#1F1F1F', zeroline=False),
                    yaxis=dict(showgrid=True, gridcolor='#1F1F1F', zeroline=False),
                    # Remove legend title for cleaner look
                    legend_title_text=''
                )
        except Exception as e:
            # If plotting fails (e.g. wrong columns returned by SQL), fall back to none
            insight += f" (Note: Could not generate {chart_type} chart due to error: {e})"

    return fig, insight, result_df
