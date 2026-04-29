from fastapi import FastAPI, HTTPException
from mosip_auth_sdk.models import DemographicsModel
from mosip_auth_sdk import MOSIPAuthenticator
from dynaconf import Dynaconf

from ID_Payload import ScannedIDPayload
from database import process_entry, process_exit 

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

    try:
        response = authenticator.auth(
            individual_id=payload.uin,
            individual_id_type="UIN",
            demographic_data=demographics_data,
            consent=True,
        )
        return response.json().get("response", {}).get("authStatus", False)
    except Exception:
        raise HTTPException(status_code=503, detail="Identity service unavailable")


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