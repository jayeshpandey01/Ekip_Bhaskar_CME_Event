
"""
Test script to diagnose CME detection data loading issues
"""

import pandas as pd
import numpy as np
from datetime import datetime

def check_data_files():
    """Check all CSV files and their structure"""
    print("=" * 60)
    print("CME DETECTION DATA DIAGNOSTIC")
    print("=" * 60)
    
    data_path = "csv_file"
    
    # Define file mappings
    file_mapping = {
        'swepam': 'ace_swepam_data.csv',
        'mag': 'ace_mag_data.csv', 
        'epam': 'ace_epam_data.csv',
        'sis': 'ace_sis_data.csv'
    }
    
    all_data = {}
    
    for instrument, filename in file_mapping.items():
        filepath = f"{data_path}/{filename}"
        print(f"\nChecking {instrument} data ({filename}):")
        print("-" * 40)
        
        try:
            # Load the CSV file
            df = pd.read_csv(filepath)
            
            # Check if first row contains column headers
            if df.iloc[0].astype(str).str.contains('YR|MO|DA').any():
                print("First row contains headers, adjusting...")
                df.columns = df.iloc[0]
                df = df[1:].reset_index(drop=True)
            
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            
            # Check data types
            print(f"Data types:")
            for col in df.columns:
                print(f"  {col}: {df[col].dtype}")
            
            # Check for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            print(f"Numeric columns: {numeric_cols}")
            
            # Try to create datetime
            try:
                df['datetime'] = pd.to_datetime(
                    df['YR'].astype(int).astype(str) + '-' + 
                    df['MO'].astype(int).astype(str).str.zfill(2) + '-' + 
                    df['DA'].astype(int).astype(str).str.zfill(2) + ' ' + 
                    df['HHMM'].astype(int).astype(str).str.zfill(4).str[:2] + ':' + 
                    df['HHMM'].astype(int).astype(str).str.zfill(4).str[2:], 
                    errors='coerce'
                )
                
                valid_dates = df['datetime'].notna().sum()
                print(f"Valid dates created: {valid_dates}/{len(df)}")
                
                if valid_dates > 0:
                    df_clean = df.dropna(subset=['datetime'])
                    print(f"Date range: {df_clean['datetime'].min()} to {df_clean['datetime'].max()}")
            
            except Exception as date_error:
                print(f"Error creating datetime: {date_error}")
            
            # Check for CME-relevant columns
            print(f"Sample data (first 3 rows):")
            print(df.head(3))
            
            all_data[instrument] = df
            print(f"✓ {instrument} data loaded successfully")
            
        except Exception as e:
            print(f"✗ Error loading {instrument} data: {str(e)}")
    
    return all_data

def test_cme_signatures(data):
    """Test for CME signature detection capability"""
    print(f"\n" + "=" * 60)
    print("CME SIGNATURE DETECTION TEST")
    print("=" * 60)
    
    for instrument, df in data.items():
        print(f"\n{instrument.upper()} Analysis:")
        print("-" * 30)
        
        if instrument == 'swepam':
            # Test solar wind parameters
            key_params = ['Bulk_Speed', 'Proton_Density', 'Ion_Temperature']
            for param in key_params:
                if param in df.columns:
                    values = pd.to_numeric(df[param], errors='coerce')
                    print(f"{param}: mean={values.mean():.2f}, std={values.std():.2f}, range=[{values.min():.2f}, {values.max():.2f}]")
                else:
                    print(f"{param}: NOT FOUND")
        
        elif instrument == 'mag':
            # Test magnetic field parameters
            key_params = ['Bt', 'Bx', 'By', 'Bz']
            for param in key_params:
                if param in df.columns:
                    values = pd.to_numeric(df[param], errors='coerce')
                    print(f"{param}: mean={values.mean():.2f}, std={values.std():.2f}, range=[{values.min():.2f}, {values.max():.2f}]")
                else:
                    print(f"{param}: NOT FOUND")
        
        elif instrument in ['epam', 'sis']:
            # Test particle flux parameters
            flux_cols = [col for col in df.columns if any(keyword in col for keyword in ['Proton', 'Electron', 'MeV'])]
            print(f"Found {len(flux_cols)} particle flux columns:")
            for col in flux_cols[:5]:  # Show first 5
                values = pd.to_numeric(df[col], errors='coerce')
                print(f"  {col}: mean={values.mean():.2f}, std={values.std():.2f}")

def run_simple_cme_detection(data):
    """Run a simplified CME detection test"""
    print(f"\n" + "=" * 60)
    print("SIMPLE CME DETECTION TEST")
    print("=" * 60)
    
    total_detections = 0
    
    for instrument, df in data.items():
        print(f"\n{instrument.upper()} Detection:")
        print("-" * 25)
        
        detections = 0
        
        if instrument == 'swepam':
            # Simple speed enhancement detection
            if 'Bulk_Speed' in df.columns:
                speeds = pd.to_numeric(df['Bulk_Speed'], errors='coerce')
                speed_mean = speeds.mean()
                speed_std = speeds.std()
                threshold = speed_mean + 2 * speed_std
                
                enhancements = speeds > threshold
                detections = enhancements.sum()
                print(f"Speed threshold: {threshold:.2f} km/s")
                print(f"Speed enhancements detected: {detections}")
        
        elif instrument == 'mag':
            # Simple magnetic field rotation detection
            if all(col in df.columns for col in ['Bx', 'By', 'Bz']):
                bx = pd.to_numeric(df['Bx'], errors='coerce')
                by = pd.to_numeric(df['By'], errors='coerce')
                bz = pd.to_numeric(df['Bz'], errors='coerce')
                
                # Calculate field changes
                field_changes = np.sqrt(bx.diff()**2 + by.diff()**2 + bz.diff()**2)
                threshold = field_changes.quantile(0.95)
                
                rotations = field_changes > threshold
                detections = rotations.sum()
                print(f"Field rotation threshold: {threshold:.2f}")
                print(f"Field rotations detected: {detections}")
        
        elif instrument in ['epam', 'sis']:
            # Simple particle flux enhancement detection
            flux_cols = [col for col in df.columns if any(keyword in col for keyword in ['Proton', 'Electron'])]
            if flux_cols:
                col = flux_cols[0]  # Use first flux column
                fluxes = pd.to_numeric(df[col], errors='coerce')
                flux_mean = fluxes.mean()
                flux_std = fluxes.std()
                threshold = flux_mean + 3 * flux_std
                
                enhancements = fluxes > threshold
                detections = enhancements.sum()
                print(f"Flux threshold: {threshold:.2e}")
                print(f"Flux enhancements detected: {detections}")
        
        total_detections += detections
        print(f"Total detections for {instrument}: {detections}")
    
    print(f"\nOVERALL RESULTS:")
    print(f"Total detections across all instruments: {total_detections}")
    
    if total_detections == 0:
        print("\n⚠️  NO CME EVENTS DETECTED!")
        print("Possible issues:")
        print("1. Thresholds are too high")
        print("2. Data quality issues")
        print("3. No actual CME events in the data period")
        print("4. Algorithm needs adjustment")
    else:
        print(f"\n✓ {total_detections} potential CME signatures detected!")

if __name__ == "__main__":
    # Run diagnostic tests
    data = check_data_files()
    
    if data:
        test_cme_signatures(data)
        run_simple_cme_detection(data)
    else:
        print("No data loaded successfully.")
