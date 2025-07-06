import spacepy.pycdf as cdf
import numpy as np

# Open one of the L2 files to examine structure
cdf_file = 'cdf_data/20250108/AL1_ASW91_L2_TH1_20250108_UNP_9999_999999_V02.cdf'
with cdf.CDF(cdf_file) as data:
    print('=== CDF Variables ===')
    for var in data.keys():
        shape_info = data[var].shape if hasattr(data[var], 'shape') else 'scalar'
        units = data[var].attrs.get('UNITS', 'no units')
        print(f'{var}: {shape_info} - {units}')
    
    print('\n=== Sample Data ===')
    # Check if we have the expected solar wind parameters
    if 'Epoch' in data:
        print(f'Time range: {data["Epoch"][0]} to {data["Epoch"][-1]}')
        print(f'Data points: {len(data["Epoch"])}')
