# BlueButtonFHIR_API
This is the BlueButton On FHIR Pass through API. This application will handle the backend calls to the FHIR Server and will perform beneficiary authentication and Client Application OAuth Key validation 

This is one part of a three part application suite:

0. BlueButtonUser - Front-end user application 
   ( https://github.com/ekivemark/BlueButtonUser )
0. BlueButtoDev - Front-end Developer administration application
   ( https://github.com/ekivemark/BlueButtonDev )
0. BlueButtonFHIR_API - Public API providing authenticated pass-through to back-end FHIR Services. 
   ( https://github.com/ekivemark/BlueButtonFHIR_API ) 
 
In the current iteration the Developer and User Accounts are handled in this single application. 
User Model has is_developer and is_user boolean settings. 
User mode should be chosen if both are True.


