## Changelog

### April 17:
- Started refactoring MOSIP Auth Code from template:
    - refactored Y/N Auth Code to dynamically take in a payload from an HTTP POST from the ESP32x using FastAPI
    - made class ScannedIDPayload to structure the payload into a DemographicsData
    - refactored authentication function to take in all ID fields as part of the MOSIP authentication check
    - refactored to return the authstatus
    - placed template API key codes bc it might be important for cloud integration
- Next:
    - add MOSIP keys and other dependencies
    - recheck the API thingy
    - check cloud integration

### April 22:
- Cleaned code for AWS migration (removed unnecessary dependencies)
- added dependencies (MOSIP keys etc.)
- filled in config.toml file
- added local set up testing instructions
- tested => PASSED 7/7 TEST CASES
- Fixes:
    - added wrapping to all necessary values
    - returned whole response for now
- Next:
    - edit code to only return authstatus

### April 26:
- Started drafting query code (all files under "querying")
- Designed to be easily integrated with actual database