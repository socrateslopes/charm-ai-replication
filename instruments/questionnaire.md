# Service characterization questionnaire

The following data collection questionnaire is used to obtain information
from services as part of an architecture characterization process.

**Q1.** What is the service name?

**Q2.** What are the main responsibilities of this service? Describe with
two or three sentences what this service does.

**Q3.** What is the name of each endpoint (operation) exposed by this
service? What are the names of the services that invoke each endpoint of
this service?

| Endpoint | Consumed by |
|---|---|

**Q4.** What are the endpoints synchronously called by this service?

| Endpoint | Service Name/Provider |
|---|---|

**Q5.** What is the label of each topic published by this service in a
message queue? What are the names of the services that consume messages
produced by this service?

| Topic published to | Consumed by |
|---|---|

**Q6.** What is the label of each topic consumed by this service from a
message queue? What are the names of the source services that publish
messages consumed by this service?

| Topic consumed from | Produced by |
|---|---|

**Q7.** What is the name of each data source accessed by this service? What
is the type (NoSQL, relational database, search engine, spreadsheet, file,
etc.) of each data source accessed by this service? What role (principal,
cache) does each data source play in this service? What type of action
(read, write, read/write) does this service perform on each data source it
accesses? Are any of those data sources shared among other services? If
yes, what are the names of those services that share each data source?

| Name | Type | Role | Actions | Shared by |
|---|---|---|---|---|

**Q8.** Must this service be deployed together with other services (i.e.,
does this service have deployment dependencies)? If yes, what are the names
of the services that must be deployed together with it?

| Service name | Why is a dependency? |
|---|---|

**Q9.** Is this service part of a module (i.e., are there other services
deployed together as a single unit like workers or any other thing)? If
yes, list the names of other services that are part of the same module with
a short description of them.

| Service name | What does it do? |
|---|---|

**Q10.** What are your overall thoughts about this service? What do you
consider it does right and what are some parts that seem to need
improvement? Provide as much detail as you can.

**Q11.** Do you have any other comments about an important service
characteristic not addressed in the previous questions?
