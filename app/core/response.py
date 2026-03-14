from datetime import datetime

def success_response(data):
    return {
        "metaData": {
            "apiVersion": "1.0",
            "apiResponseDtts" : str(datetime.now()),
        },
        "data": data
    }


def error_response(code, message):
    return {
        "metaData": {
            "apiVersion": "1.0",
            "apiResponseDtts" : str(datetime.now()),
        },
        "error": {
            "error_code": code,
            "error_desc": message
        }
    }
