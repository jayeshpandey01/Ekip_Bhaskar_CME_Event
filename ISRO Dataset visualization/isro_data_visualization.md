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

