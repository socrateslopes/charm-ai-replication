# How to read the characterization tables

The characterization covers the five in-scope services. **Internal** means
the five in-scope services and their own module components (workers,
schedulers). **External** means everything else: services of other teams of
the same company and systems of other companies.

## sync.csv: Synchronous Coupling and Size

- Rows are request senders; columns are request receivers.
- A cell is the number of distinct operations (endpoints) of the receiver
  that the sender invokes synchronously.
- The diagonal cell of an in-scope service is the number of operations it
  exposes. This is the **Size** dimension.
- Column "Depends on (internal)" / "Depends on (external)": the number of
  distinct internal / external services that the row service invokes.
- Row "Important to (internal)" / "Important to (external)": the number of
  distinct internal / external services that invoke the column service.

## async.csv: Asynchronous Coupling

- Rows are publishers; columns are subscribers.
- A cell is the number of distinct topics or queues of the publisher that
  the subscriber consumes.
- The diagonal cell of an in-scope service is the number of distinct topics
  or queues it publishes. A note such as "15 3 self" means 15 topics
  published, 3 of which are consumed by the service itself.
- Column "Important to (internal)" / "Important to (external)": the number
  of distinct internal / external subscribers of the row service.
- Row "Depends on (internal)" / "Depends on (external)": the number of
  distinct internal / external publishers the column service consumes from.

## databases.csv: Data Source Coupling

- Rows are data sources; columns are in-scope services.
- A cell is the action the service performs on the data source (Read,
  Write, Read/Write).
- The last column is the number of services (in scope or not) that share
  the data source.
