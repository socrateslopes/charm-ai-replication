# System context

The system under study is the Payments System of a large online real
estate company operating in Latin America. It handles the money that flows
between tenants, landlords, real estate agents, the company and other
parties, and it is organized in two domains:

- **Pay In:** payments made by customers to the company (for example, rent,
  using payment slips, instant payments and credit cards).
- **Pay Out:** disbursements made by the company to third parties (for
  example, rent transfers to landlords and commissions).

Both domains execute high volumes of monetary transactions, with predictable
peaks at specific days of the month, and have strict requirements on
availability, data consistency and transactional correctness. Both integrate
with internal services of other teams and with external financial
institutions and payment providers.

The scope of this assessment is the five services described in
`services.md`, together with their module components (workers and
schedulers deployed with them). Everything else is external. The
characterization reflects the system as of March 2026.
