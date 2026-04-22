from fastapi import FastAPI, HTTPException
from mosip_auth_sdk.models import DemographicsModel
from mosip_auth_sdk import MOSIPAuthenticator
from dynaconf import Dynaconf

from ID_Payload import ScannedIDPayload

# [1] Config
config = Dynaconf(settings_files=["./config.toml"], environments=False)
authenticator = MOSIPAuthenticator(config=config)

# [2] App
app = FastAPI()

# [3] Authentication endpoint
@app.post("/authenticate")
async def authenticate(payload: ScannedIDPayload):
    def wrap(value):
        return [{"language": "eng", "value": value}] if value else None

    demographics_data = DemographicsModel(
        name=wrap(payload.name),
        dob=payload.dob,
        location1=wrap(payload.location1),
        location3=wrap(payload.location3),
        zone=wrap(payload.zone),
        postal_code=wrap(payload.postal_code),
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
        response_body = response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail="Identity service unavailable")

    return {
        "authStatus": response_body.get("authStatus", False),
        "errors":     response_body.get("errors", None),
    }