🎯 Additional Guidance: Designing Individual Entities (Entity vs. Property)

Entity design is one of the most critical yet subtle tasks in building and maintaining knowledge graphs. The line between “entities” and “properties” can seem blurry, so follow these principles to ensure clarity, coherence, and flexibility as your graph evolves.

## Defining Entities with Pydantic

Graphiti loads entity definitions as Pydantic models from your project’s
`ai/graph/entities` directory when a container starts. Each model should
inherit from `pydantic.BaseModel` and explicitly forbid unexpected fields so
the generated JSON schema sets `additionalProperties: false`.

```python
from pydantic import BaseModel, Field, ConfigDict

class Product(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Human‑readable name")
    category: str | None = Field(None, description="Type of product")
```

The `model_config` line prevents undeclared keys from being accepted and keeps
OpenAI’s `response_format` validation happy. Graphiti internally generates some
models dynamically; those are automatically patched to be strict, but static
classes like the one above must include this configuration. When you scaffold a
new entity with the Graphiti CLI, the generated file already includes this
`model_config` line so your project entities start out compliant.

🧩 What Makes an Entity?

An entity is typically a concept, object, or abstraction that:
	•	Has a distinct identity independent of its properties.
	•	Can be linked clearly to other entities through relationships (edges).
	•	Is meaningful enough that you would regularly search for, query directly, or relate to other entities.
	•	Could reasonably stand alone with its own descriptive attributes or metadata.

Examples:
	•	✅ Good entities: Candidate, Agent, Project, Resource, ContextBundle
	•	🚫 Not ideal entities (usually properties instead): Job title, Email, Phone number

🔖 What Makes a Property?

A property is usually an attribute or descriptor that:
	•	Does not have meaningful relationships on its own (typically).
	•	Is primarily useful as a piece of metadata or descriptive information within an entity.
	•	Would rarely, if ever, be directly queried or referenced independently without the context of an entity.

Examples:
	•	✅ Good properties: Email, Phone number, Location, Job title (inside a Candidate entity)
	•	🚫 Not ideal properties (usually entities instead): Agent, Project, Tool

⚖️ How to Decide: Entity vs. Property

Ask yourself these critical questions:

Question	Entity ✅	Property 🔖
Does it have a meaningful, independent existence?	Yes	No
Will I query/search this directly on its own?	Yes	No
Will it have significant relationships with other entities?	Yes	No
Would adding this improve discoverability in the graph?	Yes	No
Is it purely descriptive metadata of something else?	No	Yes

Use this table consistently for quick mental checks as you design your graph structure.

🌳 Guidelines for Creating Effective Entities

When defining new entities:
	•	Clear identity: Ensure it has a unique identifier or combination of attributes clearly distinguishing it from others.
	•	Structured metadata: Choose descriptive yet not overly granular properties. Balance detail with clarity.
	•	Consistent granularity: Keep entities at a similar “level” of abstraction across your graph to avoid confusion or redundancy.
	•	Relationships first: If something primarily exists to establish relationships (e.g., “Agent assigned to Project”), prefer creating explicit relationship edges rather than standalone entities.

📐 Pitfalls and Common Missteps

❌ Over-entitying:
Too many narrowly-defined entities (e.g., “Email entity”) leads to a fragmented graph that’s cumbersome to query. Prefer properties here.

❌ Property explosion:
Too many properties within a single entity make it difficult to use, extend, or maintain. Split overly complex entities into coherent sub-entities if needed.

✅ Recommended practice:
Prefer fewer, richly defined entities with carefully chosen properties over many thin, ambiguous entities.

🎨 Example (Good Entity Design): Candidate

class Candidate(BaseModel):
    name: str
    email: Optional[str]
    phone: Optional[str]
    linkedin_url: Optional[str]
    current_title: Optional[str]
    current_company: Optional[str]
    location: Optional[str]
    years_of_experience: Optional[int]
    summary: Optional[str]

	•	Entity clearly represents: A job candidate (distinct identity).
	•	Properties clearly represent: Contact information, descriptive metadata (email, phone).
	•	Avoided pitfalls:
	•	🚫 Separate entity for email or phone number
	•	🚫 Overloading single entity with unrelated info (e.g., job postings, company info)

🚦 Quick Checklist (Entity Creation)

When creating an entity, run through this quick checklist:
	1.	✅ Identity: Does it clearly stand alone?
	2.	✅ Relationships: Does it clearly link meaningfully to other entities?
	3.	✅ Searchability: Would you regularly search/query for it explicitly?
	4.	✅ Property vs. Entity Check: Have you double-checked your decision using the Entity vs. Property questions?

If you can confidently answer “Yes” to these, you have a well-formed entity.

⸻

🎯 Summary:
Careful and deliberate entity vs. property distinction directly affects the ease of querying, managing, and evolving your knowledge graph. Following these clear principles and quick-check guidelines ensures clarity, maintainability, and future flexibility as your meta-layer knowledge graph grows and evolves.