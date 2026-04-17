from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, validator
from typing import Optional
import os
from mosip_auth_sdk.models import DemographicsModel
from mosip_auth_sdk import MOSIPAuthenticator
from dynaconf import Dynaconf

from ID_Payload import ScannedIDPayload

# [1] Config [as shown in template]
config = Dynaconf(settings_files=["./config.toml"], environments=False)
authenticator = MOSIPAuthenticator(config=config)

# API Key Auth for Cloud shenanigans that I don't fully understand yet
'''
# ── API Key Auth ─────────────────────────────────────────────
# Store this in your environment: export ESP32_API_KEY="your-secret-key"
# Flash the same key into your ESP32 firmware
API_KEY = os.environ.get("ESP32_API_KEY", "change-me-in-production")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return key
'''

# [2] API app for HTTP and JSON handling
app = FastAPI()

# [3] Authentication Function
@app.post("/authenticate")
async def authenticate(
    payload: ScannedIDPayload,      # from ID_Payload import ScannedIDPayload
    # api_key: str = Depends(verify_api_key),   # ← blocks unauthorized callers [API stuff I don't understand yet]
):
    # Build language-wrapped fields
    def wrap(value):
        return [{"language": "eng", "value": value}] if value else None
    # # #

    demographics_data = DemographicsModel(
        name = wrap(payload.name),
        dob = payload.dob,
        location1 = payload.location1,
        location3 = payload.location3,
        zone = payload.zone,
        postal_code = payload.postal_code,
        address_line1 = wrap(payload.address_line1),
        address_line2 = wrap(payload.address_line2),
        address_line3 = wrap(payload.address_line3),
    )

    try:        # try authenticating
        response = authenticator.auth(
            individual_id = payload.uin,
            individual_id_type = "UIN",
            demographic_data = demographics_data,
            consent = True,
        )
        response_body = response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail="Identity service unavailable")

    # contruct and return authstatus
    auth_status = response_body.get("authStatus", False)

    return {
        "authStatus": auth_status,
        "errors":     response_body.get("errors", None),
    }

# cloud stuff for later:
'''
# HEALTH CHECK (for cloud)
@app.get("/health")
async def health():
    return {"status": "ok"}
'''