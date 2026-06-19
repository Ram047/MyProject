import pandas as pd


def load_excel(file_path, sheet_name=0):
    """
    Load an Excel file into a pandas DataFrame.
    Uses header=1 because the first row contains the report title.
    """

    try:
        df = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            header=1
        )

        return df

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")

    except Exception as e:
        raise Exception(f"Error loading Excel file: {e}")