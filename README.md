# DICOM Rerun Viewer

A comprehensive Python tool that uses Rerun for interactive 3D visualization of DICOM medical imaging data. Built with pydicom for DICOM processing and Rerun for immersive 3D visualization.

## Features

### 🔍 **DICOM Processing**
- **Recursive DICOM File Reading**: Scans folders and subfolders for DICOM files
- **Metadata Extraction**: Extracts comprehensive DICOM metadata including series information
- **Series Grouping**: Groups images by Series Instance UID with proper sorting
- **Smart Sorting**: Automatically sorts by series UID and instance number

### 📊 **Interactive Visualizations**
- **Individual 2D Images**: Browse DICOM slices grouped by series
- **3D Tensor Volumes**: Interactive volumetric data exploration
- **3D Mesh Surfaces**: Smooth anatomical surfaces using marching cubes algorithm
- **Multi-Threshold Meshes**: Different tissue types at various density levels

### 🎨 **Advanced 3D Features**
- **Color-Coded Meshes**:
  - 🔴 Red: Soft tissue (threshold 0.3)
  - 🟢 Green: Medium density structures (threshold 0.5)
  - ⚪ White: Bone/high density (threshold 0.7)
- **Interactive Navigation**: Rotate, zoom, and explore 3D structures
- **Real-time Rendering**: Powered by Rerun's modern visualization engine

### 📝 **Comprehensive Logging**
- **Detailed Console Output**: Real-time progress and statistics
- **File Logging**: Complete analysis log saved to `dicom_analysis.log`
- **Metadata Display**: Rich information panels for each visualization

## Installation

This project uses Poetry for dependency management. Make sure you have Poetry installed on your system.

### Install Poetry (if not already installed)

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Install Dependencies

```bash
poetry install
```

This will install the dependencies and create a virtual environment.

### Using the Script Command

You can also use the configured script:

```bash
poetry run dicom-rerun
```

The script will:
1. Prompt you to enter the path to your DICOM folder
2. Load and sort all DICOM files
3. Launch the Rerun viewer automatically
4. Display multiple visualization options

## Visualization Hierarchy

The Rerun viewer organizes data in a clear hierarchy:

```
📁 series/
  └── {series_uid}/           # Individual 2D images
📁 volumes/
  ├── tensor/{series_uid}/    # 3D tensor volumes
  └── mesh/{series_uid}/      # 3D mesh surfaces
      ├── threshold_0.3/      # Soft tissue mesh
      ├── threshold_0.5/      # Medium density mesh
      └── threshold_0.7/      # Bone/high density mesh
📄 summary                    # Processing statistics
```

## Example Workflow

1. **Run the script**: `poetry run python dicom_rerun/main.py`
2. **Enter DICOM folder path**: `/path/to/your/dicom/files`
3. **Rerun viewer opens** automatically in your browser
4. **Explore visualizations**:
   - Browse 2D slices in `series/` folder
   - View 3D volumes in `volumes/tensor/` 
   - Interact with 3D meshes in `volumes/mesh/`
   - Toggle different mesh layers for tissue analysis

## Sample Output

```
2024-01-15 10:30:00 - INFO - Starting to load DICOM files from: /path/to/dicom
2024-01-15 10:30:05 - INFO - Sorting DICOM files by series UID, then by instance number
2024-01-15 10:30:06 - INFO - Creating 3D volume for series 1.2.826... with 64 slices
2024-01-15 10:30:08 - INFO - Created mesh at threshold 0.3: 15420 vertices, 30840 faces
2024-01-15 10:30:09 - INFO - Created mesh at threshold 0.5: 8250 vertices, 16500 faces
2024-01-15 10:30:10 - INFO - Created mesh at threshold 0.7: 4120 vertices, 8240 faces

DICOM Processing Summary
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
Total valid DICOM files: 192
Number of series: 3

Visualization Options:
• Individual images: series/{series_uid}
• 3D tensor volumes: volumes/tensor/{series_uid}
• 3D mesh surfaces: volumes/mesh/{series_uid}
```

## Development

### Install Development Dependencies

Development dependencies are automatically installed with `poetry install`.

### Code Formatting

```bash
poetry run black dicom_rerun/
```

### Linting

```bash
poetry run flake8 dicom_rerun/
```

### Testing

```bash
poetry run pytest
```

## Project Structure

```
dicom_rerun/
├── dicom_rerun/
│   ├── __init__.py          # Package initialization
│   └── main.py              # Main DICOM viewer script
├── pyproject.toml           # Poetry configuration and dependencies
├── README.md                # This file
└── dicom_analysis.log       # Generated log file (after running)
```

## Dependencies

### Core Libraries
- **Python**: ≥3.10, <3.13
- **pydicom**: ^2.4.0 - DICOM file processing
- **rerun-sdk**: ^0.18.0 - Interactive 3D visualization
- **numpy**: ^1.26.0 - Numerical computations
- **scikit-image**: ^0.22.0 - Marching cubes algorithm for mesh generation

### Development Tools
- **pytest**: ^7.0 - Testing framework
- **black**: ^23.0 - Code formatting
- **flake8**: ^6.0 - Code linting

## Medical Imaging Use Cases

This tool is perfect for:

- **CT Scan Analysis**: Visualize bone structures, organs, and soft tissues
- **MRI Data Exploration**: Interactive brain anatomy, tumor visualization
- **Medical Research**: 3D analysis of anatomical structures
- **Educational Purposes**: Teaching medical imaging concepts
- **Clinical Review**: Multi-perspective examination of patient data

## Technical Features

- **Marching Cubes Algorithm**: Generates smooth 3D surfaces from volumetric data
- **Multi-threshold Visualization**: Simultaneous display of different tissue densities
- **Memory Efficient**: Optimized processing for large DICOM datasets
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Web-based Viewer**: No additional software installation required

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please create an issue on the project repository.