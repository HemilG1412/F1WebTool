import streamlit as st
import fastf1 as f1
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import fastf1.plotting

def load_session_data(year, track, sesh):
    """Load the session data for the given year, track, and session."""
    try:
        session = f1.get_session(year, track, sesh)
        session.load()
        return session
    except Exception as e:
        st.error(f"Error loading session data: {e}")
        return None

def plot_speed(driver_car_data, driver):
    """Generate the speed plot for the given driver car data using Plotly."""
    t = driver_car_data['Time']
    vCar = driver_car_data['Speed']

    fig = px.line(x=t, y=vCar, labels={'x': 'Time', 'y': 'Speed [Km/h]'}, title=f'{driver} Speed Plot')
    return fig

def plot_track(lap, weekend, year, driver):
    """Generate the track plot for the given lap data using Plotly."""
    x = lap.telemetry['X']
    y = lap.telemetry['Y']
    color = lap.telemetry['Speed']

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='black', width=16), name='Track'))
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='plasma', width=5, colorscale='plasma'), name='Speed'))

    fig.update_layout(title=f'{weekend.name} {year} - {driver} - Speed',
                      xaxis_title='X',
                      yaxis_title='Y',
                      showlegend=False)
    return fig

def main():
    # Streamlit app title
    st.title('F1 Driver Analysis')

    # Sidebar inputs for user interaction
    year = st.sidebar.selectbox('Year', [2023, 2024])  # Add more years as needed
    track = st.sidebar.selectbox('Track', ['Abu Dhabi', 'Monza', 'Silverstone'])  # Add more tracks
    sesh = st.sidebar.selectbox('Session', ['FP1', 'FP2', 'FP3', 'Q', 'R'])
    driver = st.sidebar.selectbox('Driver', ['LEC', 'VER', 'HAM', 'NOR'])  # Add more drivers

    # Load session data
    session = load_session_data(year, track, sesh)
    if session is None:
        return

    # Speed Plot
    try:
        fast_driver = session.laps.pick_driver(driver).pick_fastest()
        driver_car_data = fast_driver.get_car_data()
        speed_fig = plot_speed(driver_car_data, driver)
        st.plotly_chart(speed_fig, use_container_width=True)
    except KeyError:
        st.warning(f"No data available for driver {driver} in this session.")

    # Track Plot
    try:
        lap = session.laps.pick_driver(driver).pick_fastest()
        weekend = session.event
        track_fig = plot_track(lap, weekend, year, driver)
        st.plotly_chart(track_fig, use_container_width=True)
    except KeyError:
        st.warning(f"No telemetry data available for driver {driver} in this session.")

if __name__ == "__main__":
    main()