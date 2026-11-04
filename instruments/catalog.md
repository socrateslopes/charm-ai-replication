# Pattern catalog

Summary of patterns from *Cloud Application Architecture Patterns* (Brown, Woolf and Yoder, 2025), chapters 4, 5 and 6, in three groups. For each pattern: the problem it addresses, a summary, how it is usually implemented, and its benefits.

## Microservice Architecture Patterns

### Domain Microservice (aka Decompose by Business Capability)

*Problem: How should a set of microservices in an architecture provide the business functionality for an application?*

- **Summary:** A microservice that encapsulates a single business capability, implementing its functionality and exposing it via a Service API. It solves the challenge of modularizing a system by aligning the architecture with actual business domains rather than technical layers, preventing the creation of tightly coupled services or messy "Big Balls of Mud".
- **How it is usually implemented:** It is designed to be broad enough to perform complete business transactions using only the data it manages, avoiding dependency chaining with other services. It is implemented statelessly, persists its own data, and is often designed using domain-driven design (DDD) and Event Storming techniques.
- **Benefits:** It acts as an independent building block that can be developed, maintained, deployed, and reused by a small team without requiring an enterprise service bus (ESB) for integration.

### Adapter Microservice

*Problem: How can the application take advantage of existing functionality without abandoning the microservices approach?*

- **Summary:** A microservice that acts as a wrapper around an existing, external system of record to expose its capabilities through a modern, standardized Service API. This enables seamless integration with legacy systems or external services that otherwise have antiquated interfaces, outdated data formats, or incompatible protocols.
- **How it is usually implemented:** It contains little to no actual business domain logic; instead, its internal implementation consists of integration and translation logic that acts as a proxy, routing modern requests to the legacy system and translating the responses back.
- **Benefits:** It isolates the modern architecture from legacy API complexities while enabling automated data transformation and the seamless addition of modern quality-of-service features like caching and retries.

### Dispatcher (aka BFF)

*Problem: How can a client access a microservices application through a channel-specific service interface when the business functionality is spread across an evolving set of domain-specific APIs?*

- **Summary:** A specialized microservice that provides a single, unified API customized for a specific type of client, such as a web browser or mobile app. It solves the problem of client applications struggling to connect to a dynamic, constantly evolving web of multiple backend microservices.
- **How it is usually implemented:** It contains no business domain logic; instead, it delegates to backend microservices and performs routing, orchestration, data translation, and filtering. It is typically developed by the same team that builds the client application, often using the same language (e.g., Node.js for JavaScript web clients).
- **Benefits:** It isolates external clients from changes in the backend architecture, optimizes data payloads for specific devices, and provides a convenient layer for data caching.

### Polyglot Development

*Problem: What programming language(s) should be used for implementing microservices?*

- **Summary:** An architectural practice where different microservices within the same application can be implemented using different programming languages or technologies. It solves the constraints of monolithic applications where developers are forced to use a single, uniform language that may be a poor fit for specialized tasks.
- **How it is usually implemented:** Because each microservice runs in its own isolated process and communicates over universal protocols like REST, the internal language is completely abstracted away from the rest of the system. Teams embed their language runtime of choice inside the application package and avoid sharing code libraries between services.
- **Benefits:** It empowers teams to choose the most efficient tool for a specific problem (e.g., Python for machine learning, Node.js for web I/O) and allows developers to work in the languages they are most skilled in without causing system-wide library conflicts.

### Self-Managed Data Store (aka Database per Service)

*Problem: How does a microservice store its state?*

- **Summary:** A pattern where each stateful microservice persists its data in its own dedicated storage that it manages exclusively. It solves the severe coupling, performance bottlenecks, and fragility caused by multiple applications or modules sharing a single, centralized Database of Record (DoR).
- **How it is usually implemented:** Different microservices never share the same database; if one service needs another's data, it must request it via the owning service's API. It often utilizes "Polyglot Persistence," meaning the type of database (relational, NoSQL, etc.) is chosen based on what best fits the specific microservice's data format.
- **Benefits:** It ensures true independence by allowing teams to evolve their data schemas without breaking other services, isolates failures, and prevents cascading data corruption across the architecture.

### Service Orchestrator

*Problem: How does a microservice perform a complex task, one that is performed in multiple steps?*

- **Summary:** A microservice that performs a complex, multi-step task by coordinating and combining the capabilities of several simpler microservices. It solves the problem of maintaining data consistency and transaction-like behavior (ensuring all steps succeed, or none do) in a distributed cloud environment where traditional database transactions are unreliable or unavailable.
- **How it is usually implemented:** It can be implemented in three ways: as an orchestration microservice that only calls read-only or idempotent tasks; as a consolidated microservice that shares a single database session for all steps; or as a business process running in a BPM engine that handles retries and compensating transactions (reversing completed steps if a later step fails).
- **Benefits:** It enables the reliable execution of highly complex distributed business workflows, handling partial failures gracefully through retries and compensating actions without leaving the system in an inconsistent state.

## Microservices Design Patterns

### Model Around the Domain

*Problem: How can you encourage stakeholders to explain enough of the domain requirements in a way that reveals the relevant capabilities for the application you are building?*

- **Summary:** A technique to capture an application's requirements by bringing stakeholders together to describe the subject area using the natural language of the domain, known as Ubiquitous Language. This helps developers and domain experts acquire a shared understanding of the system's rules, entities, and relationships.
- **How it is usually implemented:** It is typically executed through informal, lightweight domain modeling sessions (like Event Storming) using whiteboards and sticky notes, intentionally avoiding technical jargon to focus entirely on understanding the business terminology.
- **Benefits:** It clarifies requirements, ensures the software closely aligns with real-world business capabilities, and provides a solid foundation for designing right-sized microservices.

### Event Storming

*Problem: How do you get the stakeholders to understand and describe the elements and events around the domain and subdomain?*

- **Summary:** A fast, lightweight, and nontechnical workshop where software developers and domain experts collaborate to brainstorm and elucidate the set of Domain Events that flow through a system. It reveals the boundaries of the system and describes the actions, commands, and aggregates within a subdomain.
- **How it is usually implemented:** Participants place colored sticky notes on a wide wall to map out a time-sequenced timeline of "facts" (Domain Events), followed by the commands that caused them, the actors involved, and the data aggregates they affect.
- **Benefits:** It quickly creates a shared common understanding of the domain model among all stakeholders, bridging the gap between technical and non-technical team members to clearly identify candidate boundaries for microservices.

### Domain Event

*Problem: How do you model those aspects of a design that correspond to things that happen during the various scenarios encountered by the system?*

- **Summary:** A representation of a fact or state change that has happened in the domain at a specific point in time, always expressed in the past tense (e.g., "Order placed"). It signals that something of interest occurred and can be used to trigger changes or actions in other parts of the system.
- **How it is usually implemented:** They are implemented using the technologies of the specific architecture (often an Event Backbone) and are published by the Bounded Context where the event occurred so that other subscribing Bounded Contexts can react asynchronously.
- **Benefits:** It significantly reduces coupling between different bounded contexts, allowing services to evolve independently while enabling high scalability and eventual consistency across the architecture.

### Bounded Context

*Problem: How do you clearly define the logical boundaries (edges) of a domain and subdomain(s) where particular terms and rules apply?*

- **Summary:** A logical boundary within a larger domain where a specific domain model, including its terms and rules (Ubiquitous Language), applies consistently. It groups related aspects of a subdomain, such as Domain Events, Aggregates, and behaviors, into a cohesive whole.
- **How it is usually implemented:** It typically maps directly to the boundaries of a microservice, ensuring that the encapsulated entities, values, and logic are strictly isolated and accessible only through its defined Application Service API.
- **Benefits:** It separates concerns by breaking a large, complex system into smaller, autonomous pieces with stable interfaces, preventing the muddying of concepts across different teams.

### Aggregate

*Problem: How do you tie together the groups of tightly related concepts and the values that belong within them in a subdomain?*

- **Summary:** A cluster of logically related domain objects, specifically entities and their associated Value Objects, that are treated as a single, cohesive conceptual unit. It defines a consistency boundary where the related objects either succeed or fail as a whole.
- **How it is usually implemented:** It is modeled around a main "Aggregate Root" entity that acts as the single API to access anything within it, and it is persisted or loaded from a database in its entirety through a Repository.
- **Benefits:** It guarantees transactional consistency, encapsulates domain objects to protect them from external changes, and supports the Single Responsibility principle by ensuring related business concepts are managed together.

### Domain Service

*Problem: How do you model those operations within a subdomain that do not belong to a specific Entity or Aggregate?*

- **Summary:** A standalone, stateless interface used to model business operations or rules that do not naturally belong to a specific entity or Value Object. It orchestrates domain logic that spans across multiple entities within the same Bounded Context.
- **How it is usually implemented:** It is implemented using the system's programming language (e.g., a Java class) as part of the domain layer and is never accessed directly from outside the Bounded Context; instead, it is invoked by Application Services or Domain Events.
- **Benefits:** It keeps core domain entities clean and loosely coupled by preventing them from being overloaded with responsibilities that fall outside their strict boundaries.

### Anti-Corruption Layer

*Problem: How can we design the system so that the Bounded Contexts (BCs) can interact without being tightly coupled together?*

- **Summary:** An isolation layer that mediates interactions between different Bounded Contexts or external legacy systems with incompatible domain models. It ensures that the semantics of one system do not "corrupt" or tightly couple with the clean semantics of the protected system.
- **How it is usually implemented:** It contains translation, filtering, and validation logic (often acting as an Adapter, Facade, or Proxy) rather than business logic, serving as the "glue-code" between systems.
- **Benefits:** It preserves the design integrity of core components and allows interacting systems to evolve independently without forcing them to share a common, rigid model.

### Repositories

*Problem: How do you mediate between an Aggregate’s entities and the persistent storage for their values?*

- **Summary:** An abstraction that mediates between the domain Aggregates and the underlying persistent storage mechanisms (like databases). It provides an in-memory abstraction of all the entities and values that make up an Aggregate.
- **How it is usually implemented:** It provides an interface with methods to add, remove, and query objects based on criteria, keeping database connection and transaction details strictly out of the domain objects.
- **Benefits:** It loosely couples the domain model from the persistence mechanism, allowing the application to work with simple data abstractions without worrying about database infrastructure.

### Application Services

*Problem: How can you protect the internals of a bounded context?*

- **Summary:** The top-level interface or API that exposes the functionality of a Bounded Context to external clients or other systems. It acts as a coordinator for calls to the domain elements inside the Bounded Context.
- **How it is usually implemented:** It contains no domain-specific business logic itself; instead, it delegates operations to Aggregates and Domain Services while handling cross-cutting concerns like transactions, access control, and logging.
- **Benefits:** It strictly controls access to the internal domain model, protecting the Aggregates from direct external manipulation while providing a stable, segregated interface for clients.

### Context Map

*Problem: How do you understand the relationships and boundaries between different domains within a complex system?*

- **Summary:** A visual map that captures and defines the technical and organizational relationships and boundaries between different Bounded Contexts.
- **How it is usually implemented:** It is drawn collaboratively by domain experts and technical teams, labeling the connections based on how Domain Events trigger communication between the various contexts, intentionally avoiding deep technical details.
- **Benefits:** It provides a comprehensive, high-level view of the entire system's architecture, helping teams easily understand inter-dependencies and appropriately assign organizational responsibilities.

## Event-driven Architecture Patterns

### Event Choreography

*Problem: When a change occurs in one component, how can a variable number of other components react accordingly?*

- **Summary:** An architectural approach where components coordinate by independently reacting to events rather than relying on a central orchestrator. It solves the problem of tightly coupled systems by allowing multiple components to react to a single change at their own pace and in their own way, avoiding the rigidity and single points of failure found in centralized Service Orchestration.
- **How it is usually implemented:** It uses a generic API (Event Notification) where components announce changes as events on an Event Backbone. Components act as "Event Notifiers" or "Reactive Components," communicating indirectly over topics without needing to know the location or readiness of the other components.
- **Benefits:** It provides extreme loose coupling and separation of time and space, allowing teams to add new features seamlessly by adding new subscribers. It also vastly improves system scalability, throughput, and availability since threads are never blocked waiting for synchronous responses.

### Event

*Problem: How do you represent a change in one component to be communicated to other components?*

- **Summary:** A minimal data package representing a fact, state change, or an interesting occurrence within a system. It solves the problem of communicating changes to the rest of the architecture without breaking encapsulation or exposing the internal implementation details of the component that changed.
- **How it is usually implemented:** It is transmitted as a message over an Event Backbone. It typically contains just enough information to identify the type of event, its cause, and the source component. To keep coupling low, large data payloads are avoided; instead, a key or reference is passed so interested components can fetch details via a Service API if needed.
- **Benefits:** It enables a "fire and forget" communication model where publishers do not need to wait for downstream processes, allowing parts of the system to scale entirely independently.

### Reactive Component

*Problem: How can you construct an application that can react to events?*

- **Summary:** A component that listens for specific events from an Event Backbone and decides independently if and how to react to them. It solves the problem of monolithic branching logic (complex if/then statements) by allowing different parts of a system to respond to the same external stimuli in completely different ways.
- **How it is usually implemented:** Usually implemented as a Microservice that subscribes to one or more event topics. It parses incoming events, filters out what it doesn't care about, and executes logic for the rest. Because it may receive duplicate events in a distributed system, it must be implemented as an "Idempotent Receiver" (where processing the same event multiple times produces the same safe result).
- **Benefits:** It makes the system highly extensible, as new behaviors and features can be introduced by simply adding a new Reactive Component to listen to an existing event, requiring zero changes to the rest of the system.

### Event API

*Problem: How can the reactive components in an event-driven architecture know what events to expect?*

- **Summary:** A formal contract that describes the set of topics and the exact format of the Event Messages flowing through an Event-Driven Architecture. It solves the problem of miscommunication between decoupled publishers and subscribers who need to agree on how to parse and interpret asynchronous messages without having a direct, hardcoded Service API.
- **How it is usually implemented:** It is documented and managed using standardized specifications like AsyncAPI (similar to OpenAPI for REST services), which define the channels, their purposes, and the JSON payload structures for every event.
- **Benefits:** It creates a clear, standardized agreement that prevents integration errors, enables independent teams to build compatible components, and allows for automated tooling and code validation.

### Event Notifier

*Problem: How and when should a component announce changes to other components?*

- **Summary:** A component that detects its own internal state changes and announces them to the rest of the system as events. It solves the problem of notifying other components about crucial occurrences without needing to know who is listening, how many listeners there are, or what they will do with the information.
- **How it is usually implemented:** It acts as a publisher, sending formatted event messages to specific topics on an Event Backbone whenever a significant Domain Event (or business milestone) occurs. A single Microservice frequently acts as both an Event Notifier and a Reactive Component.
- **Benefits:** It preserves strict boundaries and loose coupling, allowing the notifying component to evolve completely independently from the downstream components that consume its data.

### Event Backbone

*Problem: How can reactive components receive the events they are interested in without being coupled directly to the event notifiers that generate the events?*

- **Summary:** A centralized messaging infrastructure that connects Event Notifiers to Reactive Components. It solves the problem of routing events from producers to consumers asynchronously, separating them in both time and space so they don't have to know each other's physical locations or be active simultaneously.
- **How it is usually implemented:** It is typically implemented using event-style messaging systems (like Apache Kafka or Amazon EventBridge) or MQ-style messaging systems (like RabbitMQ). It hosts publish-subscribe topics to distribute a single event notification to multiple different listeners safely.
- **Benefits:** It decouples components geographically and temporally, provides reliable event distribution, and handles the heavy lifting of routing, allowing the microservices themselves to remain simple and focused.

### Event Sourcing

*Problem: As an application’s state changes constantly and unpredictably due to evolving conditions, how can you audit the history that created the current state?*

- **Summary:** A pattern where a system records the complete, append-only history of events it receives to represent its current state, rather than just storing a static snapshot of the latest data. It solves the problem of auditing complex processes, recovering from failures, or undoing actions when a simple point-in-time database snapshot is insufficient.
- **How it is usually implemented:** The system persists an ordered log of every event. To reconstruct the current state, the system starts from a baseline (or a recent "checkpoint") and replays the events sequentially. If a mistake was made in the past, new compensating events can be appended to correct the sequence.
- **Benefits:** It provides a flawless forensic audit trail, allows developers to query historical states ("time travel"), and enables powerful capabilities to simulate changes or cleanly recover from errors by replaying corrected event streams.
