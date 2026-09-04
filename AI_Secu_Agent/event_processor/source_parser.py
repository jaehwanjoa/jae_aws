import json

def parse_xdr(data):

    if isinstance(data, list):
        return {
            "source": "xdr",
            "id": data[0]["internal_id"]
        }

    return {
        "source": "xdr",
        "id": data["internal_id"]
    }


def parse_guardduty(data):

    return {
        "source": "guardduty",
        "id": data["detail"]["id"]
    }


def parse_waf(data):

    return {
        "source": "waf"
    }
