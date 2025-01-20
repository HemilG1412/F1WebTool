from flask import Flask, request, jsonify
from flask_cors import CORS
import fastf1 as f1
import numpy as np
import matplotlib.pyplot as plt
import fastf1.plotting
from matplotlib.collections import LineCollection
import io
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return "Welcome to the F1 Dashboard API!"

@app.route('/get_plots', methods=['POST'])
def get_plots():
    data = request.json
    year = data.get('year', 2024)
    track = data.get('track', 'Abu Dhabi')
    sesh = data.get('session', 'R')
    driver = data.get('driver', 'LEC')

    session = f1.get_session(year, track, sesh)
    session.load()

    # Speed Plot
    fast_driver = session.laps.pick_driver(driver).pick_fastest()
    driver_car_data = fast_driver.get_car_data()
    t = driver_car_data['Time']
    vCar = driver_car_data['Speed']

    fig, ax = plt.subplots()
    ax.plot(t, vCar, label='Fast')
    ax.set_xlabel('Time')
    ax.set_ylabel('Speed [Km/h]')
    ax.set_title(f'{driver} Speed Plot')
    ax.legend()

    # Save plot to a string buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    speed_plot = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    # Track Plot
    lap = session.laps.pick_driver(driver).pick_fastest()
    x = lap.telemetry['X']
    y = lap.telemetry['Y']
    color = lap.telemetry['Speed']

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    fig, ax = plt.subplots(figsize=(12, 6.75))
    colormap = plt.cm.plasma
    ax.plot(lap.telemetry['X'], lap.telemetry['Y'],
            color='black', linestyle='-', linewidth=16, zorder=0)

    norm = plt.Normalize(color.min(), color.max())
    lc = LineCollection(segments, cmap=colormap, norm=norm,
                        linestyle='-', linewidth=5)
    lc.set_array(color)
    ax.add_collection(lc)
    ax.axis('off')

    # Save plot to a string buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    track_plot = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return jsonify({'speed_plot': speed_plot, 'track_plot': track_plot})

if __name__ == '__main__':
    app.run(debug=True)