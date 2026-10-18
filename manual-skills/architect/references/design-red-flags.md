# Design red flags

Screen every candidate before synthesis. A red flag is a reason to revise or reject the shape.

## Shallow module

A shallow module exposes a large interface while hiding little complexity. Judge depth by the capability and policy hidden behind the public surface relative to the size of that surface. Prefer a simple interface backed by substantial behavior.

Do not confuse a deep module with a deep call chain. A deep call chain scatters understanding across layers. A deep module concentrates capability behind one interface.

Look for these signs:

- Callers coordinate several methods to complete one operation.
- Public options expose internal stages or implementation choices.
- Learning the interface does not save the caller from learning the implementation.

## Information leakage

Information leakage makes multiple modules depend on the same internal decision. A representation, policy, or protocol detail appears in more than one place, so changing it requires coordinated edits.

Public re-exports of transport or wire types are leakage. Parse external data into domain types behind the interface. Keep storage schemas, framework objects, and protocol details private.

## Temporal decomposition

Temporal decomposition organizes modules by execution order instead of the knowledge they own. Separate load, validate, transform, and save stages often repeat one representation and its invariants across several boundaries.

Group code around domain knowledge and ownership. Methods that run at different times can still belong to one module when they protect the same decisions.

## Pass-through method

A pass-through method forwards the same arguments to another method with the same shape. It adds a layer without hiding complexity.

Remove it or move responsibility to the module that can complete the operation. Keep a forwarding boundary only when it adds policy, adaptation, or a distinct abstraction.

## Split ownership

When two modules both write the same piece of state, neither fully owns it. Updates require coordinating both writers. Assign one authoritative owner and make the other module request changes through that owner's interface.

## Two ways to do one task

When the codebase offers two mechanisms for the same operation, contributors pick whichever they find first. Over time both paths accumulate call sites. Keep one canonical path and remove or deprecate the other.

## Importable internals

When internal helpers, private types, or implementation details can be imported from outside the owning module, callers couple to decisions that were not meant to be public. Restrict visibility so only the intended interface is reachable.

## Hand-synced list

When adding a new variant requires updating a list in a separate file — a registry, a switch statement, a config array — contributors forget the second edit. Co-locate the registration with the definition, or generate the list from source so omissions fail the build.
