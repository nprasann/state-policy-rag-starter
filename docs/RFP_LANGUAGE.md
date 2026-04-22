# RFP Language

This document provides sample procurement language for agencies evaluating or acquiring a policy-grounded AI assistant based on the architecture in this repository.

The text below is intended as a starting point for State IT, Legal, Security, and Procurement teams. Agencies should adapt it to their statutes, security baselines, hosting constraints, and records-retention requirements.

## 1. Purpose

The Agency seeks a solution or implementation partner to support a policy-grounded AI assistant that enables authorized users to retrieve answers from approved policy documents and, where explicitly permitted, from controlled case-data systems.

The solution must prioritize:

- in-state or state-controlled data handling
- strong auditability
- deterministic or low-variance model behavior
- citation-based responses
- strict control over system-to-system access
- support for legal, security, and procurement review

## 2. Functional Requirements

The proposed solution should:

- ingest approved policy documents, including PDF documents
- store policy content in a searchable vector database
- support retrieval-augmented generation using approved context only
- return responses with citations to policy or approved source systems
- support human escalation when the answer cannot be grounded in approved policy
- provide a documented API architecture suitable for integration with Teams, web applications, or internal workflow tools

## 3. Security And Privacy Requirements

The proposer must describe how the solution will:

- prevent the disclosure of PII or confidential data in prompts and responses
- restrict access to case or line-of-business systems to approved interfaces only
- prevent arbitrary SQL execution or equivalent unrestricted data access
- generate audit logs for user actions and system decisions
- support deployment in an isolated network segment
- disable or avoid external telemetry unless explicitly approved by the Agency

Preferred language:

`The solution shall support deployment in a state-controlled environment and shall not require agency content, prompts, responses, or operational data to be transmitted to third-party hosted model providers unless explicitly approved in writing by the Agency.`

## 4. Data Residency And Ownership

Use language such as:

`All Agency data, including documents, prompts, vector embeddings, output content, audit records, and configuration data, shall remain the property of the Agency.`

`The proposer shall describe whether the solution can be deployed entirely within Agency-controlled or Agency-approved infrastructure, including on-premises environments and state-approved cloud tenants.`

`The proposer shall identify all data flows leaving the Agency environment, if any, and shall provide a technical and contractual justification for each such flow.`

## 5. No Training / No Retention Language

Use language such as:

`Agency data shall not be used to train, fine-tune, improve, or otherwise modify foundation models or vendor systems without explicit prior written authorization from the Agency.`

`The proposer shall disclose all logging, retention, telemetry, and product analytics behavior associated with the solution.`

`The proposer shall provide configuration options to disable telemetry, external analytics, and non-essential data retention wherever technically supported.`

## 6. Model And Response Controls

Use language such as:

`The solution shall support configuration of model parameters to reduce output variance for policy-sensitive use cases, including support for deterministic or near-deterministic generation settings where appropriate.`

`The solution shall support response-grounding controls, including the ability to require citations to approved policy sources or approved source systems.`

`When sufficient grounding is unavailable, the solution should support a configurable escalation response directing the user to a supervisor, subject-matter expert, or other human review path.`

## 7. Access Control And Integration Requirements

Use language such as:

`The solution shall support integration with Agency identity and access controls, including support for enterprise identity providers where applicable.`

`The solution shall support service boundaries that separate user-facing interaction, retrieval logic, model inference, and system-of-record access.`

`Any access to Agency operational systems shall occur through explicit allowlists, approved interfaces, or stored procedures and shall not permit unrestricted query execution by end users or model-generated instructions.`

## 8. Hosting And Infrastructure Requirements

Use language such as:

`The proposer shall identify the minimum and recommended hardware requirements for pilot and production deployments, including CPU, memory, storage, and optional GPU requirements.`

`The proposer shall support deployment on state-approved virtual infrastructure, including Azure virtual machines and on-premises virtualized environments, subject to Agency network segmentation requirements.`

`The solution shall be deployable within a dedicated subnet, VLAN, or similarly isolated network segment and shall not require co-location with unrelated application servers.`

## 9. Audit And Oversight Requirements

Use language such as:

`The solution shall generate structured audit records for key user and system actions, including policy retrieval requests, controlled database access requests, and other administratively relevant events.`

`The proposer shall describe how audit records can be retained, exported, reviewed, and integrated with Agency logging or SIEM platforms.`

`The solution shall support review by technical, legal, privacy, and procurement stakeholders through clear documentation of architecture, data flow, and control points.`

## 10. Vendor Response Questions

The Agency may request responses to questions such as:

1. Describe how the proposed solution keeps Agency content within state-controlled infrastructure.
2. Identify every external dependency or hosted service required for core operation.
3. Explain how the solution prevents hallucinated or uncited policy advice.
4. Describe how the solution handles personally identifiable information and restricted case data.
5. Describe how access to operational databases is constrained and audited.
6. Explain what telemetry is enabled by default and how it can be disabled.
7. Provide recommended pilot and production hardware sizing.
8. Describe the network isolation model recommended for Azure and on-premises deployments.
9. Identify all logs generated and how they can be exported to the Agency.
10. State whether Agency data is ever used for vendor model improvement, training, or analytics.

## 11. Evaluation Criteria Suggestions

Possible scoring categories:

- security and privacy controls
- data residency and hosting flexibility
- quality of grounding and citation support
- auditability and oversight
- deployment simplicity
- interoperability with state identity and system-of-record patterns
- total cost of ownership
- documentation quality for technical and non-technical reviewers

## 12. Short Procurement Summary

If a short summary paragraph is needed, use:

`The Agency seeks a practical, secure, and governable AI solution for policy-grounded assistance. The solution should support deployment within state-controlled infrastructure, require citations to approved sources, prevent unrestricted access to operational systems, minimize external telemetry, and provide the documentation and controls necessary for technical, legal, privacy, and procurement review.`
