import pandas as pd
import numpy as np
import polars as pl
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import logging
from sklearn.metrics import precision_score, recall_score, f1_score


def load_ace_file(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    # Filter out comment lines
    data_lines = [line for line in lines if not line.startswith(('#', ':')) and line.strip()]
    
    # Convert to a DataFrame using fixed-width format
    from io import StringIO
    data_str = ''.join(data_lines)
    df = pd.read_fwf(StringIO(data_str))
    
    return df

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('cme_analysis.log', mode='w')]
)
logger = logging.getLogger(__name__)

def load_and_preprocess_csv(file_path, file_type):
    """Load and preprocess ACE CSV files."""
    try:
        df = pl.read_csv(file_path)
        # Create datetime column from YR, MO, DA, HHMM
        df = df.with_columns(
            pl.col("YR").cast(str) + "-" +
            pl.col("MO").cast(str).str.zfill(2) + "-" +
            pl.col("DA").cast(str).str.zfill(2) + " " +
            pl.col("HHMM").cast(str).str.zfill(4).str.slice(0, 2) + ":" +
            pl.col("HHMM").cast(str).str.zfill(4).str.slice(2, 2)
        ).with_columns(
            pl.col("col_0").str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M").alias("datetime")
        ).drop(["YR", "MO", "DA", "HHMM", "col_0"])
        logger.info(f"Loaded and preprocessed {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error loading {file_path}: {str(e)}")
        return None

def load_cactus_cme(cme_file):
    """Load CACTUS CME data."""
    try:
        cme_df = pl.read_csv(cme_file)
        cme_df = cme_df.with_columns(
            pl.col("CME_time").str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S")
        )
        cme_df = cme_df.filter(pl.col("is_halo") == True)
        logger.info(f"Loaded {len(cme_df)} halo CME events")
        return cme_df
    except Exception as e:
        logger.error(f"Error loading CACTUS CME data: {str(e)}")
        return None

def extract_cme_windows(data_df, cme_df, window_hours=12):
    """Extract time windows around CME events."""
    windows = []
    for cme_time in cme_df["CME_time"]:
        start_time = cme_time - timedelta(hours=window_hours)
        end_time = cme_time + timedelta(hours=window_hours)
        window_df = data_df.filter(
            (pl.col("datetime") >= start_time) & (pl.col("datetime") <= end_time)
        )
        window_df = window_df.with_columns(pl.lit(cme_time).alias("cme_time"))
        windows.append(window_df)
    if windows:
        return pl.concat(windows)
    return None

def derive_features(df, file_type):
    """Derive time-series features for CME detection."""
    try:
        # Select relevant columns based on file type
        if file_type == "epam":
            flux_cols = ["Proton_47-65", "Proton_112-187", "Proton_310-580", "Proton_761-1220", "Proton_1060-1910"]
        elif file_type == "sis":
            flux_cols = ["Proton_>10MeV", "Proton_>30MeV"]
        elif file_type == "swepam":
            flux_cols = ["Proton_Density", "Bulk_Speed", "Ion_Temperature"]
        else:
            return df
        
        # Compute moving averages (1-hour window, assuming 5-min data)
        window_size = 12  # 12 * 5min = 1 hour
        for col in flux_cols:
            df = df.with_columns(
                pl.col(col).rolling_mean(window_size=window_size, min_periods=1).alias(f"{col}_ma")
            )
            # Compute gradient
            df = df.with_columns(
                (pl.col(col) - pl.col(col).shift(1)).alias(f"{col}_gradient")
            )
        
        # Compute combined metric (e.g., flux * speed for swepam)
        if file_type == "swepam":
            df = df.with_columns(
                (pl.col("Proton_Density") * pl.col("Bulk_Speed")).alias("density_speed_product")
            )
        return df
    except Exception as e:
        logger.error(f"Error deriving features for {file_type}: {str(e)}")
        return df

def detect_cme_events(df, file_type, thresholds):
    """Detect CME events based on thresholds."""
    try:
        detections = pl.DataFrame({"datetime": df["datetime"], "is_cme": False})
        for col, thresh in thresholds.items():
            if col in df.columns:
                detections = detections.with_columns(
                    pl.col("is_cme") | (pl.col(col) > thresh).fill_null(False)
                )
        return detections
    except Exception as e:
        logger.error(f"Error detecting CMEs for {file_type}: {str(e)}")
        return None

def validate_detections(detections, cme_df, tolerance_minutes=60):
    """Validate detected CMEs against CACTUS timestamps."""
    try:
        true_cmes = cme_df["CME_time"].to_list()
        detected_cmes = detections.filter(pl.col("is_cme") == True)["datetime"].to_list()
        
        y_true = []
        y_pred = []
        for dt in detections["datetime"]:
            # Check if datetime is near a true CME (within tolerance)
            is_true_cme = any(abs((dt - cme).total_seconds()) / 60 <= tolerance_minutes for cme in true_cmes)
            y_true.append(is_true_cme)
            is_pred_cme = dt in detected_cmes
            y_pred.append(is_pred_cme)
        
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)
        logger.info(f"Precision: {precision:.2f}, Recall: {recall:.2f}, F1-Score: {f1:.2f}")
        return precision, recall, f1
    except Exception as e:
        logger.error(f"Error validating detections: {str(e)}")
        return None, None, None

def plot_time_series(df, cme_df, file_type, output_file):
    """Plot time-series with CME markers."""
    try:
        plt.figure(figsize=(12, 6))
        if file_type == "epam":
            cols = ["Proton_47-65", "Proton_112-187", "Proton_761-1220"]
        elif file_type == "sis":
            cols = ["Proton_>10MeV", "Proton_>30MeV"]
        elif file_type == "swepam":
            cols = ["Proton_Density", "Bulk_Speed", "Ion_Temperature"]
        else:
            return
        
        for col in cols:
            plt.plot(df["datetime"].to_pandas(), df[col].to_pandas(), label=col)
        
        for cme_time in cme_df["CME_time"]:
            plt.axvline(x=cme_time, color='r', linestyle='--', alpha=0.5, label="CME" if cme_time == cme_df["CME_time"][0] else "")
        
        plt.xlabel("Time")
        plt.ylabel("Value")
        plt.title(f"{file_type.upper()} Parameters with CME Events")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_file)
        plt.close()
        logger.info(f"Saved plot to {output_file}")
    except Exception as e:
        logger.error(f"Error plotting {file_type}: {str(e)}")

