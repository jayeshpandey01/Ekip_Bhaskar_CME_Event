import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import spacepy.pycdf as pycdf
from spacepy import pycdf
import shutil
import os

# rearrange distributed file accoeding to there dates
def filter_data_into_file(SRC_DIR, DEST_DIR):
    sample_df = pd.DataFrame(
        [(os.path.join(SRC_DIR, fname), fname) for fname in os.listdir(SRC_DIR)],
        columns=['file_path', 'label']
    )

    def make_folder(folder_name):
        os.makedirs(folder_name, exist_ok=True)

    def file_transfer(source, destination):
        shutil.move(source, destination)

    # Move files into new folders
    for _, row in sample_df.iterrows():
        image = row['file_path']
        # Adjust slicing as needed for your filenames
        folder_name = image[17:-24]
        dest_folder = os.path.join(DEST_DIR, folder_name)
        make_folder(dest_folder)
        dest_path = os.path.join(dest_folder, os.path.basename(image))
        file_transfer(image, dest_path)

# image dataframe
def prepare_data(image_path):
        image_data = pycdf.CDF(image_path)
        if 'L1_AUX' in image_path:
            df = pd.DataFrame({
                'epoch_for_cdf': image_data['epoch_for_cdf'][:, 0],
                'trig_counts': image_data['trig_counts'][:, 0, 0, 0],
                'coin_trig_counts': image_data['coin_trig_counts'][:, 0, 0],
                'coinc_trig_count_total': image_data['coinc_trig_count_total'][:, 0],
                'angle_tha1': image_data['angle_tha1'][:, 0, 0],
                'angle_tha2': image_data['angle_tha2'][:, 0, 0],
                'angle_xgse': image_data['angle_xgse'][:],
                'angle_ygse': image_data['angle_ygse'][:],
                'angle_zgse': image_data['angle_zgse'][:],
                'peak_det_counts': image_data['peak_det_counts'][:, 0, 0],
                'rej_counts': image_data['rej_counts'][:, 0, 0],
                'obs_time': image_data['obs_time'][:, 0],
                'spacecraft_xpos': image_data['spacecraft_xpos'][:],
                'spacecraft_xvel': image_data['spacecraft_xvel'][:],
                'spacecraft_ypos': image_data['spacecraft_ypos'][:],
                'spacecraft_yvel': image_data['spacecraft_yvel'][:],
                'spacecraft_zpos': image_data['spacecraft_zpos'][:],
                'spacecraft_zvel': image_data['spacecraft_zvel'][:]
            })
            return df

        elif 'L1_TH1' in image_path:
            df = pd.DataFrame({
                'epoch_for_cdf': image_data['epoch_for_cdf'][:, 0],
                'obs_time': image_data['obs_time'][:, 0],
                'THA-1_spec': image_data['THA-1_spec'],
                'fpga_ticks': image_data['fpga_ticks'],
                'frame_num': image_data['frame_num']
            })
            return df

        elif 'L2_BLK' in image_path:
            df = pd.DataFrame({
                'time': pd.to_datetime(image_data['epoch_for_cdf_mod'][:]),
                'proton_bulk_speed': image_data['proton_bulk_speed'][:],
                'alpha_bulk_speed': image_data['alpha_bulk_speed'][:],
                'alpha_density': image_data['alpha_density'][:],
                'alpha_thermal': image_data['alpha_thermal'][:],
                'proton_density': image_data['proton_density'][:],
                'proton_thermal': image_data['proton_thermal'][:],
                'proton_xvelocity': image_data['proton_xvelocity'][:],
                'proton_yvelocity': image_data['proton_yvelocity'][:],
                'proton_zvelocity': image_data['proton_zvelocity'][:],
                'spacecraft_xpos': image_data['spacecraft_xpos'][:],
                'spacecraft_ypos': image_data['spacecraft_ypos'][:],
                'spacecraft_zpos': image_data['spacecraft_zpos'][:]
            })
            return df

        elif 'L1_TH2' in image_path:
            df = pd.DataFrame({
                'epoch': image_data['epoch_for_cdf'][:, 0],
                'obs_time': image_data['obs_time'][:, 0],
                'fpga_ticks': image_data['fpga_ticks'][:],
                'frame_num': image_data['frame_num'][:],
                'tha2_spec': image_data['THA-2_spec'][:],
            })
            return df

        elif 'L2_TH1' in image_path:
            df = pd.DataFrame({
                'epoch': pd.to_datetime(image_data['epoch_for_cdf_mod'][:]),
                'spacecraft_xpos': image_data['spacecraft_xpos'][:],
                'spacecraft_ypos': image_data['spacecraft_ypos'][:],
                'spacecraft_zpos': image_data['spacecraft_zpos'][:],
            })

            # Optional: flatten sun_angle_tha1 (16 sectors × 3 components)
            sun_angle = image_data['sun_angle_tha1'][:]  # shape: [N, 16, 3]
            for sector in range(sun_angle.shape[1]):
                for comp in range(3):
                    df[f'sun_angle_s{sector}_c{comp}'] = sun_angle[:, sector, comp]

            return df
        # elif 'L2_TH2' in image_path:
        #     df = pd.DataFrame({
        #         'epoch': pd.to_datetime(image_data['epoch_for_cdf_mod'][:]),
        #         'spacecraft_xpos': image_data['spacecraft_xpos'][:],
        #         'spacecraft_ypos': image_data['spacecraft_ypos'][:],
        #         'spacecraft_zpos': image_data['spacecraft_zpos'][:],
        #         # Shape: (time, 32)
        #         'integrated_flux_mod': image_data['integrated_flux_mod'][:]
        #     })

        #     # Flatten sun_angle_tha2: [time, 32 sectors, 3 components]
            

        #     return df

        else:
            return None

# exception handling prepre data
def prepare_data_exception(file_paths):
    """
    Prepare data from a list of .cdf files into a unified DataFrame for training a model.
    Handles different row sizes with alignment and includes exception handling.
    
    Args:
        file_paths (list): List of paths to .cdf files.
    
    Returns:
        pd.DataFrame: Unified DataFrame with processed features, or None if processing fails.
    """
    dfs = []
    scaler = StandardScaler()
    
    try:
        for file_path in file_paths:
            if not isinstance(file_path, str) or not file_path.endswith('.cdf'):
                print(f"Skipping invalid file path: {file_path}")
                continue
            
            try:
                image_data = pycdf.CDF(file_path)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
            
            df = pd.DataFrame()
            if 'L1_AUX' in file_path:
                df = pd.DataFrame({
                    'epoch_for_cdf': image_data['epoch_for_cdf'][:, 0],
                    'trig_counts': image_data['trig_counts'][:, 0, 0, 0],
                    'coin_trig_counts': image_data['coin_trig_counts'][:, 0, 0],
                    'coinc_trig_count_total': image_data['coinc_trig_count_total'][:, 0],
                    'angle_tha1': image_data['angle_tha1'][:, 0, 0],
                    'angle_tha2': image_data['angle_tha2'][:, 0, 0],
                    'angle_xgse': image_data['angle_xgse'][:],
                    'angle_ygse': image_data['angle_ygse'][:],
                    'angle_zgse': image_data['angle_zgse'][:],
                    'peak_det_counts': image_data['peak_det_counts'][:, 0, 0],
                    'rej_counts': image_data['rej_counts'][:, 0, 0],
                    'obs_time': image_data['obs_time'][:, 0],
                    'spacecraft_xpos': image_data['spacecraft_xpos'][:],
                    'spacecraft_xvel': image_data['spacecraft_xvel'][:],
                    'spacecraft_ypos': image_data['spacecraft_ypos'][:],
                    'spacecraft_yvel': image_data['spacecraft_yvel'][:],
                    'spacecraft_zpos': image_data['spacecraft_zpos'][:],
                    'spacecraft_zvel': image_data['spacecraft_zvel'][:]
                })
                df['time'] = pd.to_datetime(df['epoch_for_cdf'])

            elif 'L1_TH1' in file_path:
                df = pd.DataFrame({
                    'epoch_for_cdf': image_data['epoch_for_cdf'][:, 0],
                    'obs_time': image_data['obs_time'][:, 0],
                    'THA-1_spec': image_data['THA-1_spec'],
                    'fpga_ticks': image_data['fpga_ticks'],
                    'frame_num': image_data['frame_num']
                })
                df['time'] = pd.to_datetime(df['epoch_for_cdf'])

            elif 'L2_BLK' in file_path:
                df = pd.DataFrame({
                    'time': pd.to_datetime(image_data['epoch_for_cdf_mod'][:]),
                    'proton_bulk_speed': image_data['proton_bulk_speed'][:],
                    'alpha_bulk_speed': image_data['alpha_bulk_speed'][:],
                    'alpha_density': image_data['alpha_density'][:],
                    'alpha_thermal': image_data['alpha_thermal'][:],
                    'proton_density': image_data['proton_density'][:],
                    'proton_thermal': image_data['proton_thermal'][:],
                    'proton_xvelocity': image_data['proton_xvelocity'][:],
                    'proton_yvelocity': image_data['proton_yvelocity'][:],
                    'proton_zvelocity': image_data['proton_zvelocity'][:],
                    'spacecraft_xpos': image_data['spacecraft_xpos'][:],
                    'spacecraft_ypos': image_data['spacecraft_ypos'][:],
                    'spacecraft_zpos': image_data['spacecraft_zpos'][:]
                })

            elif 'L1_TH2' in file_path:
                df = pd.DataFrame({
                    'epoch': image_data['epoch_for_cdf'][:, 0],
                    'obs_time': image_data['obs_time'][:, 0],
                    'fpga_ticks': image_data['fpga_ticks'][:],
                    'frame_num': image_data['frame_num'][:],
                    'tha2_spec': image_data['THA-2_spec'][:]
                })
                df['time'] = pd.to_datetime(df['epoch'])

            elif 'L2_TH1' in file_path:
                df = pd.DataFrame({
                    'time': pd.to_datetime(image_data['epoch_for_cdf_mod'][:]),
                    'spacecraft_xpos': image_data['spacecraft_xpos'][:],
                    'spacecraft_ypos': image_data['spacecraft_ypos'][:],
                    'spacecraft_zpos': image_data['spacecraft_zpos'][:]
                })
                sun_angle = image_data['sun_angle_tha1'][:]  # shape: [N, 16, 3]
                for sector in range(sun_angle.shape[1]):
                    for comp in range(3):
                        df[f'sun_angle_s{sector}_c{comp}'] = sun_angle[:, sector, comp]

            # Handle missing L2_TH2 for now (commented out in original)
            elif 'L2_TH2' in file_path:
                df = pd.DataFrame({
                    'time': pd.to_datetime(image_data['epoch_for_cdf_mod'][:]),
                    'spacecraft_xpos': image_data['spacecraft_xpos'][:],
                    'spacecraft_ypos': image_data['spacecraft_ypos'][:],
                    'spacecraft_zpos': image_data['spacecraft_zpos'][:],
                    'integrated_flux_mod': image_data['integrated_flux_mod'][:]
                })
                sun_angle = image_data['sun_angle_tha2'][:]  # shape: [N, 32, 3]
                for sector in range(sun_angle.shape[1]):
                    for comp in range(3):
                        df[f'sun_angle_s{sector}_c{comp}'] = sun_angle[:, sector, comp]

            else:
                print(f"Unsupported file type: {file_path}")
                continue

            if df.empty:
                print(f"No data extracted from {file_path}")
                continue

            # Ensure 'time' is the index for alignment
            df = df.set_index('time')
            dfs.append(df)

        if not dfs:
            print("No valid data frames created from the provided files.")
            return None

        # Combine all DataFrames, aligning on 'time' index
        combined_df = pd.concat(dfs, axis=1, join='outer').sort_index()

        # Handle missing values due to different row sizes
        if combined_df.isnull().any().any():
            print("Warning: Missing values detected due to row size differences. Attempting to fill...")
            combined_df = combined_df.interpolate(method='time').ffill().bfill()
            if combined_df.isnull().any().any():
                print("Warning: Some missing values could not be filled. Dropping rows with NaN...")
                combined_df = combined_df.dropna()

        # Select relevant features for training
        relevant_features = [
            'proton_bulk_speed', 'proton_density', 'alpha_density', 'alpha_thermal',
            'proton_thermal', 'proton_xvelocity', 'proton_yvelocity', 'proton_zvelocity',
            'spacecraft_xpos', 'spacecraft_ypos', 'spacecraft_zpos', 'trig_counts',
            'coin_trig_counts', 'coinc_trig_count_total', 'peak_det_counts', 'rej_counts'
        ]
        combined_df = combined_df[relevant_features]

        # Derive additional features
        if 'alpha_density' in combined_df.columns and 'proton_density' in combined_df.columns:
            combined_df['alpha_to_proton_ratio'] = combined_df['alpha_density'] / combined_df['proton_density']

        # Scale the features
        scaled_features = scaler.fit_transform(combined_df)
        combined_df = pd.DataFrame(scaled_features, index=combined_df.index, columns=combined_df.columns)

        return combined_df

    except Exception as e:
        print(f"Error in prepare_data: {e}")
        return None


def safe_get(data, key, *slices):
    try:
        val = data[key][:]
        if slices:
            # Only apply slicing if dimensions allow it
            for s in slices:
                if isinstance(val, np.ndarray) and val.ndim > 0:
                    val = val[s]
                else:
                    break
        return val
    except Exception as e:
        print(f"safe_get: Failed to access {key} with slices {slices}: {e}")
        return np.nan



# for L1
def L1_prepare_data(image_path):
    sample = pd.DataFrame()
    for image in image_path:
        image_data = pycdf.CDF(image)
        if 'L1_AUX' in image:
            df = pd.DataFrame({
                'epoch_for_cdf': image_data['epoch_for_cdf'][:, 0],
                'trig_counts': image_data['trig_counts'][:, 0, 0, 0],
                'coin_trig_counts': image_data['coin_trig_counts'][:, 0, 0],
                'coinc_trig_count_total': image_data['coinc_trig_count_total'][:, 0],
                'angle_tha1': image_data['angle_tha1'][:, 0, 0],
                'angle_tha2': image_data['angle_tha2'][:, 0, 0],
                'angle_xgse': image_data['angle_xgse'][:],
                'angle_ygse': image_data['angle_ygse'][:],
                'angle_zgse': image_data['angle_zgse'][:],
                'peak_det_counts': image_data['peak_det_counts'][:, 0, 0],
                'rej_counts': image_data['rej_counts'][:, 0, 0],
                'obs_time': image_data['obs_time'][:, 0],
                'spacecraft_xpos': image_data['spacecraft_xpos'][:],
                'spacecraft_xvel': image_data['spacecraft_xvel'][:],
                'spacecraft_ypos': image_data['spacecraft_ypos'][:],
                'spacecraft_yvel': image_data['spacecraft_yvel'][:],
                'spacecraft_zpos': image_data['spacecraft_zpos'][:],
                'spacecraft_zvel': image_data['spacecraft_zvel'][:]
            })
            sample = pd.concat([sample,df], ignore_index=True)

        elif 'L1_TH1' in image:
            df = pd.DataFrame({
                'epoch_for_cdf': image_data['epoch_for_cdf'][:, 0],
                'obs_time': image_data['obs_time'][:, 0],
                'THA-1_spec': image_data['THA-1_spec'],
                'fpga_ticks': image_data['fpga_ticks'],
                'frame_num': image_data['frame_num']
            })
            sample = pd.concat([sample,df], ignore_index=True)

        elif 'L1_TH2' in image:
            df = pd.DataFrame({
                'epoch': image_data['epoch_for_cdf'][:, 0],
                'obs_time': image_data['obs_time'][:, 0],
                'fpga_ticks': image_data['fpga_ticks'][:],
                'frame_num': image_data['frame_num'][:],
                'tha2_spec': image_data['THA-2_spec'][:].flatten(),
            })
            sample = pd.concat([sample,df], ignore_index=True)
    return sample


# for L2

def L2_prepare_data(image):
    image_data = pycdf.CDF(image)

    if 'L2_BLK' in image:
            data_dict = {
                'time': safe_get(image_data, 'epoch_for_cdf_mod'),
                'proton_bulk_speed': safe_get(image_data, 'proton_bulk_speed'),
                'alpha_bulk_speed': safe_get(image_data, 'alpha_bulk_speed'),
                'alpha_density': safe_get(image_data, 'alpha_density'),
                'alpha_thermal': safe_get(image_data, 'alpha_thermal'),
                'proton_density': safe_get(image_data, 'proton_density'),
                'proton_thermal': safe_get(image_data, 'proton_thermal'),
                'proton_xvelocity': safe_get(image_data, 'proton_xvelocity'),
                'proton_yvelocity': safe_get(image_data, 'proton_yvelocity'),
                'proton_zvelocity': safe_get(image_data, 'proton_zvelocity'),
                'spacecraft_xpos': safe_get(image_data, 'spacecraft_xpos'),
                'spacecraft_ypos': safe_get(image_data, 'spacecraft_ypos'),
                'spacecraft_zpos': safe_get(image_data, 'spacecraft_zpos')
            }

            max_len = max([len(v) if isinstance(v, (list, np.ndarray)) else 1 for v in data_dict.values()])
            for k, v in data_dict.items():
                if not isinstance(v, (list, np.ndarray)):
                    data_dict[k] = [v] * max_len
                elif len(v) < max_len:
                    data_dict[k] = np.append(v, [np.nan] * (max_len - len(v)))

            df = pd.DataFrame(data_dict)
            sample = pd.concat([sample, df], ignore_index=True)

    elif 'L2_TH1' in image or 'L2_TH2' in image:
            is_th1 = 'L2_TH1' in image
            data_dict = {
                'spacecraft_xpos': safe_get(image_data, 'spacecraft_xpos'),
                'spacecraft_ypos': safe_get(image_data, 'spacecraft_ypos'),
                'spacecraft_zpos': safe_get(image_data, 'spacecraft_zpos')
            }

            # Attempt to access energy bins and flux data
            try:
                energy_bins = safe_get(image_data, 'energy_center_mod')
                n_bins = energy_bins.shape[1] if isinstance(energy_bins, np.ndarray) and energy_bins.ndim == 2 else 0

                for i in range(n_bins):
                    data_dict[f'flux_mod_E{i}'] = safe_get(image_data, 'integrated_flux_mod', slice(None), i)
                    if is_th1:
                        data_dict[f'flux_s9_E{i}'] = safe_get(image_data, 'integrated_flux_s9_mod', slice(None), i)
                        data_dict[f'flux_s10_E{i}'] = safe_get(image_data, 'integrated_flux_s10_mod', slice(None), i)
                        data_dict[f'flux_s11_E{i}'] = safe_get(image_data, 'integrated_flux_s11_mod', slice(None), i)
                    else:
                        data_dict[f'flux_s15_E{i}'] = safe_get(image_data, 'integrated_flux_s15_mod', slice(None), i)
                        data_dict[f'flux_s16_E{i}'] = safe_get(image_data, 'integrated_flux_s16_mod', slice(None), i)
                        data_dict[f'flux_s17_E{i}'] = safe_get(image_data, 'integrated_flux_s17_mod', slice(None), i)
                        data_dict[f'flux_s18_E{i}'] = safe_get(image_data, 'integrated_flux_s18_mod', slice(None), i)
                        data_dict[f'flux_s19_E{i}'] = safe_get(image_data, 'integrated_flux_s19_mod', slice(None), i)
            except Exception:
                pass  # Skip if energy bins are missing or malformed

            # Flatten sun_angle
            sun_key = 'sun_angle_tha1' if is_th1 else 'sun_angle_tha2'
            try:
                sun_angle = safe_get(image_data, sun_key)
                if isinstance(sun_angle, np.ndarray) and sun_angle.ndim == 3:
                    for sector in range(sun_angle.shape[1]):
                        for comp in range(sun_angle.shape[2]):
                            data_dict[f'sun_angle_s{sector}_c{comp}'] = sun_angle[:, sector, comp]
            except Exception:
                pass

            # Normalize lengths
            max_len = max([len(v) if isinstance(v, (list, np.ndarray)) else 1 for v in data_dict.values()])
            for k, v in data_dict.items():
                if not isinstance(v, (list, np.ndarray)):
                    data_dict[k] = [v] * max_len
                elif len(v) < max_len:
                    data_dict[k] = np.append(v, [np.nan] * (max_len - len(v)))

            df = pd.DataFrame(data_dict)
            sample = pd.concat([sample, df], ignore_index=True)

    return sample

def detect_cme_event_graph(df):
    """
    Basic CME event detector from solar wind plasma data.
    Input:
        df: pandas DataFrame with L2_BLK data fields.
    Output:
        Plots highlighting potential CME passage.
    """
    time = pd.to_datetime(df['time'], unit='ms')  # Convert epoch to datetime

    # Plot key plasma parameters
    fig, axs = plt.subplots(4, 1, figsize=(20, 10), sharex=True)

    axs[0].plot(time, df['proton_bulk_speed'], label='Proton Bulk Speed (km/s)', color='orange')
    axs[0].set_ylabel('Speed (km/s)')
    axs[0].legend()

    axs[1].plot(time, df['proton_density'], label='Proton Density (cm⁻³)', color='green')
    axs[1].set_ylabel('Density')
    axs[1].legend()

    axs[2].plot(time, df['proton_thermal'], label='Proton Thermal Velocity (km/s)', color='red')
    axs[2].set_ylabel('Thermal')
    axs[2].legend()

    # Alpha-to-proton density ratio
    alpha_ratio = df['alpha_density'] / (df['proton_density'] + 1e-5)
    axs[3].plot(time, alpha_ratio, label='Alpha-to-Proton Ratio', color='blue')
    axs[3].set_ylabel('α/p Ratio')
    axs[3].axhline(0.08, linestyle='--', color='gray', label='CME Threshold')
    axs[3].legend()

    plt.xlabel('Time')
    plt.suptitle('CME Detection via Solar Wind Plasma Signatures')
    plt.tight_layout()
    plt.show()

def calculate_alpha_to_proton_ratio(df):
    """
    Calculates the alpha-to-proton density ratio and adds it as a column to the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame with 'alpha_density' and 'proton_density' columns.
    
    Raises:
        ValueError: If required columns are missing.
    """
    if 'alpha_density' in df.columns and 'proton_density' in df.columns:
        df['alpha_to_proton_ratio'] = df['alpha_density'] / df['proton_density']
    else:
        raise ValueError("Required columns 'alpha_density' and 'proton_density' not found in DataFrame")
    
def calculate_spacecraft_distance(df):
    """
    Calculates the spacecraft distance from Earth (assuming Earth at origin) and adds it as a column.
    
    Args:
        df (pd.DataFrame): DataFrame with 'spacecraft_xpos', 'spacecraft_ypos', 'spacecraft_zpos' columns.
    
    Raises:
        ValueError: If required position columns are missing.
    """
    required_cols = ['spacecraft_xpos', 'spacecraft_ypos', 'spacecraft_zpos']
    if all(col in df.columns for col in required_cols):
        df['distance'] = np.sqrt(df['spacecraft_xpos']**2 + df['spacecraft_ypos']**2 + df['spacecraft_zpos']**2)
    else:
        raise ValueError("Required position columns not found in DataFrame")

def calculate_dynamic_pressure(df):
    """
    Calculates the dynamic pressure (in nPa) and adds it as a column.
    
    Args:
        df (pd.DataFrame): DataFrame with 'proton_density' and 'proton_bulk_speed' columns.
    
    Raises:
        ValueError: If required columns are missing.
    """
    if 'proton_density' in df.columns and 'proton_bulk_speed' in df.columns:
        df['P_dyn'] = 1.67e-6 * df['proton_density'] * df['proton_bulk_speed']**2
    else:
        raise ValueError("Required columns 'proton_density' and 'proton_bulk_speed' not found in DataFrame")

def detect_events(df, detect_var, threshold, min_duration, comparison='above'):
    """
    Detects events where a specified variable crosses a threshold for a minimum duration.
    
    Args:
        df (pd.DataFrame): DataFrame with 'time' and the detection variable column.
        detect_var (str): Name of the column to monitor (e.g., 'alpha_to_proton_ratio').
        threshold (float): Threshold value for detection.
        min_duration (float): Minimum duration in seconds for an event to be valid.
        comparison (str): 'above' or 'below' to specify threshold crossing type.
    
    Returns:
        pd.DataFrame: DataFrame with event details (start_time, end_time, duration, etc.).
    
    Raises:
        ValueError: If comparison type is invalid or required columns are missing.
    """
    if detect_var not in df.columns or 'time' not in df.columns:
        raise ValueError(f"DataFrame must contain 'time' and '{detect_var}' columns")
    
    if comparison == 'above':
        condition = df[detect_var] > threshold
    elif comparison == 'below':
        condition = df[detect_var] < threshold
    else:
        raise ValueError("Invalid comparison type; use 'above' or 'below'")
    
    df['condition'] = condition
    df['event_id'] = (df['condition'] != df['condition'].shift()).cumsum()
    
    events = df[df['condition']].groupby('event_id').agg(
        start_time=('time', 'min'),
        end_time=('time', 'max'),
        duration=('time', lambda x: (x.max() - x.min()).total_seconds()),
        average_speed=('proton_bulk_speed', 'mean'),
        first_speed=('proton_bulk_speed', 'first'),
        first_distance=('distance', 'first'),
        max_P_dyn=('P_dyn', 'max')
    ).reset_index()
    
    return events[events['duration'] >= min_duration]