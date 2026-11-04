# Check 3: are the patterns the agents added really in the system?

Both B conditions reported patterns that no participant named. The protocol
(Section 9.2) asks the researcher to check each one against the code and
classify it as **supported** or **unsupported**. The agents in Task B never
saw the code; they inferred these patterns from the characterization, the
service descriptions and, in B1, the developers' comments.

For each pattern: read the catalog definition, look at the places listed
under "Where to look" (the Task A results already point to them), and fill in
the three lines at the end. "Partly" is fine when only some of the listed
services have it.

---

## 1. Event Backbone (B0 and B1; all five services)

*Later added to the answer key (one participant, P1): protocol Section 11, deviation 12.*

**Catalog:** a centralized messaging infrastructure (e.g., Kafka, an MQ
system) that connects Event Notifiers to Reactive Components through
publish-subscribe topics.

**What the agents said:** every service publishes topics or queues that
others consume, so there must be shared messaging infrastructure; Payout
Processor states Kafka and SQS explicitly.

**Where to look:** code locations in the Task A results (not public).

- Verdict (supported / partly / unsupported): partly
- Services where it holds: all five
- Note: Kafka have a confluent instance managed by another team, while SQS/SNS are availble inside AWS but managed by the team that owns each service.

## 2. Domain Event (B0: payout-processor, payin-processor, bank-interface, agents-commissions; B1: payout-processor, agents-commissions)

**Catalog:** a fact that happened in the domain, named in the past tense
("Order placed"), published by the bounded context where it occurred so that
others can react.

**What the agents said:** payout-processor publishes state changes through a
transactional outbox; agents-commissions's names mix past-tense facts with
command-like names; the other services' payloads were not visible.

**Where to look:** code locations in the Task A results (not public).

Note for the paper: participants named the catalog's **Event** pattern
(2 participants), not Domain Event. Say whether, in your judgment, they meant
the same thing.

- Verdict (supported / partly / unsupported): partly
- Services where it holds: all of the listed
- Same as the "Event" participants named? (yes / no): yes
- Note: Despite some names withhold the definition of a Domain service, using past tense, those systems were not designed with this design pattern in mind. It was more of a good design choice rooted at develoepers experience, rather than a formal pattern selection. It is als explained by the inconsistency in naming (some are past tense, some not).

## 3. Service Orchestrator (B0: payout-processor; B1: payout-processor, bank-interface)

**Catalog:** a microservice that performs a multi-step task by coordinating
other services, keeping transaction-like behavior through idempotent steps,
a shared session, or a process engine with retries and compensating
transactions.

**What the agents said:** payout-processor runs a multi-step lifecycle (create,
approve, submit to bank) across Bank Interface, the ledger and the ERP gateway, with
auto-approval and auto-send; no evidence of compensation, so "partial".

**Where to look:** code locations in the Task A results (not public).

- Verdict (supported / partly / unsupported): supported
- Services where it holds: both
- Note: Both services are responsible for orchestrating payments, including processing the request, send to external services, send the reconciliation info to SAP and other services.

## 4. Application Services (B1 only: agents-commissions, payout-processor)

**Catalog:** the top-level API of a bounded context; it holds no domain
logic and delegates to aggregates and domain services, handling transactions,
access control and logging.

**What the agents said:** agents-commissions keeps controllers thin and delegates to
"application commands" over a pure domain layer; payout-processor keeps logic
in a core behind ports (hexagonal), with idempotency, rate limiting and
error handling at the API.

**Where to look:** code locations in the Task A results (not public).

- Verdict (supported / partly / unsupported): unsupported
- Services where it holds: none
- Note: agents-commissions acts as a billing system that receives payments requests and forwards it to multiple paths, orchestrating the payment. payout-processor does the same, but acts as a single point of entry to payment orders, then follows it to the banks and records payments compensation in other systems.
  Revised 2026-10-03: their APIs are not thin layers over a domain layer; both act as Service Orchestrators, so Application Services is unsupported.

## 5. Bounded Context (B1 only: all five services)

**Catalog:** a logical boundary where one domain model and its language apply
consistently; usually maps to a microservice and is accessed only through its
application service API.

**What the agents said:** each service encapsulates its model and data, but
"payment request" and "payment order" are used by agents-commissions, payout-processor
and bank-interface without explicit context definitions, so "partial".

**Where to look:** code locations in the Task A results (not public).

- Verdict (supported / partly / unsupported): unsupported
- Services where it holds: none
- Note: despite some services might present this behavior, they are more due to good design choices rather than explicit domain definition and a bounded context setting. overall, developers chose to keep the domain concise but explicit bounded context decisions were not made.
