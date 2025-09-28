# Cosmos: 
Cosmos acts like a datastore to store a user data collected across multiple frontend screens.

**db name = cosmos_local**
**database_id = 7**

## 1. Tables Overview
- application
- application_stage
- application_section

### Primary relationships:
- application.id = application_stage.application_id (1:M)
- application.id = application_section.application_id (1:M)

All timestamps are ISO-8601 UTC (Z). All UUIDs are canonical lowercase UUID strings unless otherwise noted.

## 2. Table: application
Purpose: Stores the high-level lifecycle state of an onboarding application.

Fields:
- id (UUID, PK)
- spool_id (UUID) : spool id is a type of application or group of same type applications
- status (STRING ENUM)
  - Possible: CREATED, DATA_CAPTURE_INITIATED, DATA_CAPTURE, PROVISIONING_INITIATED, PROVISIONING_FAILED, COMPLETED, REJECTED, FAILED
- ifi_id : Financial institution identifier / tenant.
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- Success path would end at e.g. COMPLETED.

Example row:
```json
{
  "id": "9f49e5c9-6484-4397-a3a9-bb14242bfca8",
  "spool_id": "59dc2abf-7dcc-45d9-81de-29f8b17e5942",
  "status": "PROVISIONING_FAILED",
  "ifi_id": 1000001,
  "created_at": "2025-09-03T08:14:08.705Z",
  "updated_at": "2025-09-09T15:10:30.417Z",
  "request_id": "194599731315697"
}
```

---

## 3. Table: application_stage
Purpose: Captures discrete processing stages and their outcomes.

Fields:
- id (UUID, PK)
- application_id (UUID, FK -> application.id)
- name (STRING ENUM)
  - DATA_CAPTURE, PROVISIONING, ENRICHMENT
- status (STRING ENUM)
  - COMPLETED, FAILED, INITIATED, NOT_INITIATED
- result (JSONB) : Outcome metadata for the stage (validation, decision).
- details (JSONB) : Extended contextual data (sub-process statuses, error causes).
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- ifi_id (INT)
- reason_code: If not blank, the is the reason code behind any failures. 
- reason_description: If not blank, the is the a description about the failure 

Observed result JSON schema
```json
{
  "validationPassed": {
    "validation": "successful"
  }
}
```

## 4. Table: application_section
Purpose: Stores user-entered or system-generated sections of the application form / verification artifacts.

Fields:
- id (UUID, PK)
- application_id (UUID, FK -> application.id)
- name (STRING ENUM) : Section identifier (see catalog below).
- details (JSONB) : Section payload.
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- ifi_id (INT)

---

## 5. Section Catalog & JSON Schemas


### 5.1 contactDetails
User Contact details
details:
```json
{
  "emailId": "example@domain.com"// string,
  "phoneNumber": "+918989898989" // string  with country code followed by 10 digit number.
}
```

### 5.2 shipping
Shipping address to deliver the card
```json
{
  "preferredDeliveryTime1": "",
  "preferredDeliveryTime2": "",
  "addressLine1": "",
  "addressLine2": "",
  "state": "",
  "pincode": "",
  "city": ""

}
```

### 5.3 personalDetails (type: input)
```json
{
  "dob": "",// 
  "title": "", // e.g. Mr., Ms., Dr.
  "gender": "",
  "lastName": "",
  "firstName":"",
  "middleName": "",
  "nationality": "",    // e.g. INDIAN
  "maritalStatus": "",  // e.g. Married, Single
  "indianResident": ""
}
```

### 5.4 familyDetails
This section is used as a beneficiary and for CKYC purpose
```json
{
  "mother": {
    "maidenName": // used for CKYC
  },
  "spouse": {
    "name": "",
    "companyName": "",
    "officeTelephoneNo": ""
  }
}
```

### 5.5 existingCustomerDetails
```json
{
  "customerId": "" // bank customer id
}
```

### 5.6 employmentDetails
```json
{
  "companyCode": "",
  "designation": "",
  "employerName": "",
  "officeEmailId": "",
  "occupationType": "", 
  "currentPosition": "",
  "officeExtensionNo": "",
  "officeTelephoneNo": ""
}
```

### 5.7 card
```json
{
  "nameOnCard": // name to be printed on card
}
```

### 5.8 communicationAddress
```json
{
  "city": "",
  "state": "",
  "pincode": "",
  "landmark": "",
  "addressLine1": "",
  "addressLine2": "",
  "addressLine3": "",
  "addressLine4": ""
}
```

### 5.9 theme
```json
{
  "themeId": "", // e.g PXLGO, PXLLT, PXLIE, PXLPP
  "metadata": {
    "selectedBy": "", // selected by user(users.in) or selected by system(admin-india.in)
    "defaultConfigId": "", // if the theme was selected due to default config set against the offer/product code such as ZLT, ZMX, TRMAX, ZTZAP, ZTC
  }
}
```

### 5.10 aadhaar
```json
{
  "aadhaarReferenceNumber": ""   // tokenized / reference, not raw Aadhaar
}
```

### 5.11 permanentAddress
```json
{
  "city": "",
  "pincode": "",
  "telephone": "",
  "addressLine1": "",
  "addressLine2": "",
  "addressLine3": ""
}
```

### 5.12 bankRelationship
```json
{
  "salesReferenceNumber": "" // Code of the person who helped user to fill this application and get the Pixel card
}
```

### 5.13 cardNetwork
```json
{
  "networkSelections": [] // e.g. ["VISA", "MASTERCARD", "RUPAY"]
}
```

### 5.14 pan
```json
{
  "pan": ""  // PAN number
}
```

### 5.15 applicationDecision 
```json
{
  "offerCode": "", // product user is will be getting such as ZLT, ZMX, TRMAX, ZTZAP, ZTC
  "creditLimit": "", // credit limit in INR user has got.
  "decisionTime": "" 
}
```

### 5.16 employmentAddress
```json
{
  "fax": "",
  "city": "",
  "pincode": "",
  "landmark": "",
  "telephone": "",
  "addressLine1": "",
  "addressLine2": "",
  "addressLine3": ""
}
```

### 5.17 education 
```json
{
  "education": ""
}
```

### 5.18 attributes
```json
{
  "regionCode": "",
  "externalApplicationDate": "" // date when user had applied for card at bank.
}
```



## 6. High-Level Lifecycle (Observed Flow)
application table staus column
1. DATA_CAPTURE COMPLETED
2. DATA_CAPTURE INITIATED
3. ENRICHMENT INITIATED
4. ENRICHMENT COMPLETED
5. PROVISIONING INITIATED
6. PROVISIONING FAILED

Success path (expected):
DATA_CAPTURE_INITIATED -> DATA_CAPTURE_COMPLETED -> ENRICHMENT_INITIATED -> ENRICHMENT_COMPLETED -> PROVISIONING_INITIATED -> COMPLETED



## 7. Query guidelines
1. Do not include db name in queries. Choose correct database_id and directly query table. 
e.g. cosmos_local.application is wrong. Do application instead.
End of schema.
2. Postgres is powering the metabase hence use postgresql.
3. The examples provided are just for reference. Do not query the DB searching for predefined errors. Instead strictly follow generic approach