import streamlit as st
import fastf1 as f1
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import fastf1.plotting

@st.cache
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

def plot_lap_times(session, driver):
    """Generate the lap times plot for the given driver using Plotly."""
    laps = session.laps.pick_driver(driver)
    lap_times = laps['LapTime'].dt.total_seconds()

    fig = px.line(x=laps['LapNumber'], y=lap_times, labels={'x': 'Lap Number', 'y': 'Lap Time [s]'}, title=f'{driver} Lap Times')
    return fig

def plot_speed_vs_distance(driver_car_data, driver):
    """Generate the speed vs. distance scatter plot for the given driver car data using Plotly."""
    distance = driver_car_data['Distance']
    vCar = driver_car_data['Speed']

    fig = px.scatter(x=distance, y=vCar, labels={'x': 'Distance [m]', 'y': 'Speed [Km/h]'}, title=f'{driver} Speed vs. Distance')
    return fig

def display_summary_statistics(driver_car_data, driver):
    """Display summary statistics for the given driver car data."""
    vCar = driver_car_data['Speed']
    st.write(f"### {driver} Speed Summary Statistics")
    st.write(f"Mean Speed: {np.mean(vCar):.2f} Km/h")
    st.write(f"Max Speed: {np.max(vCar):.2f} Km/h")
    st.write(f"Min Speed: {np.min(vCar):.2f} Km/h")

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
    st.sidebar.title("F1 Dashboard")
    page = st.sidebar.selectbox("Select a page", ["Speed Plot", "Lap Times", "Speed vs. Distance", "Summary Statistics"])

    years = f1.get_event_schedule().Year.unique()
    tracks = f1.get_event_schedule().EventName.unique()
    sessions = ['FP1', 'FP2', 'FP3', 'Q', 'R']

    year = st.sidebar.selectbox('Year', years)
    track = st.sidebar.selectbox('Track', tracks)
    sesh = st.sidebar.selectbox('Session', sessions)

    session = load_session_data(year, track, sesh)
    if session:
        drivers = session.laps['Driver'].unique()
        driver = st.sidebar.selectbox('Driver', drivers)
        driver_car_data = session.laps.pick_driver(driver).get_car_data().add_distance()

        if page == "Speed Plot":
            st.plotly_chart(plot_speed(driver_car_data, driver))
        elif page == "Lap Times":
            try:
                lap_times_fig = plot_lap_times(session, driver)
                st.plotly_chart(lap_times_fig, use_container_width=True)
            except KeyError:
                st.warning(f"No lap times data available for driver {driver} in this session.")
        elif page == "Speed vs. Distance":
            try:
                speed_vs_distance_fig = plot_speed_vs_distance(driver_car_data, driver)
                st.plotly_chart(speed_vs_distance_fig, use_container_width=True)
            except KeyError:
                st.warning(f"No speed vs. distance data available for driver {driver} in this session.")
        elif page == "Summary Statistics":
            try:
                display_summary_statistics(driver_car_data, driver)
            except KeyError:
                st.warning(f"No summary statistics available for driver {driver} in this session.")

if __name__ == "__main__":
    main()