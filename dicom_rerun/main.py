import os
import logging
from pathlib import Path
import pydicom
import rerun as rr
import numpy as np


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('dicom_analysis.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def process_dicom_folder(folder_path):
    logger = setup_logging()
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        logger.error(f"Folder does not exist: {folder_path}")
        return
    
    if not folder_path.is_dir():
        logger.error(f"Path is not a directory: {folder_path}")
        return
    
    rr.init("dicom_viewer", spawn=True)
    
    logger.info(f"Starting to process DICOM files from: {folder_path}")
    
    total_files = 0
    valid_dicom_files = 0
    invalid_files = 0
    
    for file_path in folder_path.rglob('*'):
        if file_path.is_file():
            total_files += 1
            
            try:
                dicom_data = pydicom.dcmread(str(file_path), force=True)
                valid_dicom_files += 1
                    
                series_uid = getattr(dicom_data, 'SeriesInstanceUID', 'UNKNOWN_SERIES')
                series_description = getattr(dicom_data, 'SeriesDescription', 'N/A')
                modality = getattr(dicom_data, 'Modality', 'N/A')
                patient_id = getattr(dicom_data, 'PatientID', 'N/A')
                instance_number = getattr(dicom_data, 'InstanceNumber', 0)
                
                if hasattr(dicom_data, 'pixel_array'):
                    pixel_array = dicom_data.pixel_array
                    
                    entity_path = f"series/{series_uid}"
                    rr.log(entity_path, rr.Image(pixel_array))
                    metadata_text = f"""
Series Description: {series_description}
Modality: {modality}
Patient ID: {patient_id}
Instance Number: {instance_number}
Image Shape: {pixel_array.shape}
Image Data Type: {pixel_array.dtype}
Min Value: {np.min(pixel_array)}
Max Value: {np.max(pixel_array)}
Mean Value: {np.mean(pixel_array):.2f}
File Path: {file_path}
                    """.strip()
                    
                    rr.log(f"{entity_path}/metadata", rr.TextDocument(metadata_text))
                    
                    pixel_stats = {
                        "shape": pixel_array.shape,
                        "dtype": str(pixel_array.dtype),
                        "min": float(np.min(pixel_array)),
                        "max": float(np.max(pixel_array)),
                        "mean": float(np.mean(pixel_array)),
                        "std": float(np.std(pixel_array))
                    }
                    
                    logger.info(f"Processed DICOM: {file_path}")
                    logger.info(f"  Series: {series_uid}")
                    logger.info(f"  Shape: {pixel_array.shape}")
                    logger.info(f"  Data type: {pixel_array.dtype}")
                    logger.info(f"  Value range: [{np.min(pixel_array)}, {np.max(pixel_array)}]")
                    
                else:
                    logger.warning(f"No pixel data found in file: {file_path}")
                    
            except Exception as e:
                invalid_files += 1
                logger.error(f"Error processing file {file_path}: {str(e)}")
    
    logger.info(f"Processing complete!")
    logger.info(f"Total files: {total_files}")
    logger.info(f"Valid DICOM files: {valid_dicom_files}")
    logger.info(f"Invalid files: {invalid_files}")
    
    summary_text = f"""
DICOM Processing Summary
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
Total files processed: {total_files}
Valid DICOM files: {valid_dicom_files}
Invalid files: {invalid_files}
Success rate: {(valid_dicom_files/total_files*100):.1f}% if total_files > 0 else N/A

Check the series hierarchy to view individual DICOM images.
Each series is grouped by its SeriesInstanceUID.
    """.strip()
    
    rr.log("summary", rr.TextDocument(summary_text))


def main():
    try:
        logger = setup_logging()
        
        dicom_folder = input("Enter the path to the DICOM folder: ").strip()
        
        if not dicom_folder:
            logger.error("No folder path provided")
            return
        
        logger.info(f"Starting DICOM analysis with Rerun for folder: {dicom_folder}")
        
        process_dicom_folder(dicom_folder)
        
        logger.info("DICOM analysis complete. Rerun viewer should be open with visualizations.")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return
    
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()