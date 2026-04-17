from mosip_auth_sdk import MOSIPAuthenticator
from dynaconf import Dynaconf

config = Dynaconf(settings_files=["./config.toml"], environments=False)
authenticator = MOSIPAuthenticator(config=config)

# step 2: use OTP and transaction ID in auth request
# can change function to authenticator.kyc()
# but don't forget to decrypt the response for that
response = authenticator.auth(
    individual_id="5408602380",
    individual_id_type="UIN",
    otp_value="PLACE OTP HERE",
    txn_id="PLACE TRANSACTION ID HERE",
    consent=True,
)
response_body = response.json()
print(f"RESPONSE: {response_body}")
