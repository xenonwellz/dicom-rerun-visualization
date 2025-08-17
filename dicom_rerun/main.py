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


def load_and_sort_dicom_files(folder_path):
    """
    Load and sort DICOM files from a folder.
    
    Args:
        folder_path (str): Path to the folder containing DICOM files
        
    Returns:
        list: Sorted list of DICOM file metadata dictionaries
    """
    logger = setup_logging()
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        logger.error(f"Folder does not exist: {folder_path}")
        return []
    
    if not folder_path.is_dir():
        logger.error(f"Path is not a directory: {folder_path}")
        return []
    
    logger.info(f"Starting to load DICOM files from: {folder_path}")
    
    total_files = 0
    valid_dicom_files = 0
    invalid_files = 0
    dicom_files = []
    
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
                logger.info(f"Processing instance: {instance_number}")
                
                if hasattr(dicom_data, 'pixel_array'):
                    dicom_files.append({
                        'file_path': file_path,
                        'dicom_data': dicom_data,
                        'series_uid': series_uid,
                        'series_description': series_description,
                        'modality': modality,
                        'patient_id': patient_id,
                        'instance_number': instance_number,
                        'pixel_array': dicom_data.pixel_array
                    })
                else:
                    logger.warning(f"No pixel data found in file: {file_path}")
                    
            except Exception as e:
                invalid_files += 1
                logger.error(f"Error processing file {file_path}: {str(e)}")
    
    logger.info(f"Sorting DICOM files by series UID, then by instance number")
    dicom_files.sort(key=lambda x: (x['series_uid'], x['instance_number']))
    
    logger.info(f"Loading complete!")
    logger.info(f"Total files: {total_files}")
    logger.info(f"Valid DICOM files: {valid_dicom_files}")
    logger.info(f"Invalid files: {invalid_files}")
    
    return dicom_files


def log_individual_series(dicom_files):
    """
    Log individual DICOM images to Rerun by series.
    
    Args:
        dicom_files (list): Sorted list of DICOM file metadata
    """
    logger = setup_logging()
    logger.info(f"Logging individual series to Rerun")
    
    for file_info in dicom_files:
        file_path = file_info['file_path']
        pixel_array = file_info['pixel_array']
        series_uid = file_info['series_uid']
        series_description = file_info['series_description']
        modality = file_info['modality']
        patient_id = file_info['patient_id']
        instance_number = file_info['instance_number']
        
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
        
        logger.info(f"Logged DICOM: {file_path}")
        logger.info(f"  Series: {series_uid}")
        logger.info(f"  Instance: {instance_number}")


def create_3d_volumes(dicom_files):
    """
    Create 3D volumes by stacking sorted DICOM instances and log to Rerun.
    
    Args:
        dicom_files (list): Sorted list of DICOM file metadata
    """
    logger = setup_logging()
    logger.info(f"Creating 3D volumes from sorted DICOM instances")
    
    # Group files by series
    series_groups = {}
    for file_info in dicom_files:
        series_uid = file_info['series_uid']
        if series_uid not in series_groups:
            series_groups[series_uid] = []
        series_groups[series_uid].append(file_info)
    
    for series_uid, series_files in series_groups.items():
        if len(series_files) < 2:
            logger.warning(f"Series {series_uid} has only {len(series_files)} images, skipping 3D volume creation")
            continue
            
        logger.info(f"Creating 3D volume for series {series_uid} with {len(series_files)} slices")
        
        # Stack pixel arrays to create 3D volume
        pixel_arrays = [file_info['pixel_array'] for file_info in series_files]
        
        try:
            # Stack arrays along a new axis (depth)
            volume_3d = np.stack(pixel_arrays, axis=0)
            
            # Log 3D volume to Rerun
            volume_entity_path = f"volumes/{series_uid}"
            rr.log(volume_entity_path, rr.Tensor(volume_3d))
            
            # Create volume metadata
            first_file = series_files[0]
            volume_metadata = f"""
3D Volume - {first_file['series_description']}
Series UID: {series_uid}
Modality: {first_file['modality']}
Patient ID: {first_file['patient_id']}
Number of slices: {len(series_files)}
Volume Shape: {volume_3d.shape}
Data Type: {volume_3d.dtype}
Min Value: {np.min(volume_3d)}
Max Value: {np.max(volume_3d)}
Mean Value: {np.mean(volume_3d):.2f}
Instance Numbers: {[f['instance_number'] for f in series_files]}
            """.strip()
            
            rr.log(f"{volume_entity_path}/metadata", rr.TextDocument(volume_metadata))
            
            logger.info(f"Created 3D volume for series {series_uid}")
            logger.info(f"  Volume shape: {volume_3d.shape}")
            logger.info(f"  Number of slices: {len(series_files)}")
            
        except Exception as e:
            logger.error(f"Error creating 3D volume for series {series_uid}: {str(e)}")


def process_dicom_folder(folder_path):
    """
    Main processing function that loads DICOM files and creates both individual series and 3D volumes.
    
    Args:
        folder_path (str): Path to the folder containing DICOM files
    """
    logger = setup_logging()
    
    # Initialize Rerun
    rr.init("dicom_viewer", spawn=True)
    
    # Load and sort DICOM files
    dicom_files = load_and_sort_dicom_files(folder_path)
    
    if not dicom_files:
        logger.error("No valid DICOM files found")
        return
    
    # Log individual series
    log_individual_series(dicom_files)
    
    # Create and log 3D volumes
    create_3d_volumes(dicom_files)
    
    # Log summary
    total_files = len(dicom_files)
    series_count = len(set(f['series_uid'] for f in dicom_files))
    
    summary_text = f"""
DICOM Processing Summary
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
Total valid DICOM files: {total_files}
Number of series: {series_count}

Individual images are logged under: series/{{series_uid}}
3D volumes are logged under: volumes/{{series_uid}}
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