from mosip_auth_sdk.models import DemographicsModel
from mosip_auth_sdk import MOSIPAuthenticator
from dynaconf import Dynaconf

config = Dynaconf(settings_files=["./config.toml"], environments=False)
authenticator = MOSIPAuthenticator(config=config)

# yes/no auth
demographics_data = DemographicsModel(dob="1997/09/12")
response = authenticator.auth(
    individual_id="5408602380",
    individual_id_type="UIN",
    demographic_data=demographics_data,
    consent=True,
)
response_body = response.json()
print(f"RESPONSE: {response_body}")

# try with other demographic data
# can be dob, age, phone_number, email_id, postal_code,
# location1 (city), location3 (province), zone (barangay),
# address_line1, address_line2, address_line3,
# name, gender
demographics_data = DemographicsModel(
    name=[{"language": "eng", "value": "Yuki Nakashima"}],
    address_line1=[{"language": "eng", "value": "UP AECH"}],
)
response = authenticator.auth(
    individual_id="5408602380",
    individual_id_type="UIN",
    demographic_data=demographics_data,
    consent=True,
)
response_body = response.json()
print(f"RESPONSE: {response_body}")
