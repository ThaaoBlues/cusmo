from base64 import decodebytes, encodebytes
from string import digits


def is_endpoint_valid(endpoint:str):
    """check if the given endpoint is not another thing than an endpoint

    Args:
        endpoibnt (str): _description_
    """
    
    try:
        int(endpoint)
    except:
        return False
        
    return True


def encode_dict(data:dict):
    
    return encodebytes(str(data).encode("utf-8"))

def decode_dict(data:dict):
    return decodebytes(data).decode("utf-8")
    
    
