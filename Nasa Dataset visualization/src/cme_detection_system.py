"""
Advanced CME Detection System for Aditya-L1 SWIS Data Analysis
==============================================================

This system analyzes solar wind data to detect transient events such as halo Coronal Mass Ejections (CMEs).
It processes time-series data from Solar Wind Ion Spectrometer (SWIS) instrument parameters including:
- Particle flux (proton and electron energy channels)
- Number density
- Temperature
- Velocity

Handles differing HHMM formats and large datasets with robust data cleaning.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from scipy import signal
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import logging
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cme_detection.log', mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CMEDetectionSystem:
    """
    Advanced CME Detection System for analyzing solar wind data
    """
    
    def __init__(self, data_path):
        """
        Initialize the CME detection system
        
        Args:
            data_path (str): Path to the data directory containing CSV files
        """
        self.data_path = data_path
        self.data = {}
        self.processed_data = {}
        self.detection_results = {}
        self.thresholds = {}
        
        # Adjusted CME detection parameters for higher sensitivity
        self.cme_signatures = {
            'speed_enhancement': 50,       # km/s increase above background
            'density_enhancement': 1.5,    # Factor increase above background
            'temperature_decrease': 0.7,   # Factor decrease
            'proton_flux_increase': 5.0,   # Factor increase in high-energy protons
            'magnetic_field_rotation': 30, # Degrees
            'duration_min': 2,             # Hours minimum duration
            'duration_max': 24            # Hours maximum duration
        }
        # Instrument-specific time resolutions (in minutes)
        self.time_resolutions = {
            'swepam': 1,  # 1-minute data
            'mag': 1,     # 1-minute data
            'epam': 5,    # 5-minute data
            'sis': 5      # 5-minute data
        }
    
    def load_data(self):
        """Load and preprocess all available data files, handling HHMM differences and data types"""
        logger.info("Loading solar wind data files...")
        
        file_mapping = {
            'swepam': 'ace_swepam_data.csv',
            'mag': 'ace_mag_data.csv', 
            'epam': 'ace_epam_data.csv',
            'sis': 'ace_sis_data.csv'
        }
        
        for instrument, filename in file_mapping.items():
            filepath = f"{self.data_path}/{filename}"
            try:
                df = pd.read_csv(filepath)
                
                if df.empty:
                    raise ValueError(f"Empty dataframe for {instrument}")

                # Adjust column names if necessary
                if not df.columns[0].startswith('YR'):
                    df.columns = df.iloc[0]
                    df = df[1:]

                # Normalize HHMM or derive from HH and MM
                if 'HHMM' in df.columns:
                    df['HHMM'] = df['HHMM'].astype(str).str.zfill(4)
                    df['HH'] = df['HHMM'].str[:2]
                    df['MM'] = df['HHMM'].str[2:]
                elif 'HH' in df.columns and 'MM' in df.columns:
                    logger.info(f"{instrument}: Using separate HH and MM columns")
                    df['HH'] = df['HH'].astype(str).str.zfill(2)
                    df['MM'] = df['MM'].astype(str).str.zfill(2)
                else:
                    logger.error(f"{instrument}: No HHMM or HH/MM columns found")
                    raise ValueError(f"{instrument}: Cannot construct datetime without HHMM or HH/MM columns")

                # Log sample of problematic HHMM entries
                invalid_hhmm = df['HHMM'].str.contains(r'[^0-9]', na=True) | (df['HHMM'].str.len() != 4)
                if invalid_hhmm.any():
                    sample_invalid = df[invalid_hhmm]['HHMM'].head(5).tolist()
                    logger.warning(f"{instrument}: Sample invalid HHMM entries: {sample_invalid}")

                # Create datetime column
                df['datetime'] = pd.to_datetime(
                    df['YR'].astype(str) + '-' + 
                    df['MO'].astype(str).str.zfill(2) + '-' + 
                    df['DA'].astype(str).str.zfill(2) + ' ' + 
                    df['HH'] + ':' + df['MM'],
                    errors='coerce'
                )
                
                # Log and drop invalid dates
                invalid_dates = df['datetime'].isna().sum()
                if invalid_dates > 0:
                    sample_invalid_dates = df[df['datetime'].isna()][['YR', 'MO', 'DA', 'HH', 'MM']].head(5).to_dict()
                    logger.warning(f"{instrument}: {invalid_dates} invalid datetime entries dropped. Sample: {sample_invalid_dates}")
                df = df.dropna(subset=['datetime']).sort_values('datetime')
                
                if len(df) == 0:
                    logger.error(f"{instrument}: No valid data after datetime parsing")
                    continue

                # Convert numeric columns to float
                exclude_cols = ['YR', 'MO', 'DA', 'HHMM', 'HH', 'MM', 'Julian_Day', 'Seconds_of_Day', 'year', 'file']
                numeric_cols = [col for col in df.columns if col not in exclude_cols and col != 'datetime']
                for col in numeric_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    invalid_count = df[col].isna().sum()
                    if invalid_count > 0:
                        logger.warning(f"{instrument}: {col} has {invalid_count} non-numeric values converted to NaN")

                # Downsample large datasets to reduce memory usage (e.g., to 5-minute resolution for swepam)
                df = df.set_index('datetime')
                if instrument == 'swepam' and len(df) > 1_000_000:
                    logger.info(f"{instrument}: Downsampling to 5-minute resolution to reduce memory usage")
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    df = df[numeric_cols].resample('5min').mean().interpolate(method='time', limit_direction='both')
                else:
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    df = df[numeric_cols].resample(self.time_resolutions[instrument], label='right').mean().interpolate(method='time', limit_direction='both')
                
                df = df.reset_index()
                
                self.data[instrument] = df
                logger.info(f"Loaded {instrument} data: {len(df)} records from {df['datetime'].min()} to {df['datetime'].max()}")
                
            except Exception as e:
                logger.error(f"Error loading {instrument} data: {str(e)}")
    
    def preprocess_data(self):
        """Preprocess data for CME detection"""
        logger.info("Preprocessing data...")
        
        for instrument, df in self.data.items():
            try:
                processed_df = df.copy()

                # Ensure datetime is valid
                if 'datetime' not in processed_df.columns or not pd.api.types.is_datetime64_any_dtype(processed_df['datetime']):
                    logger.error(f"Invalid datetime column for {instrument}")
                    continue
                
                # Set DatetimeIndex
                processed_df = processed_df.set_index('datetime')
                processed_df = processed_df.sort_index()

                # Identify numeric columns
                numeric_cols = processed_df.select_dtypes(include=[np.number]).columns

                # Replace invalid values with NaN
                for col in numeric_cols:
                    processed_df[col] = processed_df[col].replace([9, 99, 999, 9999, -999, -99, -9], np.nan)

                # Log missing values
                missing_counts = processed_df[numeric_cols].isna().sum()
                for col, count in missing_counts.items():
                    if count > 0:
                        logger.warning(f"{instrument}: {col} has {count} missing values")

                # Fill missing values
                processed_df[numeric_cols] = processed_df[numeric_cols].ffill().bfill()
                processed_df[numeric_cols] = processed_df[numeric_cols].interpolate(method='time', limit_direction='both')

                # Remove extreme outliers
                for col in numeric_cols:
                    if processed_df[col].notna().sum() > 100:
                        Q1 = processed_df[col].quantile(0.25)
                        Q3 = processed_df[col].quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 3 * IQR
                        upper_bound = Q3 + 3 * IQR
                        outlier_mask = (processed_df[col] < lower_bound) | (processed_df[col] > upper_bound)
                        processed_df.loc[outlier_mask, col] = np.nan
                        processed_df[col] = processed_df[col].interpolate(method='time', limit_direction='both')

                processed_df = processed_df.reset_index()
                self.processed_data[instrument] = processed_df
                logger.info(f"Preprocessed {instrument} data successfully")

            except Exception as e:
                logger.error(f"Error preprocessing {instrument} data: {str(e)}")
    
    def derive_features(self):
        """Derive advanced features for CME detection"""
        logger.info("Deriving advanced features...")
        
        for instrument, df in self.processed_data.items():
            try:
                if len(df) == 0:
                    logger.warning(f"Skipping feature derivation for {instrument}: empty dataset")
                    continue
                
                df = df.set_index('datetime')
                if instrument == 'swepam':
                    df['speed_ma_1h'] = df['Bulk_Speed'].rolling(window='60min', center=True, min_periods=10).mean()
                    df['speed_gradient'] = df['Bulk_Speed'].diff()
                    df['speed_enhancement'] = df['Bulk_Speed'] - df['speed_ma_1h']
                    
                    df['density_ma_1h'] = df['Proton_Density'].rolling(window='60min', center=True, min_periods=10).mean()
                    df['density_enhancement'] = df['Proton_Density'] / df['density_ma_1h']
                    
                    df['temp_ma_1h'] = df['Ion_Temperature'].rolling(window='60min', center=True, min_periods=10).mean()
                    df['temp_depression'] = df['temp_ma_1h'] / df['Ion_Temperature']
                    
                    df['dynamic_pressure'] = df['Proton_Density'] * df['Bulk_Speed']**2
                    df['pressure_ma_1h'] = df['dynamic_pressure'].rolling(window='60min', center=True, min_periods=10).mean()
                    df['pressure_enhancement'] = df['dynamic_pressure'] / df['pressure_ma_1h']
                    
                elif instrument == 'mag':
                    df['Bt_ma_1h'] = df['Bt'].rolling(window='60min', center=True, min_periods=10).mean()
                    df['field_enhancement'] = df['Bt'] / df['Bt_ma_1h']
                    
                    df['field_rotation'] = np.sqrt(df['Bx'].diff()**2 + df['By'].diff()**2 + df['Bz'].diff()**2)
                    df['rotation_ma_1h'] = df['field_rotation'].rolling(window='60min', center=True, min_periods=10).mean()
                    
                    if 'swepam' in self.processed_data:
                        swepam_aligned = self.processed_data['swepam'].set_index('datetime')
                        mag_aligned = df
                        common_times = swepam_aligned.index.intersection(mag_aligned.index)
                        if len(common_times) > 100:
                            temp_aligned = swepam_aligned.loc[common_times, 'Ion_Temperature']
                            density_aligned = swepam_aligned.loc[common_times, 'Proton_Density']
                            bt_aligned = mag_aligned.loc[common_times, 'Bt']
                            beta = (2e-6 * 1.38e-23 * temp_aligned * density_aligned * 1e6) / (bt_aligned**2 * 1e-18 / (2 * 4e-7 * np.pi))
                            df.loc[common_times, 'plasma_beta'] = beta
                
                elif instrument in ['epam', 'sis']:
                    flux_cols = [col for col in df.columns if 'Proton' in col and col not in ['YR', 'MO', 'DA', 'HH', 'MM']]
                    if not flux_cols:
                        flux_cols = [col for col in df.columns if any(keyword in col for keyword in ['Electron', 'Anisotropy', 'MeV']) and col not in ['YR', 'MO', 'DA', 'HH', 'MM', 'year', 'file']]
                    
                    for col in flux_cols[:5]:
                        if col in df.columns and df[col].dtype in ['float64', 'int64', 'float32', 'int32']:
                            df[f'{col}_ma_1h'] = df[col].rolling(window='60min', center=True, min_periods=10).mean()
                            df[f'{col}_enhancement'] = df[col] / df[f'{col}_ma_1h']
                            df[f'{col}_gradient'] = df[col].diff()
                
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                exclude_cols = ['YR', 'MO', 'DA', 'HHMM', 'HH', 'MM', 'Julian_Day', 'Seconds_of_Day', 'year', 'file']
                feature_cols = [col for col in numeric_cols if col not in exclude_cols and 'ma_' not in col]
                
                for col in feature_cols[:5]:
                    if col in df.columns:
                        df[f'{col}_variance'] = df[col].rolling(window='60min', min_periods=10).var()
                
                self.processed_data[instrument] = df.reset_index()
                logger.info(f"Derived features for {instrument}")
                
            except Exception as e:
                logger.error(f"Error deriving features for {instrument}: {str(e)}")
    
    def detect_speed_enhancements(self, df, threshold_factor=1.5):
        """Detect solar wind speed enhancements"""
        if 'speed_enhancement' not in df.columns:
            return pd.Series(False, index=df.index)
        
        background_std = df['speed_enhancement'].rolling(window='1440min', min_periods=100).std()
        threshold = threshold_factor * background_std
        return df['speed_enhancement'] > threshold
    
    def detect_density_enhancements(self, df, threshold_factor=1.2):
        """Detect proton density enhancements"""
        if 'density_enhancement' not in df.columns:
            return pd.Series(False, index=df.index)
        
        return df['density_enhancement'] > threshold_factor
    
    def detect_temperature_depressions(self, df, threshold_factor=1.2):
        """Detect ion temperature depressions"""
        if 'temp_depression' not in df.columns:
            return pd.Series(False, index=df.index)
        
        return df['temp_depression'] > threshold_factor
    
    def detect_particle_flux_enhancements(self, df, threshold_factor=2.0):
        """Detect energetic particle flux enhancements"""
        enhancement_cols = [col for col in df.columns if 'enhancement' in col and 'Proton' in col]
        
        if not enhancement_cols:
            return pd.Series(False, index=df.index)
        
        detections = pd.DataFrame(False, index=df.index, columns=enhancement_cols)
        for col in enhancement_cols:
            detections[col] = df[col] > threshold_factor
        
        return detections.any(axis=1)
    
    def detect_magnetic_field_rotations(self, df, threshold_degrees=20):
        """Detect magnetic field rotations"""
        if 'field_rotation' not in df.columns:
            return pd.Series(False, index=df.index)
        
        rotation_degrees = df['field_rotation'] * 180 / np.pi
        return rotation_degrees > threshold_degrees
    
    def composite_cme_detection(self):
        """Perform composite CME detection using multiple signatures"""
        logger.info("Performing composite CME detection...")
        
        all_detections = []
        
        for instrument, df in self.processed_data.items():
            try:
                if len(df) == 0:
                    logger.warning(f"Skipping CME detection for {instrument}: empty dataset")
                    continue
                
                detections = pd.DataFrame({
                    'datetime': df['datetime'],
                    'instrument': instrument
                })
                
                df = df.set_index('datetime')
                if instrument == 'swepam':
                    detections['speed_enhancement'] = self.detect_speed_enhancements(df)
                    detections['density_enhancement'] = self.detect_density_enhancements(df)
                    detections['temp_depression'] = self.detect_temperature_depressions(df)
                    detections['swepam_score'] = (
                        detections['speed_enhancement'].astype(int) +
                        detections['density_enhancement'].astype(int) +
                        detections['temp_depression'].astype(int)
                    )
                    detections['cme_detected'] = detections['swepam_score'] >= 2
                
                elif instrument == 'mag':
                    detections['field_rotation'] = self.detect_magnetic_field_rotations(df)
                    detections['cme_detected'] = detections['field_rotation']
                
                elif instrument in ['epam', 'sis']:
                    detections['particle_enhancement'] = self.detect_particle_flux_enhancements(df)
                    detections['cme_detected'] = detections['particle_enhancement']
                
                signature_cols = [col for col in detections.columns if col in [
                    'speed_enhancement', 'density_enhancement', 'temp_depression', 
                    'field_rotation', 'particle_enhancement'
                ]]
                detections['confidence'] = detections[signature_cols].sum(axis=1) / max(1, len(signature_cols))
                
                all_detections.append(detections)
                self.detection_results[instrument] = detections
                logger.info(f"CME detection completed for {instrument}: {detections['cme_detected'].sum()} events detected")
                
            except Exception as e:
                logger.error(f"Error in CME detection for {instrument}: {str(e)}")
        
        return all_detections
    
    def merge_detections(self, time_window_hours=2):
        """Merge detections from different instruments within time windows"""
        logger.info("Merging detections from multiple instruments...")
        
        if not self.detection_results:
            logger.warning("No detection results to merge")
            return None
        
        all_events = []
        for instrument, detections in self.detection_results.items():
            events = detections[detections['cme_detected'] == True].copy()
            if len(events) > 0:
                events['source_instrument'] = instrument
                all_events.append(events[['datetime', 'confidence', 'source_instrument']])
        
        if not all_events:
            logger.info("No CME events detected by any instrument")
            return pd.DataFrame()
        
        combined_events = pd.concat(all_events, ignore_index=True)
        combined_events = combined_events.sort_values('datetime').reset_index(drop=True)
        
        merged_events = []
        time_window = timedelta(hours=time_window_hours)
        
        i = 0
        while i < len(combined_events):
            event_start = combined_events.loc[i, 'datetime']
            event_end = event_start + time_window
            
            window_events = combined_events[
                (combined_events['datetime'] >= event_start) &
                (combined_events['datetime'] <= event_end)
            ]
            
            merged_event = {
                'start_time': window_events['datetime'].min(),
                'end_time': window_events['datetime'].max(),
                'duration_hours': (window_events['datetime'].max() - window_events['datetime'].min()).total_seconds() / 3600,
                'instruments': ', '.join(np.unique(window_events['source_instrument'])),
                'num_instruments': len(np.unique(window_events['source_instrument'])),
                'avg_confidence': window_events['confidence'].mean(),
                'max_confidence': window_events['confidence'].max()
            }
            
            merged_events.append(merged_event)
            i = len(combined_events[combined_events['datetime'] <= event_end])
        
        merged_df = pd.DataFrame(merged_events)
        logger.info(f"Merged {len(combined_events)} individual detections into {len(merged_df)} CME events")
        return merged_df
    
    def validate_cme_events(self, merged_events, min_duration_hours=2, min_instruments=1, min_confidence=0.2):
        """Validate CME events based on physical criteria"""
        logger.info("Validating CME events...")
        
        if merged_events is None or len(merged_events) == 0:
            logger.info("No events to validate")
            return pd.DataFrame()
        
        valid_events = merged_events[
            (merged_events['duration_hours'] >= min_duration_hours) &
            (merged_events['num_instruments'] >= min_instruments) &
            (merged_events['avg_confidence'] >= min_confidence)
        ].copy()
        
        def classify_event(row):
            if row['num_instruments'] >= 3 and row['avg_confidence'] > 0.6:
                return 'High Confidence'
            elif row['num_instruments'] >= 2 and row['avg_confidence'] > 0.4:
                return 'Medium Confidence'
            else:
                return 'Low Confidence'
        
        valid_events['classification'] = valid_events.apply(classify_event, axis=1)
        logger.info(f"Validated {len(valid_events)} CME events out of {len(merged_events)} candidates")
        return valid_events
    
    def plot_detection_overview(self, start_date=None, end_date=None, figsize=(15, 15)):
        """Plot overview of CME detections with enhanced visualization"""
        logger.info("Creating detection overview plot...")
        
        fig, axes = plt.subplots(len(self.processed_data) + 1, 1, figsize=figsize, sharex=True)
        if len(self.processed_data) == 0:
            logger.warning("No data to plot")
            return
        
        if len(self.processed_data) == 1:
            axes = [axes]
        
        for i, (instrument, df) in enumerate(self.processed_data.items()):
            if len(df) == 0:
                logger.warning(f"Skipping plot for {instrument}: empty dataset")
                continue
                
            ax = axes[i]
            
            if start_date and end_date:
                mask = (df['datetime'] >= pd.to_datetime(start_date)) & (df['datetime'] <= pd.to_datetime(end_date))
                df_plot = df[mask]
            else:
                df_plot = df.head(10000)
            
            if instrument == 'swepam':
                ax2 = ax.twinx()
                l1 = ax.plot(df_plot['datetime'], df_plot['Bulk_Speed'], 'b-', alpha=0.7, label='Solar Wind Speed')
                l2 = ax2.plot(df_plot['datetime'], df_plot['Proton_Density'], 'r-', alpha=0.7, label='Proton Density')
                ax.set_ylabel('Speed (km/s)', color='b')
                ax2.set_ylabel('Density (cm⁻³)', color='r')
                
                if instrument in self.detection_results:
                    detections = self.detection_results[instrument]
                    detection_times = detections[detections['cme_detected'] == True]['datetime']
                    for det_time in detection_times:
                        ax.axvline(x=det_time, color='red', alpha=0.5, linestyle='--', label='CME Detection' if det_time == detection_times.iloc[0] else '')
            
            elif instrument == 'mag':
                ax.plot(df_plot['datetime'], df_plot['Bt'], 'g-', alpha=0.7, label='|B| Total')
                ax.set_ylabel('Magnetic Field (nT)', color='g')
                
                if instrument in self.detection_results:
                    detections = self.detection_results[instrument]
                    detection_times = detections[detections['cme_detected'] == True]['datetime']
                    for det_time in detection_times:
                        ax.axvline(x=det_time, color='red', alpha=0.5, linestyle='--', label='CME Detection' if det_time == detection_times.iloc[0] else '')
            
            elif instrument in ['epam', 'sis']:
                flux_cols = [col for col in df_plot.columns if 'Proton' in col and col not in ['YR', 'MO', 'DA', 'HH', 'MM']][:3]
                colors = ['purple', 'orange', 'brown']
                
                for j, col in enumerate(flux_cols):
                    if col in df_plot.columns:
                        ax.plot(df_plot['datetime'], df_plot[col], color=colors[j % len(colors)], 
                               alpha=0.7, label=col, linewidth=0.8)
                
                ax.set_ylabel('Particle Flux')
                ax.set_yscale('log')
                
                if instrument in self.detection_results:
                    detections = self.detection_results[instrument]
                    detection_times = detections[detections['cme_detected'] == True]['datetime']
                    for det_time in detection_times:
                        ax.axvline(x=det_time, color='red', alpha=0.5, linestyle='--', label='CME Detection' if det_time == detection_times.iloc[0] else '')
            
            ax.set_title(f'{instrument.upper()} - CME Detection Overview', fontsize=10)
            ax.grid(True, alpha=0.3)
            ax.legend(loc='upper left')
            if instrument == 'swepam':
                ax2.legend(loc='upper right')
        
        ax = axes[-1]
        merged_events = self.merge_detections()
        if not merged_events.empty:
            for idx, event in merged_events.iterrows():
                ax.axvspan(event['start_time'], event['end_time'], color='orange', alpha=0.3, 
                          label=f"CME Event ({event['classification']})" if idx == 0 else '')
                ax.text(event['start_time'], 0.5, f"Event {idx+1}\n{event['classification']}", 
                        rotation=90, va='center', ha='right', fontsize=8)
        
        ax.set_ylabel('CME Events')
        ax.set_ylim(0, 1)
        ax.set_title('Merged CME Events Across All Instruments', fontsize=10)
        ax.legend(loc='upper left')
        
        plt.xlabel('Time')
        plt.suptitle('CME Detection System - Multi-Instrument Overview', fontsize=16, fontweight='bold')
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig('cme_detection_overview.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        logger.info("Detection overview plot saved as 'cme_detection_overview.png'")
    
    def generate_report(self, valid_events=None):
        """Generate comprehensive CME detection report"""
        logger.info("Generating CME detection report...")
        
        report = []
        report.append("=" * 80)
        report.append("ADITYA-L1 SWIS CME DETECTION SYSTEM - ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("DATA SUMMARY:")
        report.append("-" * 40)
        for instrument, df in self.processed_data.items():
            report.append(f"{instrument.upper()}: {len(df):,} records")
            report.append(f"  Time range: {df['datetime'].min()} to {df['datetime'].max()}")
            report.append(f"  Duration: {(df['datetime'].max() - df['datetime'].min()).days if len(df) > 0 else 0} days")
        report.append("")
        
        report.append("DETECTION RESULTS:")
        report.append("-" * 40)
        total_detections = 0
        for instrument, detections in self.detection_results.items():
            num_detections = detections['cme_detected'].sum() if len(detections) > 0 else 0
            total_detections += num_detections
            report.append(f"{instrument.upper()}: {num_detections} CME signatures detected")
        
        report.append(f"TOTAL INDIVIDUAL DETECTIONS: {total_detections}")
        report.append("")
        
        if valid_events is not None and len(valid_events) > 0:
            report.append("VALIDATED CME EVENTS:")
            report.append("-" * 40)
            report.append(f"Total validated events: {len(valid_events)}")
            
            for classification in valid_events['classification'].unique():
                count = len(valid_events[valid_events['classification'] == classification])
                report.append(f"{classification}: {count} events")
            
            report.append("")
            report.append("EVENT DETAILS:")
            report.append("-" * 40)
            
            for idx, event in valid_events.iterrows():
                report.append(f"Event {idx + 1}:")
                report.append(f"  Start: {event['start_time']}")
                report.append(f"  Duration: {event['duration_hours']:.1f} hours")
                report.append(f"  Instruments: {event['instruments']}")
                report.append(f"  Confidence: {event['avg_confidence']:.2f}")
                report.append(f"  Classification: {event['classification']}")
                report.append("")
        
        report.append("DETECTION STATISTICS:")
        report.append("-" * 40)
        if valid_events is not None and len(valid_events) > 0:
            avg_duration = valid_events['duration_hours'].mean()
            max_duration = valid_events['duration_hours'].max()
            avg_confidence = valid_events['avg_confidence'].mean()
            report.append(f"Average event duration: {avg_duration:.1f} hours")
            report.append(f"Maximum event duration: {max_duration:.1f} hours")
            report.append(f"Average confidence: {avg_confidence:.2f}")
            multi_instrument = valid_events[valid_events['num_instruments'] > 1]
            correlation_rate = len(multi_instrument) / len(valid_events) * 100 if len(valid_events) > 0 else 0
            report.append(f"Multi-instrument correlation rate: {correlation_rate:.1f}%")
        
        report.append("")
        report.append("=" * 80)
        
        report_text = "\n".join(report)
        with open('cme_detection_report.txt', 'w') as f:
            f.write(report_text)
        
        print(report_text)
        logger.info("Report saved as 'cme_detection_report.txt'")
        
        return report_text
    
    def run_full_analysis(self):
        """Run complete CME detection analysis"""
        logger.info("Starting full CME detection analysis...")
        
        try:
            self.load_data()
            self.preprocess_data()
            self.derive_features()
            self.composite_cme_detection()
            merged_events = self.merge_detections()
            valid_events = self.validate_cme_events(merged_events)
            self.plot_detection_overview()
            self.generate_report(valid_events)
            logger.info("CME detection analysis completed successfully!")
            return valid_events
            
        except Exception as e:
            logger.error(f"Error in full analysis: {str(e)}")
            raise