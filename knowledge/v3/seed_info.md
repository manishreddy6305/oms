### PURPOSE
Use this guide ONLY to triage and route onboarding or card management issues for the Pixel credit card program. Do not deep-dive here; this file is for: 
(a) deciding if you should proceed, 
(b) identifying the journey (Adobe vs Payzapp), 
(c) finding the correct POC, 
(d) selecting the next debugging playbook.
(f) Jira traiging
(g) Do not send or modify an custom field in JIRA tools

### SCOPE
Handle ONLY onboarding flow issues
Ignore: card management, account management, rewards, statements, repayments, ledger

### POCs
1. Onboarding (all journey questions, missing data, creation failures, cards not issues, pending application, error while onboarding): omkaram@zeta.tech
2. Card management (transactions, card lifecycle, PIN, status, reissue, controls, statements, repaymnets, cashbacks, etc): manishna@zeta.tech


### ONBOARDING FLOWS
1. Adobe channel: User originates from an external (Adobe) system → we issue credit bundle + card.
2. Payzapp channel: User installs Payzapp app → applies → we issue credit bundle + card.


### Answering User Queries
1. If user is asking simple queries, simply request for additional relavent knowledge.
2. If user has explicitly mentioned about journey, then refer the same and start debugging the particular flow. No need to validate user inputs.
3. If user has not given any journey details, then figure out the journey by spool_id and start with respective journey debugging steps.

### HOW TO IDENTIFY JOURNEY
Query cosmos_local application and fetch spool_id:
- spool_id = 2007c5be-16ad-4971-b9f1-4624450eac9c → Payzapp flow
- spool_id = 59dc2abf-7dcc-45d9-81de-29f8b17e5942 → Adobe flow
If multiple records: ensure you pick the latest application tied to the reported user identifier (mobile/email/customer ref).
If spool_id is neither: flag to onboarding POC before proceeding.

### Point to note
1. Always ask for human intervention when stuck. Add all the relavent details you collected so far.
2. Do not merge journeys (each application maps to exactly one flow).
3. If jira or users doesn't provide any details to start the debugging with, request for additional information.



### NEXT STEP AFTER IDENTIFYING JOURNEY
Ask for additional knowledge such as adobe flow debugging, payzapp flow debugging, jira playbook, debgging logs in details, etc.