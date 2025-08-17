# DICOM Analyzer

A Python tool that uses pydicom to read DICOM files from a folder, extract metadata, group studies by series UUID, and provide comprehensive logging and statistics.

## Features

- **Recursive DICOM File Reading**: Scans folders and subfolders for DICOM files
- **Metadata Extraction**: Extracts comprehensive DICOM metadata including study/series information
- **Series Grouping**: Groups studies by Series Instance UID (Series UUID)
- **Comprehensive Logging**: Detailed console and file logging with statistics
- **Error Handling**: Gracefully handles invalid DICOM files

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

## Usage

### Run with Poetry

```bash
poetry run python main.py
```

Or activate the virtual environment and run directly:

```bash
poetry shell
python main.py
```

### Using the Script Command

You can also use the configured script:

```bash
poetry run dicom-analyze
```

The script will prompt you to enter the path to your DICOM folder.

## Output

The script provides:

- **Console Output**: Real-time progress and statistics
- **Log File**: Detailed logging saved to `dicom_analysis.log`
- **Statistics**: 
  - Total number of series and studies
  - Studies per series with metadata
  - Average, min, and max studies per series
  - Series descriptions, modalities, and patient information

## Example Output

```
2024-01-15 10:30:00 - INFO - Starting to scan folder: /path/to/dicom/folder
2024-01-15 10:30:05 - INFO - Scan complete. Total files: 150, Valid DICOM files: 145, Invalid files: 5
==================================================
DICOM ANALYSIS STATISTICS
==================================================
Total number of series: 5
Total number of studies: 145
--------------------------------------------------
Studies per series:
  Series UID: 1.2.826.0.1.3680043.8.498.45...
    Studies: 50
    Description: T1 MPRAGE
    Modality: MR
    Patient ID: 12345
------------------------------
```

## Development

### Install Development Dependencies

Development dependencies are automatically installed with `poetry install`.

### Code Formatting

```bash
poetry run black main.py
```

### Linting

```bash
poetry run flake8 main.py
```

### Testing

```bash
poetry run pytest
```

## Project Structure

```
dicom-analyzer/
├── main.py              # Main DICOM analysis script
├── pyproject.toml        # Poetry configuration and dependencies
├── README.md            # This file
└── dicom_analysis.log   # Generated log file (after running)
```

## Requirements

- Python 3.8+
- pydicom 2.4.0+

## License

This project is open source and available under the MIT License.
