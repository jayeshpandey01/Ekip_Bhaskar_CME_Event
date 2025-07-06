import spacepy.pycdf as cdf
import numpy as np

# Open one of the L2 BLK files to examine structure
cdf_file = 'cdf_data/20250108/AL1_ASW91_L2_BLK_20250108_UNP_9999_999999_V02.cdf'
with cdf.CDF(cdf_file) as data:
    print('=== CDF BLK Variables ===')
    for var in data.keys():
        shape_info = data[var].shape if hasattr(data[var], 'shape') else 'scalar'
        units = data[var].attrs.get('UNITS', 'no units')
        print(f'{var}: {shape_info} - {units}')
    
    print('\n=== Sample Data ===')
    if 'epoch_for_cdf_mod' in data:
        print(f'Time range: {data["epoch_for_cdf_mod"][0]} to {data["epoch_for_cdf_mod"][-1]}')
        print(f'Data points: {len(data["epoch_for_cdf_mod"])}')
        
    # Check for solar wind parameters
    print('\n=== Solar Wind Parameters ===')
    sw_params = ['bulk_velocity', 'number_density', 'temperature', 'pressure']
    for param in sw_params:
        if param in data:
            print(f'{param}: Available')
        else:
            print(f'{param}: Not found')
