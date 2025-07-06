import os
import shutil
import pandas as pd
import sunpy.map
from astropy.io import fits
import matplotlib.pyplot as plt
# Create DataFrame with file paths and labels


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
        folder_name = image[40:-27]
        dest_folder = os.path.join(DEST_DIR, folder_name)
        make_folder(dest_folder)
        dest_path = os.path.join(dest_folder, os.path.basename(image))
        file_transfer(image, dest_path)

# open fits image
def open_fits_images(image_path):
    with fits.open(image_path) as hdul:
        hdr = hdul[0].header
        # Patch the unit string if present
        for key in hdr:
            if isinstance(hdr[key], str) and 'milli-angstrom' in hdr[key]:
                hdr[key] = hdr[key].replace('milli-angstrom', 'angstrom')
        # Force CUNIT1 to 'arcsec' to satisfy SunPy Map requirements
        hdr['CUNIT1'] = 'arcsec'
        # Create the SunPy map from the patched HDU
        return sunpy.map.Map(hdul[0].data, hdr)

def meta_data_of_image(image_path):
    return open_fits_images(image_path).meta

def date_from_fit_image(image_path):
    return open_fits_images(image_path).date.datetime.date()

def time_from_fit_image(image_path):
    return open_fits_images(image_path).date.datetime.time()

def wavelength_from_image(image_path):
    # Get the wavelength as a string (e.g., '2796.0 Angstrom')
    wavelength = open_fits_images(image_path).wavelength
    # Convert to float first, then int
    return float(str(wavelength).split()[0])

def return_image(image_path):
    image = open_fits_images(image_path)
    image.plot(cmap='inferno')
    plt.colorbar(label='Intensity')
    plt.title(f"{wavelength_from_image(image_path)} - {image.date}")
    plt.show()

def return_graph(image_path):
    image = open_fits_images(image_path)
    plt.figure(figsize=(10, 5))
    plt.hist(image.data.ravel(), bins=500, color='orange', log=True)
    plt.title("Pixel Intensity Distribution")
    plt.xlabel("Pixel Value")
    plt.ylabel("Log Count")
    plt.grid(True)
    plt.show()

def exposure_duration(image_path):
    return str(open_fits_images(image_path).exposure_time)

