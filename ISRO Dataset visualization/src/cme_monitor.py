import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import websocket
import json
import numpy as np
from datetime import time as dt_time
import time

class CMEApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aditya-L1 & SOHO CME Monitor")
        self.data = {
            'flux_proton': [], 'flux_sector': [], 'flux_alpha': [], 'threshold': [],
            'ahe': [], 'uncer': [], 'principal_angle': [], 'angular_width': [], 'velocity': [],
            'height_time_data': [], 'cme_detections': [], 'catalog_cmes': [], 'software_cmes': [],
            'is_cme_particle': False, 'is_cme_lasco': False, 'lasco_time': ''
        }

        # Create figures
        self.fig_heatmap, self.ax_heatmap = plt.subplots()
        self.fig_front, self.ax_front = plt.subplots()
        self.fig_map, self.ax_map = plt.subplots()

        # Initialize canvases
        self.canvas_heatmap = FigureCanvasTkAgg(self.fig_heatmap, master=root)
        self.canvas_front = FigureCanvasTkAgg(self.fig_front, master=root)
        self.canvas_map = FigureCanvasTkAgg(self.fig_map, master=root)

        # Pack canvases
        self.canvas_heatmap.get_tk_widget().pack()
        self.canvas_front.get_tk_widget().pack()
        self.canvas_map.get_tk_widget().pack()

        # Start mock data simulation
        self.simulate_data()

    def simulate_data(self):
        # Mock data
        mock_data = {
            "flux_proton": np.random.random(),
            "flux_sector": np.random.random(),
            "flux_alpha": np.random.random(),
            "threshold": np.random.random(),
            "ahe": np.random.random(),
            "uncer": np.random.random(),
            "principal_angle": np.random.uniform(0, 360),
            "angular_width": np.random.uniform(10, 100),
            "velocity": np.random.uniform(100, 1000),
            "height_time_data": np.random.random((100, 100)).tolist(),
            "cme_detections": [[time.time(), np.random.uniform(0, 360), np.random.uniform(2, 30)] for _ in range(3)],
            "catalog_cmes": [[time.time() + i*3600, np.random.uniform(0, 360)] for i in range(5)],
            "software_cmes": [[time.time() + i*3600, np.random.uniform(0, 360)] for i in range(5)],
            "is_cme_particle": np.random.choice([True, False]),
            "is_cme_lasco": np.random.choice([True, False]),
            "lasco_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "cme_detected": bool(np.random.rand() > 0.5)  # Convert to Python bool

        }
        json.dumps(mock_data)  # ✅ Works
        # Simulate WebSocket message
        self.on_message(json.dumps(mock_data))
        # Schedule next data simulation
        self.root.after(1000, self.simulate_data)  # Update every 1 second

    def on_message(self, message):
        try:
            data = json.loads(message)
            self.update_data(data)
            self.update_plots()
        except Exception as e:
            print(f"Error parsing message: {e}")

    def on_error(self, ws, error):
        print(f"WebSocket Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket Closed")

    def update_data(self, new_data):
        self.data['flux_proton'].append(new_data['flux_proton'])
        self.data['flux_sector'].append(new_data['flux_sector'])
        self.data['flux_alpha'].append(new_data['flux_alpha'])
        self.data['threshold'].append(new_data['threshold'])
        self.data['ahe'].append(new_data['ahe'])
        self.data['uncer'].append(new_data['uncer'])
        self.data['principal_angle'].append(new_data['principal_angle'])
        self.data['angular_width'].append(new_data['angular_width'])
        self.data['velocity'].append(new_data['velocity'])
        self.data['height_time_data'] = new_data['height_time_data'] if new_data['height_time_data'] else self.data['height_time_data']
        self.data['cme_detections'] = new_data['cme_detections'] if new_data['cme_detections'] else self.data['cme_detections']
        self.data['catalog_cmes'] = new_data['catalog_cmes'] if new_data['catalog_cmes'] else self.data['catalog_cmes']
        self.data['software_cmes'] = new_data['software_cmes'] if new_data['software_cmes'] else self.data['software_cmes']
        self.data['is_cme_particle'] = new_data['is_cme_particle']
        self.data['is_cme_lasco'] = new_data['is_cme_lasco']
        self.data['lasco_time'] = new_data['lasco_time']

        # Limit to last 100 points
        for key in ['flux_proton', 'flux_sector', 'flux_alpha', 'threshold', 'ahe', 'uncer',
                   'principal_angle', 'angular_width', 'velocity']:
            self.data[key] = self.data[key][-100:]

    def update_plots(self):
        # [Height, Time] Plot
        self.ax_heatmap.clear()
        heatmap = self.ax_heatmap.imshow(self.data['height_time_data'], cmap='viridis', aspect='auto')
        self.ax_heatmap.set_xlabel('Time (minutes)')
        self.ax_heatmap.set_ylabel('Height (solar radii)')
        self.ax_heatmap.set_title('[Height, Time] Plot')
        for det in self.data['cme_detections']:
            t, angle, h = det
            x = (t - self.data['cme_detections'][0][0]) / (60 * 720) * heatmap.get_array().shape[1]
            y = (1 - (h - 2) / 28) * heatmap.get_array().shape[0]
            self.ax_heatmap.plot([x, x + 10], [y, y - 10], color='red', linewidth=2)
        self.canvas_heatmap.draw()

        # CME Front Tracking
        self.ax_front.clear()
        self.ax_front.plot(self.data['principal_angle'], label='Current Front', color='red')
        self.ax_front.plot([a - 5 for a in self.data['principal_angle']], label='Earlier', color='blue')
        self.ax_front.plot([a + 5 for a in self.data['principal_angle']], label='Later', color='yellow')
        self.ax_front.set_xlabel('Time Index')
        self.ax_front.set_ylabel('Principal Angle (°)')
        self.ax_front.set_title('CME Front Tracking')
        self.ax_front.legend()
        self.canvas_front.draw()

        # Combined Map
        self.ax_map.clear()
        catalog_x = [c[1] for c in self.data['catalog_cmes']]
        catalog_y = [(c[0] - self.data['catalog_cmes'][0][0]) / (60 * 720) for c in self.data['catalog_cmes']]
        software_x = [s[1] for s in self.data['software_cmes']]
        software_y = [(s[0] - self.data['software_cmes'][0][0]) / (60 * 720) for s in self.data['software_cmes']]
        self.ax_map.scatter(catalog_x, catalog_y, color='green', label='Catalog CMEs')
        self.ax_map.scatter(software_x, software_y, color='white', label='Software CMEs')
        self.ax_map.set_xlabel('Poloidal Angle (°)')
        self.ax_map.set_ylabel('Time (minutes)')
        self.ax_map.set_title('Combined CME Map')
        self.ax_map.legend()
        self.canvas_map.draw()

        # Alert for CME detection
        if self.data['is_cme_particle'] or self.data['is_cme_lasco']:
            print(f"Halo CME Detected at {self.data['lasco_time']}: Particle={self.data['is_cme_particle']}, LASCO={self.data['is_cme_lasco']}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CMEApp(root)
    root.mainloop()