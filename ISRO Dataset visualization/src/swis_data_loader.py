"""
SWIS Data Loader for Aditya-L1 ASPEX instrument
Loads and processes CDF files containing solar wind ion spectrometer data
"""

import os
import glob
import numpy as np
import pandas as pd
import spacepy.pycdf as cdf
from datetime import datetime, timedelta
import torch
import torch.nn.functional as F
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class SWISDataLoader:
    """
    Data loader for ASPEX-SWIS Level-2 data from Aditya-L1 mission
    Processes bulk parameters and energy spectra for CME detection
    """
    
    def __init__(self, data_dir: str = "cdf_data", device: str = "cuda"):
        self.data_dir = data_dir
        self.device = device if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # CME characteristic thresholds (based on literature)
        self.cme_thresholds = {
            'proton_density_increase': 2.0,  # Factor increase
            'proton_speed_increase': 1.5,    # Factor increase
            'proton_thermal_increase': 2.0,  # Factor increase
            'alpha_proton_ratio_increase': 2.0,  # Factor increase
            'minimum_duration_minutes': 30,   # Minimum event duration
            'background_window_hours': 6,     # Hours for background calculation
        }
        
    def get_available_dates(self) -> List[str]:
        """Get list of available dates with L2 data"""
        date_dirs = glob.glob(os.path.join(self.data_dir, "20*"))
        dates = []
        
        for date_dir in date_dirs:
            date = os.path.basename(date_dir)
            # Check if BLK file exists for this date
            blk_files = glob.glob(os.path.join(date_dir, "*L2_BLK*.cdf"))
            if blk_files:
                dates.append(date)
        
        return sorted(dates)
    
    def load_single_day(self, date: str) -> Optional[pd.DataFrame]:
        """
        Load and process SWIS data for a single day
        
        Args:
            date: Date string in format YYYYMMDD
            
        Returns:
            DataFrame with processed solar wind parameters
        """
        date_dir = os.path.join(self.data_dir, date)
        
        # Find BLK file for bulk parameters
        blk_files = glob.glob(os.path.join(date_dir, "*L2_BLK*.cdf"))
        if not blk_files:
            print(f"No BLK file found for {date}")
            return None
            
        blk_file = blk_files[0]
        
        try:
            with cdf.CDF(blk_file) as data:
                # Extract time and convert to datetime
                epoch = data['epoch_for_cdf_mod'][:]
                timestamps = [datetime(1970, 1, 1) + timedelta(seconds=float(t)) for t in epoch]
                
                # Extract bulk parameters
                df = pd.DataFrame({
                    'timestamp': timestamps,
                    'proton_density': data['proton_density'][:],
                    'proton_density_error': data['numden_p_uncer'][:],
                    'proton_bulk_speed': data['proton_bulk_speed'][:],
                    'proton_speed_error': data['bulk_p_uncer'][:],
                    'proton_vx': data['proton_xvelocity'][:],
                    'proton_vy': data['proton_yvelocity'][:],
                    'proton_vz': data['proton_zvelocity'][:],
                    'proton_thermal_speed': data['proton_thermal'][:],
                    'proton_thermal_error': data['thermal_p_uncer'][:],
                    'alpha_density': data['alpha_density'][:],
                    'alpha_density_error': data['numden_a_uncer'][:],
                    'alpha_bulk_speed': data['alpha_bulk_speed'][:],
                    'alpha_speed_error': data['bulk_a_uncer'][:],
                    'alpha_thermal_speed': data['alpha_thermal'][:],
                    'alpha_thermal_error': data['thermal_a_uncer'][:],
                    'spacecraft_x': data['spacecraft_xpos'][:],
                    'spacecraft_y': data['spacecraft_ypos'][:],
                    'spacecraft_z': data['spacecraft_zpos'][:],
                })
                
                # Calculate derived parameters
                df['total_proton_speed'] = np.sqrt(df['proton_vx']**2 + df['proton_vy']**2 + df['proton_vz']**2)
                df['alpha_proton_ratio'] = df['alpha_density'] / (df['proton_density'] + 1e-10)
                df['dynamic_pressure'] = df['proton_density'] * df['proton_bulk_speed']**2 * 1.67e-27 * 1e9  # nPa
                
                # Quality filtering
                df = self._apply_quality_filters(df)
                
                return df
                
        except Exception as e:
            print(f"Error loading {date}: {e}")
            return None
    
    def _apply_quality_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply quality filters to remove bad data points"""
        # Remove negative or zero values
        df = df[df['proton_density'] > 0]
        df = df[df['proton_bulk_speed'] > 0]
        df = df[df['alpha_density'] >= 0]
        
        # Remove extreme outliers (beyond 5 sigma)
        for col in ['proton_density', 'proton_bulk_speed', 'proton_thermal_speed']:
            mean_val = df[col].mean()
            std_val = df[col].std()
            df = df[np.abs(df[col] - mean_val) < 5 * std_val]
        
        return df.reset_index(drop=True)
    
    def load_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Load data for a date range
        
        Args:
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format
            
        Returns:
            Combined DataFrame for the date range
        """
        available_dates = self.get_available_dates()
        date_range = [d for d in available_dates if start_date <= d <= end_date]
        
        if not date_range:
            print(f"No data available for range {start_date} to {end_date}")
            return pd.DataFrame()
        
        print(f"Loading {len(date_range)} days of data...")
        
        all_data = []
        for date in date_range:
            df = self.load_single_day(date)
            if df is not None and len(df) > 0:
                all_data.append(df)
                print(f"Loaded {date}: {len(df)} data points")
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            combined_df = combined_df.sort_values('timestamp').reset_index(drop=True)
            print(f"Total data points: {len(combined_df)}")
            return combined_df
        else:
            return pd.DataFrame()
    
    def calculate_background_levels(self, df: pd.DataFrame, window_hours: int = 6) -> Dict[str, float]:
        """
        Calculate background solar wind levels using rolling median
        
        Args:
            df: DataFrame with solar wind data
            window_hours: Hours for background calculation
            
        Returns:
            Dictionary with background levels
        """
        window_size = window_hours * 3600 // 5  # Assuming ~5 second cadence
        
        background = {}
        for param in ['proton_density', 'proton_bulk_speed', 'proton_thermal_speed', 'alpha_proton_ratio']:
            if param in df.columns:
                background[param] = df[param].rolling(window=window_size, center=True).median()
        
        return background
    
    def prepare_for_ml(self, df: pd.DataFrame, sequence_length: int = 360) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Prepare data for machine learning models
        
        Args:
            df: DataFrame with solar wind data
            sequence_length: Length of input sequences (in time steps)
            
        Returns:
            Tuple of (features, targets) as PyTorch tensors
        """
        # Select features for ML
        feature_cols = [
            'proton_density', 'proton_bulk_speed', 'proton_thermal_speed',
            'alpha_density', 'alpha_bulk_speed', 'alpha_thermal_speed',
            'alpha_proton_ratio', 'dynamic_pressure'
        ]
        
        # Normalize features
        features = df[feature_cols].values
        features_norm = (features - np.nanmean(features, axis=0)) / (np.nanstd(features, axis=0) + 1e-8)
        
        # Create sequences
        X, y = [], []
        for i in range(len(features_norm) - sequence_length):
            X.append(features_norm[i:i+sequence_length])
            # Simple anomaly target based on extreme values
            future_window = features_norm[i+sequence_length:i+sequence_length+60]  # Next hour
            if len(future_window) > 0:
                anomaly_score = np.mean(np.abs(future_window - np.mean(features_norm, axis=0)) > 2)
                y.append(1 if anomaly_score > 0.3 else 0)
            else:
                y.append(0)
        
        X = torch.tensor(np.array(X), dtype=torch.float32).to(self.device)
        y = torch.tensor(np.array(y), dtype=torch.float32).to(self.device)
        
        return X, y
    
    def detect_cme_candidates(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect potential CME events using threshold-based approach
        
        Args:
            df: DataFrame with solar wind data
            
        Returns:
            List of detected CME events
        """
        if len(df) < 1000:  # Need sufficient data
            return []
        
        # Calculate background levels
        background = self.calculate_background_levels(df)
        
        # Detect anomalies
        events = []
        in_event = False
        event_start = None
        
        for i, row in df.iterrows():
            anomaly_score = 0
            
            # Check each parameter against background
            for param, threshold in [
                ('proton_density', self.cme_thresholds['proton_density_increase']),
                ('proton_bulk_speed', self.cme_thresholds['proton_speed_increase']),
                ('proton_thermal_speed', self.cme_thresholds['proton_thermal_increase']),
                ('alpha_proton_ratio', self.cme_thresholds['alpha_proton_ratio_increase'])
            ]:
                if param in background and not pd.isna(background[param].iloc[i]):
                    ratio = row[param] / (background[param].iloc[i] + 1e-10)
                    if ratio > threshold:
                        anomaly_score += 1
            
            # Event detection logic
            if anomaly_score >= 2 and not in_event:  # Start of event
                in_event = True
                event_start = i
            elif anomaly_score < 2 and in_event:  # End of event
                in_event = False
                duration_minutes = (df.iloc[i]['timestamp'] - df.iloc[event_start]['timestamp']).total_seconds() / 60
                
                if duration_minutes >= self.cme_thresholds['minimum_duration_minutes']:
                    event = {
                        'start_time': df.iloc[event_start]['timestamp'],
                        'end_time': df.iloc[i]['timestamp'],
                        'duration_minutes': duration_minutes,
                        'max_proton_density': df.iloc[event_start:i]['proton_density'].max(),
                        'max_proton_speed': df.iloc[event_start:i]['proton_bulk_speed'].max(),
                        'max_alpha_ratio': df.iloc[event_start:i]['alpha_proton_ratio'].max(),
                        'event_strength': anomaly_score
                    }
                    events.append(event)
        
        return events


def main():
    """Test the SWIS data loader"""
    loader = SWISDataLoader()
    
    # Get available dates
    dates = loader.get_available_dates()
    print(f"Available dates: {len(dates)}")
    print(f"Date range: {dates[0]} to {dates[-1]}")
    
    # Load a few days of data
    if len(dates) >= 3:
        df = loader.load_date_range(dates[0], dates[2])
        
        if len(df) > 0:
            print(f"\nData summary:")
            print(df.describe())
            
            # Detect CME candidates
            events = loader.detect_cme_candidates(df)
            print(f"\nDetected {len(events)} potential CME events")
            
            for i, event in enumerate(events):
                print(f"Event {i+1}:")
                print(f"  Time: {event['start_time']} to {event['end_time']}")
                print(f"  Duration: {event['duration_minutes']:.1f} minutes")
                print(f"  Max density: {event['max_proton_density']:.2f} cm⁻³")
                print(f"  Max speed: {event['max_proton_speed']:.1f} km/s")


if __name__ == "__main__":
    main()
