# Adobe Onboarding Flow


## SCOPE
#### Covers only: 
turbo-sourcing + turbo-provisioning driven Adobe applications (spool_id = 59dc2abf-7dcc-45d9-81de-29f8b17e5942).
#### Exclude: 
Payzapp flow (see separate file), post-dispatch card lifecycle issues, rewards, repayments.


## DOMAIN OVERVIEW

### STAGES of Cosmos Application
1. DATA_CAPTURE
   - External system(Perseus here) invokes "turbo-sourcing" service's POST /spools/{spoolId}/applications endpoint to create applications.
   - This endpoint accepts the details, populate campaign details if any and creates cosmos applications.
   - Based on "submit" boolean flag received in create application API, turbo-sourcing then marks DATA_CAPTURE stage as completed by invoking Cosmos's API.
2. PROVISIONING
   - As soon as DATA_CAPTURE stage is marked as COMPLETED, Cosmos Application then moves into PROVISIONING INITIATED stage.
   - Every change in Cosmos application publish an Kafka event in APPLICATION_V1 topic.
   - "turbo-provisioning" service then listens to these events. Turbo Provisioing Service's endpoint POST /spools/{spoolId}/applications/{applicationId}/provisions will be invoked.
   - This service endpoint then resolves the workflow based on product code such as Pixel Play, Pixel Go, Times, etc. This workflow is series of operations required to perform an Credit Card issuance for an user.


### Provisioning Worflow

#### Primary Sevices Involved in Provisioning Workflow
- **turbo-provisioning:** Orchestrates provisioning workflow
- **Mars:** Maintain's account holder data. It also provides APIs to /createAccountHolder, /updateAccountHolder, /updateEffectiveKYCStatus, /addTags and /addBeneficiary
- **Aether:** Aether services orchestrates the bundle issuance. Bundle is combined entity of credit account, cashback account, cards, ledgers, etc
  Aether provides APIs to /issueBundle, /getIssuedBundleDetails, /issueCard and /getBundleDefinition.
- **Cerberus:** This service takes cares of creating auth profiles, getting auth profiles, etc. Auth profile is a user identity in authN/authZ domain
- **Cosmos:** Maintains application data and lifecycle end-to-end
- **Mercury**: Mercury service manages any communication with end user such as email, SMS, push notification, etc. It provides APIs to trigger an communication.
- **Plutus/Payzapp Onboarding**: This services handles user onboarding on Payzapp app. This service also maintains the user verified emails, etc.
- **Ruby:** Ruby maintains user's credit account. Aether uses Ruby's APIs to create an account when issuing a bundle. It provides APIs such as getAccount, closeAccounts, getCardsPerAccount, etc.
- **turbo-account-management-service(TAMS):** This servies manages post onboarding lifecycles such as passbook, card hotlisting, card reissuance, setting PINs, dispatching cards.
- **turbo-onboarding-service(TOS):** Post Payzapp onboarding, TOS takes cares of onboarding user to Pixel. This service handles user onboarding, performing verifications such as Aadhaar, Pan, integration with HDFC Bank's APS system primarily taking card of credit decisioning at bank. 


#### Provisioing Flow
The provisioning workflow consists of series of items. Below is the order in sequence.
1. ValidatorWorkFlow: The component is responsible for validating a user's provisioning request in a workflow. It mainly performs two checks:
   1. **Deduplication Check:** It checks if the user's details (like phone, PAN, Aadhaar) are already present in the system using the AccountHolderDedupeService. If a duplicate is found, it raises a business exception.
   2. **Existing Account Check:** It checks if the user already has any active Pixel accounts by: Fetching the user's identity from the Mars service. Using the identity to get account details from the Ruby service. Filtering out closed or non-Pixel accounts. If any active account (other than the current application) is found, it throws an exception to prevent duplicate account creation.
   Below are the associated details found in Cosmos provisioning stage details.
   ```json
      "dedupeResult": {
            "reason": "",
            "result": [],
            "status": "SUCCESS"
      },
      "existingAccounts": [] // non empty array means there is an existing account. This may lead to provisioning failed stage
   ```
2. **AddAuthProfileWorkflowV2:** 
   1. It checks if an authentication profile already exists for the user's phone number.
   2. If it exists, it uses the existing profile's ID.
   3. If not, it creates a new authentication profile using the Cerberus service, associating the phone number and some metadata.
   4. Once the profile is found or created, it updates the workflow state to mark this step as completed.
   5. All operations are asynchronous.
   6. If it cannot find or create a valid profile, it throws a business exception.
   Below are the associated details found in Cosmos provisioning stage details 
   ```json
      "authProfile": {
            "status": "COMPLETED",
            "authProfileId": "O6urV_920h4uGVHOwEVlCw=="
      }
   ```
3. **AddDefaultConfigWorkflow:** 
   1. It checks if the default theme and card network need to be set for a product.
   2. If they are not already set, it retrieves the default values from ProductConfig.
   3. It then uses the CosmosClient to add or update the relevant sections (theme or card network) in the application's configuration in the database.
   4. The workflow is considered complete when both the theme and card network are configured, or if the product does not require defaults for them.
   To see these details, refer cosmos application "theme" and "cardNetwork" section.
4. **SetupAccountHolderWorkflow:**
   1. It checks if an account holder already exists for the given phone number.
   2. If the account holder exists, it updates their KYC status, tags, and details.
   3. If not, it creates a new account holder.
   4. It adds or updates the account holder’s email vector, possibly verifying it if linked to Payzapp.
   5. It adds any beneficiaries specified in the request.
   6. The workflow is marked complete when the account holder is set up and marked as completed in the provisioning details.
   Below are the associated details found in Cosmos provisioning stage details 
   ```json
      "accountHolder": {
            "id": "c980edcf-7a21-4dcc-a844-bd46747ac4a6",
            "status": "COMPLETED",
            "authProfileId": "O6urV_920h4uGVHOwEVlCw=="
      }
   ```
5. **IssueBundleWorkflow:**
   1. It checks if the account holder is set up before proceeding.
   2. It fetches the account holder using their phone number.
   3. It builds a request with all necessary details (limits, preferences, tags, etc.) to issue the bundle.
   4. It calls an external service to actually issue the bundle.
   5. Once the bundle is issued, it updates the provisioning details with the issued accounts and bundle information.
   6. The workflow is marked complete when the bundle is successfully issued.
   Below are the associated details found in Cosmos provisioning stage details 
   ```json
      "bundle": {
            "status": "COMPLETED",
            "accounts": [
                {
                    "id": "98a88efa-00a4-4e69-bce8-428dfb403fbf"
                }
            ],
            "bundleId": "f339f128-2260-4e99-a1be-5519be2c4006",
            "issuanceId": "c6aad082-b38e-4809-8ca9-af0c2c461abf"
      }
   ```
6. **IssueCardWorkflow:**
   1. It checks if the card issuance step is already completed.
   2. It ensures that the required bundle (accounts/products) has been issued before proceeding.
   3. It verifies that the associated account is not closed.
   4. If then fetches the selected card along with isPhysical flag from Cosmos "cardNetwork" section. If networkSection is empty in Cosmos "cardNetwork" section, it then breaks the workflow with PENDING as stage status, "EXTERNAL_DEPENDENCY" as reasonCode indication user input(seleting network choices here) to resume the workflow.
   5. For each selected card type (form factor), it builds a request and calls an external service to issue the card.
   6. Once cards are issued, it updates the provisioning details with the card issuance information.
   7. It handles errors such as missing network selection or closed accounts.
   Below are the associated details found in Cosmos provisioning stage details 
   ```json
      "cardIssuance": {
         "cards": [
            {
                  "cardId": "421b054e-110f-4d7d-aedf-e87d99a7fe6c",
                  "status": "COMPLETED",
                  "identifier": "VISA",
                  "isCardEnabled": true,
                  "cardFFProductId": "34cfc1fe-12d2-49ca-bd73-90fa9beb3629"
            },
            {
                  "cardId": "68a7cac0-f92d-429b-b93a-1655748c6c36",
                  "status": "COMPLETED",
                  "identifier": "RUPAY",
                  "isCardEnabled": true,
                  "cardFFProductId": "168f664d-ee6f-4943-8824-408c377b7ba6"
            }
         ],
         "status": "COMPLETED"
      },
   ```
7. **CardStatusValidatorWorkflow:**
   1. It runs after cards have been issued.
   2. It fetches the latest card status details from an external service.
   3. It updates each card’s enabled status in the provisioning details.
   4. If any card is not active, it throws an error to indicate the workflow cannot proceed.
   5. The workflow step is considered complete only when all cards are active.
   Refer "isCardEnabled" flag in Cosmos provisioning stage details "cardIssuance" object
8. **SelectThemeWorkflow:** 
   1. It checks if a theme has already been selected and marked as completed.
   2. It allows theme selection at any time (no dependencies on previous steps).
   3. When executed, it verifies that a theme ID is present on Cosmos application, "theme" section. If theme not found in theme section, the workflow breaks with error "EXTERNAL_DEPENDENCY" as reasonCode. Indication, user input(selecting theme) is required to resume the workflow.
   4. It fetches the current theme for the user from TOS service; if the theme is not set or does not match the requested one, it saves the new theme using the TOSClient.
   5. After saving (or if already set), it updates the provisioning details with the selected theme.
   ```json
      "theme": {
         "id": "PXLIE",
         "status": "COMPLETED"
      }
   ```
9.  **DispatchCardWorkflow:**
   1.  It checks if card dispatch is already completed.
   2.  It ensures that cards have been issued and a theme has been selected before dispatching.
   3.  It fetches the theme details needed for the card’s appearance.
   4.  It builds a dispatch request with user, card, address, and theme information.
   5.  It calls an external service to initiate the card dispatch.
   6.  Once the card is dispatched, it updates the provisioning details to mark this step as complete.
   7.  It handles errors such as missing theme or no cards to dispatch.
   Below are the associated details found in Cosmos provisioning stage details
   ```json
      "cardDispatch": {
         "status": "COMPLETED"
      },
   ```
10. **GenerateApplicationPdfWorkflowV2:**
    1.  It checks if the PDF generation step is already completed.
    2.  It validates that the user's email address is present in the request.
    3.  It builds a request to generate the application PDF with default values.
    4.  It sends an email notification with the generated PDF attached using the Mercury client.
    5.  Once the email is sent, it updates the provisioning details to mark the PDF generation as complete.
    6.  If the email is missing, it throws an error and logs it.
    ```json
      "applicationPDF": {
         "status": "COMPLETED"
      },
    ```


### Debugging Adobe Worflow
1. First resolves the user ttributes provided in input to an application_id
2. Fetch the required applcation section, stage data.
3. Analyze reasonCode, reasonDescription, stage validate results from cosmos stage table details column to figure out any issue.
4. Fetch the logs.  If you need detailed assistance with querying logs, requets for additional knowledge such as "debugging_with_log_detailed.md".
5. Analyze the stacktraces and other logs to come to an conclusion.
6. Use may use timestamps from Cosmos stage updated_at, created_at to query logs with time range.

### when to stop
Stop or ask for human intervention if all the application stage, section details, logs looks fine and no error recorded.