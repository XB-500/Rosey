from mabel.operators import EndOperator

VERSION_FILE_URL = "https://raw.githubusercontent.com/joocer/mabel/{branch}/mabel/version.py"

def version_checker_flow():

    # extract_details
    # retrieve_version_file
    # submit push if the versions  don't match

    end = EndOperator()
