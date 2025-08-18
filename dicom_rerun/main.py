import os
import logging
from pathlib import Path
import pydicom
import rerun as rr
import rerun.blueprint as rrb
import numpy as np
from skimage import measure


def create_blueprint():
    """
    Create a Rerun blueprint with 3D meshes at the bottom and main image view at the top.
    """
    # Create a vertical layout with main images at top and 3D meshes at bottom
    blueprint = rrb.Blueprint(
        rrb.Vertical(
            # Top section: Main image viewer (takes up more space)
            rrb.Spatial2DView(
                name="DICOM Images",
                origin="series",
                contents=["+ $origin/**"]
            ),
            # Bottom section: 3D mesh viewer in horizontal layout
            rrb.Horizontal(
                rrb.Spatial3DView(
                    name="3D Meshes",
                    origin="mesh",
                    contents=["+ $origin/**"]
                ),
                rrb.TensorView(
                    name="Tensor Volumes",
                    origin="tensor",
                    contents=["+ $origin/**"]
                )
            ),
            # Metadata view
            rrb.TextDocumentView(
                name="Metadata",
                origin="series",
                contents=["+ $origin/**"]
            )
        )
    )
    
    return blueprint


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


def validate_folder_path(folder_path):
    """
    Validate that the provided folder path exists and is a directory.
    
    Args:
        folder_path (Path): Path object to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    logger = setup_logging()
    
    if not folder_path.exists():
        logger.error(f"Folder does not exist: {folder_path}")
        return False
    
    if not folder_path.is_dir():
        logger.error(f"Path is not a directory: {folder_path}")
        return False
    
    return True


def extract_dicom_metadata(dicom_data):
    """
    Extract relevant metadata from a DICOM dataset.
    
    Args:
        dicom_data: PyDICOM dataset object
        
    Returns:
        dict: Dictionary containing extracted metadata
    """
    return {
        'series_uid': getattr(dicom_data, 'SeriesInstanceUID', 'UNKNOWN_SERIES'),
        'series_description': getattr(dicom_data, 'SeriesDescription', 'N/A'),
        'modality': getattr(dicom_data, 'Modality', 'N/A'),
        'patient_id': getattr(dicom_data, 'PatientID', 'N/A'),
        'instance_number': getattr(dicom_data, 'InstanceNumber', 0)
    }


def process_single_dicom_file(file_path):
    """
    Process a single DICOM file and extract its data and metadata.
    
    Args:
        file_path (Path): Path to the DICOM file
        
    Returns:
        dict or None: DICOM file information dictionary or None if processing failed
    """
    logger = setup_logging()
    
    try:
        dicom_data = pydicom.dcmread(str(file_path), force=True)
        metadata = extract_dicom_metadata(dicom_data)
        
        logger.info(f"Processing instance: {metadata['instance_number']}")
        
        if hasattr(dicom_data, 'pixel_array'):
            return {
                'file_path': file_path,
                'dicom_data': dicom_data,
                'pixel_array': dicom_data.pixel_array,
                **metadata
            }
        else:
            logger.warning(f"No pixel data found in file: {file_path}")
            return None
            
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        return None


def scan_dicom_files(folder_path):
    """
    Scan a folder recursively for DICOM files and process them.
    
    Args:
        folder_path (Path): Path to the folder containing DICOM files
        
    Returns:
        tuple: (dicom_files list, total_files count, valid_files count, invalid_files count)
    """
    logger = setup_logging()
    logger.info(f"Starting to scan DICOM files from: {folder_path}")
    
    total_files = 0
    valid_dicom_files = 0
    invalid_files = 0
    dicom_files = []
    
    for file_path in folder_path.rglob('*'):
        if file_path.is_file():
            total_files += 1
            
            file_info = process_single_dicom_file(file_path)
            if file_info:
                dicom_files.append(file_info)
                valid_dicom_files += 1
            else:
                invalid_files += 1
    
    return dicom_files, total_files, valid_dicom_files, invalid_files


def sort_dicom_files(dicom_files):
    """
    Sort DICOM files by series UID and instance number.
    
    Args:
        dicom_files (list): List of DICOM file dictionaries
        
    Returns:
        list: Sorted list of DICOM files
    """
    logger = setup_logging()
    logger.info("Sorting DICOM files by series UID, then by instance number")
    
    dicom_files.sort(key=lambda x: (x['series_uid'], x['instance_number']))
    return dicom_files


def log_loading_summary(total_files, valid_files, invalid_files):
    """
    Log summary statistics about the DICOM loading process.
    
    Args:
        total_files (int): Total number of files processed
        valid_files (int): Number of valid DICOM files
        invalid_files (int): Number of invalid files
    """
    logger = setup_logging()
    logger.info("Loading complete!")
    logger.info(f"Total files: {total_files}")
    logger.info(f"Valid DICOM files: {valid_files}")
    logger.info(f"Invalid files: {invalid_files}")


def load_and_sort_dicom_files(folder_path):
    """
    Load and sort DICOM files from a folder.
    
    Args:
        folder_path (str): Path to the folder containing DICOM files
        
    Returns:
        list: Sorted list of DICOM file metadata dictionaries
    """
    folder_path = Path(folder_path)
    
    if not validate_folder_path(folder_path):
        return []
    
    dicom_files, total_files, valid_files, invalid_files = scan_dicom_files(folder_path)
    dicom_files = sort_dicom_files(dicom_files)
    log_loading_summary(total_files, valid_files, invalid_files)
    
    return dicom_files


def create_image_metadata_text(file_info):
    """
    Create metadata text for a DICOM image.
    
    Args:
        file_info (dict): DICOM file information dictionary
        
    Returns:
        str: Formatted metadata text
    """
    pixel_array = file_info['pixel_array']
    
    return f"""
Series Description: {file_info['series_description']}
Modality: {file_info['modality']}
Patient ID: {file_info['patient_id']}
Instance Number: {file_info['instance_number']}
Image Shape: {pixel_array.shape}
Image Data Type: {pixel_array.dtype}
Min Value: {np.min(pixel_array)}
Max Value: {np.max(pixel_array)}
Mean Value: {np.mean(pixel_array):.2f}
File Path: {file_info['file_path']}
    """.strip()


def log_single_dicom_image(file_info):
    """
    Log a single DICOM image and its metadata to Rerun.
    
    Args:
        file_info (dict): DICOM file information dictionary
    """
    logger = setup_logging()
    
    series_uid = file_info['series_uid']
    entity_path = f"series/{series_uid}"
    
    # Log the image
    rr.log(entity_path, rr.Image(file_info['pixel_array']))
    
    # Log the metadata
    metadata_text = create_image_metadata_text(file_info)
    rr.log(f"{entity_path}/metadata", rr.TextDocument(metadata_text))
    
    # Log progress
    logger.info(f"Logged DICOM: {file_info['instance_number']}")
    logger.info(f"  Series: {series_uid}")


def log_individual_series(dicom_files):
    """
    Log individual DICOM images to Rerun by series.
    
    Args:
        dicom_files (list): Sorted list of DICOM file metadata
    """
    logger = setup_logging()
    logger.info("Logging individual series to Rerun")
    
    for file_info in dicom_files:
        log_single_dicom_image(file_info)


def normalize_volume(volume_3d):
    """
    Normalize 3D volume data to range [0, 1].
    
    Args:
        volume_3d (np.ndarray): 3D volume data
        
    Returns:
        np.ndarray: Normalized volume data
    """
    min_val = np.min(volume_3d)
    max_val = np.max(volume_3d)
    
    if max_val == min_val:
        return np.zeros_like(volume_3d)
    
    return (volume_3d - min_val) / (max_val - min_val)


def get_mesh_configuration():
    """
    Get mesh thresholds and colors configuration.
    
    Returns:
        tuple: (thresholds list, colors list)
    """
    thresholds = [0.3, 0.5, 0.7]  # Different tissue density levels
    colors = [
        [0.8, 0.2, 0.2, 0.7],  # Red - Soft tissue
        [0.2, 0.8, 0.2, 0.8],  # Green - Medium density
        [0.9, 0.9, 0.9, 0.9]   # White - Bone/high density
    ]
    return thresholds, colors


def get_tissue_type_name(threshold_index):
    """
    Get tissue type name based on threshold index.
    
    Args:
        threshold_index (int): Index of the threshold
        
    Returns:
        str: Tissue type name
    """
    tissue_types = ['Soft Tissue', 'Medium Density', 'Bone/High Density']
    return tissue_types[threshold_index] if threshold_index < len(tissue_types) else 'Unknown'


def create_mesh_metadata_text(threshold, vertices_count, faces_count, tissue_type, metadata_info):
    """
    Create metadata text for a mesh.
    
    Args:
        threshold (float): Mesh threshold level
        vertices_count (int): Number of vertices
        faces_count (int): Number of faces
        tissue_type (str): Type of tissue represented
        metadata_info (dict): DICOM metadata
        
    Returns:
        str: Formatted metadata text
    """
    return f"""
Mesh Level: {threshold:.1f}
Vertices: {vertices_count}
Faces: {faces_count}
Color: {tissue_type}
Series: {metadata_info['series_description']}
Modality: {metadata_info['modality']}
    """.strip()


def extract_mesh_with_marching_cubes(volume_normalized, threshold):
    """
    Extract mesh from normalized volume using marching cubes algorithm.
    
    Args:
        volume_normalized (np.ndarray): Normalized 3D volume data
        threshold (float): Threshold level for mesh extraction
        
    Returns:
        tuple: (vertices, faces, normals, values) or None if extraction fails
    """
    try:
        return measure.marching_cubes(
            volume_normalized, 
            level=threshold,
            spacing=(1.0, 1.0, 1.0)
        )
    except Exception as e:
        logger = setup_logging()
        logger.error(f"Error in marching cubes at threshold {threshold:.1f}: {str(e)}")
        return None


def log_mesh_to_rerun(mesh_path, vertices, faces, normals, color, threshold, metadata_info):
    """
    Log a mesh and its metadata to Rerun.
    
    Args:
        mesh_path (str): Rerun entity path for the mesh
        vertices (np.ndarray): Mesh vertices
        faces (np.ndarray): Mesh faces
        normals (np.ndarray): Mesh normals
        color (list): Mesh color
        threshold (float): Threshold level
        metadata_info (dict): DICOM metadata
    """
    logger = setup_logging()
    
    # Log the mesh
    rr.log(
        mesh_path,
        rr.Mesh3D(
            vertex_positions=vertices,
            triangle_indices=faces,
            vertex_normals=normals,
            vertex_colors=color
        )
    )
    
    # Create and log metadata
    tissue_type = get_tissue_type_name(0 if threshold == 0.3 else 1 if threshold == 0.5 else 2)
    mesh_metadata = create_mesh_metadata_text(
        threshold, len(vertices), len(faces), tissue_type, metadata_info
    )
    rr.log(f"{mesh_path}/info", rr.TextDocument(mesh_metadata))
    
    logger.info(f"Created mesh at threshold {threshold:.1f}: {len(vertices)} vertices, {len(faces)} faces")


def create_mesh_from_volume(volume_3d, entity_path, metadata_info):
    """
    Create 3D mesh from volume data using marching cubes algorithm.
    
    Args:
        volume_3d (np.ndarray): 3D volume data
        entity_path (str): Rerun entity path for the mesh
        metadata_info (dict): DICOM metadata for the series
    """
    logger = setup_logging()
    
    try:
        volume_normalized = normalize_volume(volume_3d)
        thresholds, colors = get_mesh_configuration()
        
        for i, threshold in enumerate(thresholds):
            mesh_data = extract_mesh_with_marching_cubes(volume_normalized, threshold)
            
            if mesh_data is None:
                continue
                
            verts, faces, normals, values = mesh_data
            
            if len(verts) > 0 and len(faces) > 0:
                mesh_path = f"{entity_path}/threshold_{threshold:.1f}"
                log_mesh_to_rerun(mesh_path, verts, faces, normals, colors[i], threshold, metadata_info)
            else:
                logger.warning(f"No mesh generated at threshold {threshold:.1f}")
                
    except Exception as e:
        logger.error(f"Error in mesh creation: {str(e)}")


def group_files_by_series(dicom_files):
    """
    Group DICOM files by their series UID.
    
    Args:
        dicom_files (list): List of DICOM file dictionaries
        
    Returns:
        dict: Dictionary with series UID as keys and file lists as values
    """
    series_groups = {}
    for file_info in dicom_files:
        series_uid = file_info['series_uid']
        if series_uid not in series_groups:
            series_groups[series_uid] = []
        series_groups[series_uid].append(file_info)
    
    return series_groups


def validate_series_for_3d_volume(series_files, series_uid):
    """
    Validate if a series has enough images for 3D volume creation.
    
    Args:
        series_files (list): List of files in the series
        series_uid (str): Series UID
        
    Returns:
        bool: True if valid for 3D volume creation
    """
    logger = setup_logging()
    
    if len(series_files) < 2:
        logger.warning(f"Series {series_uid} has only {len(series_files)} images, skipping 3D volume creation")
        return False
    
    return True


def stack_pixel_arrays(series_files):
    """
    Stack pixel arrays from series files to create a 3D volume.
    
    Args:
        series_files (list): List of DICOM file dictionaries
        
    Returns:
        np.ndarray: 3D volume array
    """
    pixel_arrays = [file_info['pixel_array'] for file_info in series_files]
    return np.stack(pixel_arrays, axis=0)


def log_volume_to_rerun(volume_3d, series_uid, series_files):
    """
    Log a 3D volume, its mesh, and metadata to Rerun.
    
    Args:
        volume_3d (np.ndarray): 3D volume data
        series_uid (str): Series UID
        series_files (list): List of DICOM files in the series
    """
    logger = setup_logging()
    
    # Log 3D tensor volume
    tensor_entity_path = f"tensor/{series_uid}"
    rr.log(tensor_entity_path, rr.Tensor(volume_3d))
    
    # Create 3D mesh
    mesh_entity_path = f"mesh/{series_uid}"
    create_mesh_from_volume(volume_3d, mesh_entity_path, series_files[0])
    
    logger.info(f"Created 3D volume for series {series_uid}")
    logger.info(f"  Volume shape: {volume_3d.shape}")
    logger.info(f"  Number of slices: {len(series_files)}")


def process_single_series_for_3d_volume(series_uid, series_files):
    """
    Process a single series to create a 3D volume.
    
    Args:
        series_uid (str): Series UID
        series_files (list): List of DICOM files in the series
    """
    logger = setup_logging()
    
    if not validate_series_for_3d_volume(series_files, series_uid):
        return
    
    logger.info(f"Creating 3D volume for series {series_uid} with {len(series_files)} slices")
    
    try:
        volume_3d = stack_pixel_arrays(series_files)
        log_volume_to_rerun(volume_3d, series_uid, series_files)
        
    except Exception as e:
        logger.error(f"Error creating 3D volume for series {series_uid}: {str(e)}")


def create_3d_volumes(dicom_files):
    """
    Create 3D volumes by stacking sorted DICOM instances and log to Rerun.
    
    Args:
        dicom_files (list): Sorted list of DICOM file metadata
    """
    logger = setup_logging()
    logger.info("Creating 3D volumes from sorted DICOM instances")
    
    series_groups = group_files_by_series(dicom_files)
    
    for series_uid, series_files in series_groups.items():
        process_single_series_for_3d_volume(series_uid, series_files)



def initialize_rerun_with_blueprint():
    """
    Initialize Rerun viewer with a custom blueprint.
    """
    blueprint = create_blueprint()
    rr.init("dicom_viewer_1.0.3", spawn=True, default_blueprint=blueprint)



def process_dicom_folder(folder_path):
    """
    Main processing function that loads DICOM files and creates both individual series and 3D volumes.
    
    Args:
        folder_path (str): Path to the folder containing DICOM files
    """
    logger = setup_logging()
    
    initialize_rerun_with_blueprint()
    dicom_files = load_and_sort_dicom_files(folder_path)
    
    if not dicom_files:
        logger.error("No valid DICOM files found")
        return
    
    # Log individual series
    log_individual_series(dicom_files)
    
    # Create 3D volumes
    create_3d_volumes(dicom_files)


def main():
    logger = setup_logging()
    
    dicom_folder = input("Enter the path to the DICOM folder: ").strip()
    
    if not dicom_folder:
        logger.error("No folder path provided")
        return
    
    logger.info(f"Starting DICOM analysis with Rerun for folder: {dicom_folder}")
    
    process_dicom_folder(dicom_folder)
    
    logger.info("DICOM analysis complete. Rerun viewer should be open with visualizations.")
    
    rr.save("session.rrd")

    input("Press Enter to exit...")


if __name__ == "__main__":
    main()