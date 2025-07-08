# ☀️ Aditya-L1 CME Detection Project

This repository focuses on detecting **Coronal Mass Ejections (CMEs)** from solar data, likely in alignment with the Aditya-L1 mission by ISRO. It includes Jupyter notebooks for preprocessing, detection logic, threshold tuning, analysis, and detailed logs and reports.

---

## 📁 Project Structure

```

aditya-l1-isro-main/
├── cme\_detection\_csv\_01.ipynb       # Main notebook for CME detection from CSV
├── Detect\_cme\_csv.ipynb             # Alternate or modular detection notebook
├── sample.ipynb                     # Sample/demonstration notebook
├── cme\_detection\_overview\.png       # Visualization of detection output
├── threshold\_analysis.png           # Threshold tuning output
├── cme\_detection\_report.txt         # Detailed report on detection results
├── threshold\_optimization\_report.txt# Report on threshold optimization steps
├── cme\_detection.log                # Log file for detection process
├── Notebook/
│   ├── clearning\_csv\_file.ipynb     # Data cleaning/preprocessing notebook
│   └── ace\_processing.log           # Log of ACE dataset processing

````
### 📁 Key Files and Directories

* `cme_detection_csv_01.ipynb`, `Detect_cme_csv.ipynb`: Notebooks related to CME detection using CSV data.
* `cme_detection_overview.png`, `threshold_analysis.png`: Visual outputs for detection and threshold tuning.
* `cme_detection_report.txt`, `threshold_optimization_report.txt`: Text reports summarizing detection performance or settings.
* `cme_detection.log`, `ace_processing.log`: Logs indicating steps or results of detection processes.
* `sample.ipynb`: Possibly a demo or small test notebook.
---

## 🧪 Key Features

- 📊 **CSV-Based CME Detection**: Implements logic to detect solar events using CSV inputs.
- ⚙️ **Threshold Optimization**: Tools and reports for determining optimal thresholds.
- 📈 **Visualization**: Plots and images to interpret detection performance.
- 📂 **Logs & Reports**: Includes detailed tracking and analysis of execution and outputs.

---

### 🔍 CME Detection Table: Column Descriptions and Usage

| **Column Name**                  | **Description**                                   | **Usage in CME Detection**                                                     |
| -------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------ |
| `Proton_Density`                 | Number of protons per unit volume (particles/cm³) | Sharp increase may indicate a shock front from CME.                            |
| `Bulk_Speed`                     | Average speed of solar wind (km/s)                | Sudden rise in speed is a hallmark of CME arrival.                             |
| `Ion_Temperature`                | Temperature of ions in the solar wind (K)         | Enhanced ion temperatures suggest the presence of shocked or disturbed plasma. |
| `year`, `YR`, `MO`, `DA`, `HHMM` | Year, month, day, and time of the measurement     | Required for temporal analysis and event timestamping.                         |
| `Julian_Day`                     | Day of the year (Julian format)                   | Useful for plotting time series and comparing multiple datasets.               |
| `Seconds_of_Day`                 | Seconds since 00:00:00 of the same day            | High-resolution timestamping of CME event start/peak times.                    |

---

### 🚀 High-Energy Particle Flux Columns

| **Column Name**            | **Description**                                   | **Usage in CME Detection**                                                                             |
| -------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `S_10MeV`, `Proton_>10MeV` | Proton flux at >10 MeV energies (e.g., from GOES) | Sudden spike indicates Solar Energetic Particle (SEP) events, often associated with CME-driven shocks. |
| `S_30MeV`, `Proton_>30MeV` | Proton flux at >30 MeV                            | Similar use as above; important for analyzing SEP spectrum.                                            |

---

### 🧭 Magnetic Field Components (GSE Coordinates)

| **Column Name**  | **Description**                       | **Usage in CME Detection**                                                                                       |
| ---------------- | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `Bx`, `By`, `Bz` | Magnetic field vector components (nT) | Sudden and significant directional change, especially in `Bz`, helps identify magnetic clouds (a CME signature). |
| `Bt`             | Total magnetic field strength (nT)    | Increase in total field strength is typical in CME sheath and ejecta regions.                                    |

---

### 🌍 Spacecraft/Instrument Location

| **Column Name**         | **Description**                          | **Usage in CME Detection**                                                                               |
| ----------------------- | ---------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `Latitude`, `Longitude` | Spacecraft or observation point location | Important for mapping CME trajectory and impact location (e.g., at L1 point, geostationary orbit, etc.). |

---

### 🌐 Energetic Electron & Proton Fluxes

| **Column Name**                                                                           | **Description**                                                | **Usage in CME Detection**                                                          |
| ----------------------------------------------------------------------------------------- | -------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `Electron_S`                                                                              | Total electron flux from multiple channels                     | Increase may precede or follow a CME shock wave.                                    |
| `Electron_38-53`, `Electron_175-315`                                                      | Differential flux of electrons in specific energy ranges (keV) | Energy-specific responses useful in determining shock acceleration effects.         |
| `Proton_S`                                                                                | Total proton flux across all energy bands                      | Overall enhancement supports CME-related SEP analysis.                              |
| `Proton_47-65`, `Proton_112-187`, `Proton_310-580`, `Proton_761-1220`, `Proton_1060-1910` | Proton flux in various energy bands (keV)                      | Multi-energy flux profiles help study acceleration mechanisms and shock signatures. |

---

### 📈 Anisotropy Measurement

| **Column Name**    | **Description**                                         | **Usage in CME Detection**                                                              |
| ------------------ | ------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `Anisotropy_Ratio` | Ratio indicating directional variation of particle flux | High anisotropy near onset of CME-related SEP events can indicate shock nose direction. |

---

### 🧩 Combined Time Fields

| **Column Name**                            | **Description**                                         | **Usage in CME Detection**                                                                             |
| ------------------------------------------ | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `Julian_Day` (2nd), `Seconds_of_Day` (2nd) | Possibly related to the energetic particle dataset time | Needed to align magnetic, plasma, and energetic particle datasets for multi-parameter CME event study. |

---

## 🚀 Getting Started

### Requirements

- Python 3.8+
- Jupyter Notebook
- Pandas, NumPy, Matplotlib
- Optional: Logging libraries, Seaborn

### How to Run

1. Clone this repository or download the ZIP.
2. Install dependencies:

```bash
pip install pandas numpy matplotlib
````

3. Open notebooks:

```bash
jupyter notebook
```

4. Run `cme_detection_csv_01.ipynb` or `Detect_cme_csv.ipynb` to detect CMEs from CSV data.

---

## 📌 Notebooks Summary

| Notebook                     | Description                         |
| ---------------------------- | ----------------------------------- |
| `cme_detection_csv_01.ipynb` | Primary notebook for detecting CMEs |
| `Detect_cme_csv.ipynb`       | Alternate detection implementation  |
| `clearning_csv_file.ipynb`   | Data cleaning for input CSVs        |
| `sample.ipynb`               | Sample/test demonstration           |

---

## 📊 Visuals
* `cme_detection_overview.png`: Detection overview.
* `threshold_analysis.png`: Threshold tuning and evaluation.
---

## 🧾 Reports
* `cme_detection_report.txt`: Final detection summary.
* `threshold_optimization_report.txt`: Describes process of optimizing detection sensitivity.
---

## 🛰️ Mission Relevance
This project contributes to the **Aditya-L1 solar observatory mission** by providing a pipeline for detecting solar events (CMEs) using space weather data, potentially improving real-time forecasting systems.
---

## 📬 Contact

For questions, improvements, or collaborations, please raise an issue or get in touch with the maintainers.

