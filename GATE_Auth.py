from fastapi import FastAPI, HTTPException
from mosip_auth_sdk.models import DemographicsModel
from mosip_auth_sdk import MOSIPAuthenticator
from dynaconf import Dynaconf
from pprint import pprint
import time
import requests

from ID_Payload import ScannedIDPayload
from database import process_entry, process_exit, process_reset 

# [1] Config
config = Dynaconf(settings_files=["./config.toml"], environments=False)
authenticator = MOSIPAuthenticator(config=config)

# [2] App
app = FastAPI()

DUMMY_URL = "https://cs145-iot-cup-1745973870.ap-southeast-1.elb.amazonaws.com"
useMock = True

# [3] Shared MOSIP auth helper
def run_mosip_auth(payload: ScannedIDPayload, mock = False) -> bool:
    def wrap(value):
        return [{"language": "eng", "value": value}] if value else None

    demographics_data = DemographicsModel(
        name=wrap(payload.name),
        dob=payload.dob,
        location1=wrap(payload.location1),
        location3=wrap(payload.location3),
        zone=wrap(payload.zone),
        postal_code=payload.postal_code,
        address_line1=wrap(payload.address_line1),
        address_line2=wrap(payload.address_line2),
        address_line3=wrap(payload.address_line3),
    )

    is_error = False
    for x in range(3):
        try:
            if mock:
                response = requests.post(
                    f"{DUMMY_URL}/api/v1/auth/yes-no",
                    json={
                        "individual_id": payload.uin,
                        "individual_id_type": "UIN",
                        "name": payload.name,
                        "dob": payload.dob,
                        "location1": payload.location1,
                        "location3": payload.location3,
                        "zone": payload.zone,
                        "postal_code": payload.postal_code,
                        "address_line1": payload.address_line1,
                        "address_line2": payload.address_line2,
                        "address_line3": payload.address_line3,
                        "consent": True
                    },
                    verify=False
                )
            else:
                response = authenticator.auth(
                    individual_id=payload.uin,
                    individual_id_type="UIN",
                    demographic_data=demographics_data,
                    consent=True,
                )
            data = response.json()
            print("MOSIP Auth request response:")
            pprint(data)
            return data.get("response", {}).get("authStatus", False)
        except Exception as e:
            print("Identity service unavailable")
            print(e)
            is_error = True
            time.sleep(3)
    if is_error:
        raise HTTPException(status_code=503, detail="Identity service unavailable")
    raise HTTPException(status_code=500, detail="Did not return or raise error code 503")


# [4] Entry endpoint
@app.post("/enterRequest")
async def enter_request(payload: ScannedIDPayload):
    print("QR Payload:", payload)
    if not run_mosip_auth(payload, mock=useMock):
        return {"authStatus": False, "status": "not in MOSIP"}

    db_payload = {"uin": payload.uin, "precinctID": payload.precinctID}
    success, status = process_entry(db_payload)
    return {"authStatus": success, "status": status}


# [5] Exit endpoint
@app.post("/exitRequest")
async def exit_request(payload: ScannedIDPayload):
    print("QR Payload:", payload)
    if not run_mosip_auth(payload, mock=useMock):
        return {"authStatus": False, "status": "not in MOSIP"}

    db_payload = {"uin": payload.uin, "precinctID": payload.precinctID}
    success, status = process_exit(db_payload)
    return {"authStatus": success, "status": status}


@app.post("/resetState")
async def reset_state():
    success, status = process_reset()
    return {"authStatus": success, "status": status}