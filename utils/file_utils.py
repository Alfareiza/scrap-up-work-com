from settings import BASE_DIR, log


def export_json(data: str, filename: str) -> None:
    """
    Create a json file with the information coming in data.
    :param filename: Name of the file to be exported.
    :param data: Dictionary with the information to be exported
                 into a json file.
    """
    try:
        jsonfilepath = BASE_DIR / f"{filename}.json"
        with open(jsonfilepath, 'w', encoding='utf-8-sig') as jsonfile:
            jsonfile.write(data)
    except Exception as e:
        log.error(f"Exporting json file with data: {e}")
    else:
        log.info(f"File created with scanned data: {jsonfilepath}")
