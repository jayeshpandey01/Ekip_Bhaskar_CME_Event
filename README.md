# Halo CME Events Identification Using SWIS-ASPEX Data from Aditya-L1

![Project Banner](Project_Banner.png)  
*Harnessing Aditya-L1's Solar Wind Ion Spectrometer (SWIS) data to detect and predict Halo Coronal Mass Ejections (CMEs) for space weather monitoring.*

---

## 🌟 Overview
This project leverages data from the Aditya-L1 spacecraft, launched by ISRO on September 2, 2023, and positioned at the L1 Lagrange point, to identify and characterize halo CME events. Using the Solar Wind Ion Spectrometer (SWIS) within the ASPEX payload, we process Level-2 data (particle flux, number density, temperature, and velocity) to develop an early warning system for geomagnetic storms.

- **Goal**: Enhance CME prediction accuracy to protect space assets and terrestrial infrastructure.
- **Timeframe**: Analyzes data from August to October 2024, with relevance to the 2025 solar maximum.
- **Team**: Jayesh J. Pandey, Kanishk T. Vadge, [Third Author]

---

## 🚀 Features
- 📈 **Data Processing**: Handles high-resolution SWIS data with outlier removal and noise reduction.
- 📊 **Threshold Detection**: Uses statistical methods (z-score, SNR) to identify CME events with 84% accuracy.
- 💨 **Speed Estimation**: Calculates CME speeds (e.g., 780 km/s average) with kinematic models.
- 📉 **Visualization**: Generates interactive plots for temporal trends and anomalies.
- 🛰️ **Early Warning**: Lays groundwork for real-time space weather alerts.

---

## 📸 Screenshots

### Mobile App Interface
![Mobile App](https://via.placeholder.com/300x600.png?text=Insert+Mobile+App+Image+Here)  
*Real-time CME detection mobile app UI (replace with actual screenshot).*

### Sample Visualization Result
![Visualization](https://via.placeholder.com/600x400.png?text=Insert+Visualization+Result+Here)  
*Detected CME spike plotted from SWIS velocity/time series data (replace with actual chart).*

---

## 🛠️ Technologies Used

| Component      | Details                                  |
|----------------|-------------------------------------------|
| 💻 Languages   | Python 3.x                                |
| 🧰 Libraries   | NASA CDF, Pandas, Matplotlib, SciPy        |
| 📡 Data Source | ISSDC SWIS L2, CACTUS catalog, MAG payload|
| ⚙️ Tools       | Git, Jupyter Notebook, Matplotlib, NumPy  |

---

## 📝 Research Papers

Explore the technical and scientific documentation for this project:

1. 📘 [Halo CME Events Identification - Full Report](https://github.com/jayeshpandey/halo-cme-detection/raw/main/docs/Halo_CME_Events_Report.pdf)
2. 📗 [Methodology and Results](https://github.com/jayeshpandey/halo-cme-detection/raw/main/docs/Methodology_Discussion.pdf)
3. 📙 [Conclusion and References](https://github.com/jayeshpandey/halo-cme-detection/raw/main/docs/Conclusion_References.pdf)

---

## 🔗 Useful Links
- 🌞 [Aditya-L1 Mission Overview – ISRO](https://www.isro.gov.in/Aditya-L1.html)
- 🛰️ [CACTUS CME Database](https://www.sidc.be/cactus/)
- 📄 [NASA CDF Documentation](https://cdf.gsfc.nasa.gov/html/sw_package.html)

---

## 📈 Getting Started

Follow these steps to run the project locally:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/jayeshpandey/halo-cme-detection.git
   cd halo-cme-detection
   ```


2. **Install Required Packages**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Main Analysis Script**:

   ```bash
   python src/main.py
   ```

4. **Explore the Jupyter Notebooks**:

   ```bash
   jupyter notebook notebooks/data_analysis.ipynb
   ```

---

## 🧠 Folder Structure

```bash
halo-cme-detection/
├── docs/
│   ├── Halo_CME_Events_Report.pdf
│   ├── Methodology_Discussion.pdf
│   └── Conclusion_References.pdf
├── images/
│   ├── app_screenshot.png
│   └── cme_spike_plot.png
├── notebooks/
│   ├── data_analysis.ipynb
│   └── visualization.ipynb
├── src/
│   ├── main.py
│   └── utils.py
├── requirements.txt
├── README.md
├── README_PROJECT_FILES.md
└── README_DATA_DETAILS.md
```

---

## 🤝 Contributing

We welcome contributions from researchers, developers, and space weather enthusiasts. Please:

* Fork this repository
* Create a feature branch
* Submit a pull request

If you're proposing significant changes, open an issue first to discuss.

---

## 📅 Project Status

* **Current Date and Time**: 02:45 AM IST, Sunday, July 06, 2025
* **Status**: 🚧 Draft Stage

  * [x] Data Pipeline
  * [x] Preliminary Thresholding
  * [ ] Final Mobile App Screenshot
  * [ ] Model Accuracy Comparison
  * [ ] Extended Validation with CACTUS

---

## 📧 Contact

* ✉️ **Email**: [jayesh.pandey@university.edu](mailto:jayesh.pandey@university.edu)
* 💻 **GitHub**: [@jayeshpandey](https://github.com/jayeshpandey)

---

*Made with ❤️ by the Aditya-L1 Solar Event Detection Team*



---

### 📌 Final Notes for You

To complete the GitHub setup:

1. Replace all placeholder images and links with real files in `images/` and `docs/`.
2. Push everything to GitHub using:

```bash
git add .
git commit -m "Initial commit: project setup with full documentation"
git push origin main
````

