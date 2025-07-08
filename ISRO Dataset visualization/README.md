# ISRO CME Event Analysis and Modeling

This project focuses on analyzing and modeling Coronal Mass Ejections (CMEs) using observational data, processing techniques, and deep learning approaches. It includes notebooks for data exploration, preprocessing, visualization, model training, and evaluation.

---

## 📁 Project Structure

```

ISRO/
├── best\_cme\_model.pth             # Trained PyTorch model for CME predictions
├── suit\_intensity.csv             # Dataset containing solar/space weather intensity values
├── training\_loss.png              # Training loss curve visualization
├── Notebook/
│   ├── cdf\_test/
│   │   ├── 3d\_visulize.ipynb      # 3D data visualization of CDF data
│   │   ├── cdf\_test\_01.ipynb      # Initial CDF data analysis
│   │   ├── cdf\_test\_02.ipynb      # Further analysis with alternate parameters
│   │   ├── cdf\_test\_03.ipynb
│   │   ├── cdf\_test\_04.ipynb
│   │   ├── processing.ipynb       # Data preprocessing script
│   ├── fits\_test/
│   │   ├── sample\_test\_02.ipynb   # Notebook for FITS file processing tests

````

---

## 🧪 Features

- 🌌 **Solar Event Modeling**: Uses real-world data to train deep learning models for space weather event prediction.
- 📊 **Data Processing**: Includes CDF and FITS file preprocessing scripts.
- 🧠 **Model Training**: Trained model provided (`best_cme_model.pth`) and visualized using `training_loss.png`.
- 📈 **Visualization Tools**: 3D visualizations and charts via Jupyter Notebooks.

---

## L1_AUX

### 🔍 How the Variables Help Detect CMEs

| Variable | How It Helps | Why It's Useful |
|---------|--------------|-----------------|
| `trig_counts` | Measures triggered events across detectors and energy bins | Spikes in counts can indicate CME-driven particle bursts |
| `coin_trig_counts` / `coinc_trig_count_total` | Detects simultaneous hits across detectors | Helps confirm real events vs. noise |
| `angle_tha1`, `angle_tha2`, `angle_[x/y/z]gse` | Provides particle arrival directions | Used to trace CME origin and propagation path |
| `peak_det_counts` / `rej_counts` | Shows peak and rejected events | Helps identify saturation or filtering during intense events |
| `obs_time`, `epoch_for_cdf` | Time-stamps each measurement | Essential for correlating with solar observations or other spacecraft |
| `spacecraft_[x/y/z]pos` / `vel` | Gives spacecraft location and motion | Needed for coordinate transformation and triangulation |

---

## L1_TH1

### 🔍 Key zVariables for CME Analysis

| Variable | Why It Matters | How It's Used |
|---------|----------------|----------------|
| **`THA-1_spec`** | This is the **spectral data** from the THA-1 detector, likely representing energy-resolved particle counts across time, channels, and energy bins. | You analyze this to detect **sudden enhancements in particle flux**—a hallmark of CME-driven solar energetic particle (SEP) events. You can integrate over energy bins or track specific channels for spikes. |
| **`obs_time`** | Provides the **observation timestamp** for each data point. | Essential for **temporal correlation** with solar events (e.g., flares or CME onset from coronagraphs like LASCO or Aditya-L1 VELC). |
| **`epoch_for_cdf`** | Another form of time reference, often used for aligning data across instruments. | Useful for **synchronizing** THA-1 data with other spacecraft or ground-based observations. |
| **`fpga_ticks`** | Internal clock ticks from the FPGA, possibly used for **high-resolution timing**. | Can help in **fine-grained timing analysis** of particle arrival, especially if `obs_time` is coarse. |
| **`frame_num`** | Likely a sequential counter for data frames. | Helps in **data integrity checks** and aligning frames with telemetry or event logs. |

---
## L1_TH2

### 🔍 Key zVariables and Their Role

| Variable | Why It Matters | How It's Used |
|---------|----------------|----------------|
| **`THA-2_spec`** | This is the **spectral data** from the THA-2 detector—likely representing particle counts across time, channels, and energy bins. | You analyze this to detect **sudden enhancements in particle flux**, especially in higher energy bins, which are strong indicators of CME-driven solar energetic particle (SEP) events. |
| **`obs_time`** | Provides the **actual observation timestamps** for each spectral frame. | Crucial for **temporal correlation** with CME onset times from solar imagers (e.g., LASCO, Aditya-L1). |
| **`epoch_for_cdf`** | A standardized time reference used across instruments. | Helps **synchronize** THA-2 data with other spacecraft or ground-based datasets. |
| **`fpga_ticks`** | Internal FPGA clock ticks—likely high-resolution timing. | Useful for **fine-grained timing analysis** of particle arrival, especially when `obs_time` is coarse or interpolated. |
| **`frame_num`** | Sequential frame counter. | Helps ensure **data continuity** and identify any dropped or corrupted frames during CME passage. |

---

## L2_BLK

### 🔍 CME-Relevant zVariables Explained

| Variable | Why It Matters | How It's Used |
|---------|----------------|----------------|
| **`proton_bulk_speed`** | Measures the bulk flow speed of protons. | A sudden increase (shock) followed by a plateau or decrease (ejecta) is a classic CME signature. |
| **`proton_density`** | Proton number density in the solar wind. | Spikes in density often mark the **shock front**; a drop may indicate the **magnetic cloud** or ejecta. |
| **`proton_thermal`** | Proton thermal speed or temperature. | Elevated temperature in the sheath region, followed by a drop in the ejecta, is typical of CME passage. |
| **`alpha_bulk_speed`**, **`alpha_density`**, **`alpha_thermal`** | Same as above, but for alpha particles (He²⁺). | Used to compute **alpha-to-proton ratios**, which often increase inside CMEs—an important compositional signature. |
| **`proton_[x/y/z]velocity`** | 3D velocity components of protons. | Helps identify **flow deflections** and **magnetic field orientation changes** during CME passage. |
| **`epoch_for_cdf_mod`** | Time reference for all measurements. | Essential for **temporal correlation** with solar observations and other spacecraft. |
| **`spacecraft_[x/y/z]pos`** | Spacecraft position in 3D space. | Used to **map CME trajectory** and compare with other observation points. |
| **Uncertainty variables** (e.g., `bulk_p_uncer`, `thermal_p_uncer`) | Measurement uncertainties. | Important for **error propagation** and confidence in event detection. |

---
## L2_TH1

### 🔍 CME-Relevant zVariables Explained

| Variable | Why It Matters | How It's Used |
|---------|----------------|----------------|
| **`energy_center_mod`** | Represents the **central energy values** of each spectral bin. | Defines the energy axis for interpreting flux data—essential for identifying energy-dependent enhancements during CME-driven SEP events. |
| **`integrated_flux_mod`**, **`integrated_flux_s9/s10/s11_mod`** | These are **energy-resolved flux measurements**, possibly from different sectors or detectors. | You analyze these for **sudden increases in particle flux**, especially in higher energy bins—classic CME signatures. Sector-specific fluxes help identify **anisotropies** in particle arrival. |
| **`epoch_for_cdf_mod`** | Time reference for each flux measurement. | Used to **correlate flux spikes** with CME onset times from solar imagers or other instruments. |
| **`spacecraft_[x/y/z]pos`** | Spacecraft’s position in 3D space. | Crucial for **transforming flux vectors** into heliocentric coordinates and for **triangulating CME propagation**. |
| **`sun_angle_tha1`** | Likely the **angle between the detector and the Sun** for each THA-1 channel. | Helps determine **directionality** of incoming particles—important for confirming solar origin of the event. |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Jupyter Notebook / JupyterLab
- PyTorch
- NumPy, Pandas, Matplotlib
- SpacePy or libraries for handling CDF/FITS files (e.g., `cdflib`, `astropy`)

### Setup

```bash
git clone <this-repo>
cd ISRO
pip install -r requirements.txt  # If requirements are defined
jupyter notebook
````

---

## 📁 Key Files

| File/Folder           | Description                                      |
| --------------------- | ------------------------------------------------ |
| `best_cme_model.pth`  | Trained deep learning model                      |
| `suit_intensity.csv`  | Input data with solar intensity metrics          |
| `training_loss.png`   | Visualization of model training loss             |
| `Notebook/cdf_test/`  | Data preprocessing and visual analysis notebooks |
| `Notebook/fits_test/` | Sample tests and FITS file handling notebooks    |

---

## 📌 Notes

* Notebooks are structured for modular testing and can be run individually.
* The project is part of an initiative for **CME Detection and Space Weather Forecasting**, possibly supporting ISRO’s Aditya-L1 mission or similar solar studies.

---

## 📚 References

* NASA CDAWeb, CDF, and FITS formats
* PyTorch documentation
* Astropy for astronomy data handling



## 📬 Contact

For collaborations or questions, please contact the repository maintainer or open an issue.

