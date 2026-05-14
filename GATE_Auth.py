from fastapi import FastAPI, HTTPException
from mosip_auth_sdk.models import DemographicsModel
from mosip_auth_sdk import MOSIPAuthenticator
from dynaconf import Dynaconf
import time

from ID_Payload import ScannedIDPayload
from database import process_entry, process_exit, process_reset 

# [1] Config
config = Dynaconf(settings_files=["./config.toml"], environments=False)
authenticator = MOSIPAuthenticator(config=config)

# [2] App
app = FastAPI()


# [3] Shared MOSIP auth helper
def run_mosip_auth(payload: ScannedIDPayload) -> bool:
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

    # try:
    #     response = authenticator.auth(
    #         individual_id=payload.uin,
    #         individual_id_type="UIN",
    #         demographic_data=demographics_data,
    #         consent=True,
    #     )
    #     return response.json().get("response", {}).get("authStatus", False)
    # except Exception:
    #     raise HTTPException(status_code=503, detail="Identity service unavailable")

    is_error = False
    for x in range(3):
        try:
            response = authenticator.auth(
                individual_id=payload.uin,
                individual_id_type="UIN",
                demographic_data=demographics_data,
                consent=True,
            )
            return response.json().get("response", {}).get("authStatus", False)
        except Exception:
            print("Identity service unavailable")
            is_error = True
            time.sleep(3)
    if is_error:
        raise HTTPException(status_code=503, detail="Identity service unavailable")
    raise HTTPException(status_code=500, detail="Did not return or raise error code 503")


# [4] Entry endpoint
@app.post("/enterRequest")
async def enter_request(payload: ScannedIDPayload):
    if not run_mosip_auth(payload):
        return {"authStatus": False, "status": "not in MOSIP"}

    db_payload = {"uin": payload.uin, "precinctID": payload.precinctID}
    success, status = process_entry(db_payload)
    return {"authStatus": success, "status": status}


# [5] Exit endpoint
@app.post("/exitRequest")
async def exit_request(payload: ScannedIDPayload):
    if not run_mosip_auth(payload):
        return {"authStatus": False, "status": "not in MOSIP"}

    db_payload = {"uin": payload.uin, "precinctID": payload.precinctID}
    success, status = process_exit(db_payload)
    return {"authStatus": success, "status": status}


@app.post("/resetState")
async def reset_state():
    success, status = process_reset()
    return {"authStatus": success, "status": status}