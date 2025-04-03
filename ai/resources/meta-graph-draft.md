# Meta Knowledge Graph Entity Definitions

## Directory Structure

```
entities/
├── actions/
│   └── procedure.py
├── constraints/
│   └── requirement.py
├── interaction/
│   ├── interaction_model.py
│   ├── preference.py
│   └── feedback.py
├── connectors/
│   ├── agent.py
│   ├── project.py
│   ├── resource.py
│   ├── goal.py
│   ├── developer.py
│   └── context_bundle.py
└── resources/
    ├── documentation.py
    ├── artifact.py
    └── tool.py
```

---

## Entity Definitions

### Actions: Procedure

```python
from pydantic import BaseModel, Field

class Procedure(BaseModel):
    """Defines actionable steps or procedures to be executed.

    Instructions for identifying and extracting procedures:
    1. Look for clearly defined steps or instructions.
    2. Ensure each step logically follows from the previous one.
    3. Capture explicit descriptions of each step.
    """

    name: str = Field(..., description="Name of the procedure.")
    description: str = Field(..., description="Detailed steps or actions to perform.")
```

---

### Constraints: Requirement

```python
from pydantic import BaseModel, Field

class Requirement(BaseModel):
    """Defines constraints, conditions, or requirements that must be satisfied.

    Instructions for identifying and extracting requirements:
    1. Identify clearly stated constraints or prerequisites.
    2. Include rationale or importance if explicitly mentioned.
    """

    name: str = Field(..., description="Requirement identifier.")
    description: str = Field(..., description="Description of the requirement or constraint.")
```

---

### Interaction: Interaction Model

```python
from pydantic import BaseModel, Field

class InteractionModel(BaseModel):
    """Describes structured interaction patterns.

    Instructions for identifying and extracting interaction models:
    1. Look for explicit guidelines on interaction sequences.
    2. Include steps or patterns explicitly mentioned.
    """

    name: str = Field(..., description="Name of interaction pattern or model.")
    description: str = Field(..., description="How interactions typically occur.")
```

---

### Interaction: Preference

```python
from pydantic import BaseModel, Field

class Preference(BaseModel):
    """A user's expressed likes, dislikes, or preferences.

    Instructions for identifying and extracting preferences:
    1. Explicit statements of preference.
    2. Comparative statements ("I prefer X over Y").
    3. Clearly categorize by domain (e.g., food, music).
    """

    category: str = Field(..., description="The category of the preference.")
    description: str = Field(..., description="Brief description based only on provided context.")
```

---

### Interaction: Feedback

```python
from pydantic import BaseModel, Field

class Feedback(BaseModel):
    """User feedback on actions or recommendations.

    Instructions for identifying and extracting feedback:
    1. Explicit responses or evaluations provided by users.
    2. Include context or specific details from the feedback.
    """

    context: str = Field(..., description="Context or action the feedback relates to.")
    response: str = Field(..., description="Detail of user's feedback.")
```

---

### Connectors: Agent

```python
from pydantic import BaseModel, Field

class Agent(BaseModel):
    """Represents an AI agent persona or role.

    Instructions for identifying and extracting agents:
    1. Explicitly named roles or personas.
    2. Clearly stated skills, expertise, or responsibilities.
    """

    name: str = Field(..., description="Agent's name.")
    description: str = Field(..., description="Summary of agent's role and skills.")
```

---

### Connectors: Project

```python
from pydantic import BaseModel, Field

class Project(BaseModel):
    """Represents a project or initiative.

    Instructions for identifying and extracting projects:
    1. Named initiatives with clear scope and objectives.
    """

    name: str = Field(..., description="Project name.")
    description: str = Field(..., description="Project scope and objectives.")
```

---

### Connectors: Resource

```python
from pydantic import BaseModel, Field

class Resource(BaseModel):
    """Assets or resources utilized by agents or projects.

    Instructions for identifying and extracting resources:
    1. Specific tools, datasets, or other assets mentioned explicitly.
    """

    name: str = Field(..., description="Resource name.")
    description: str = Field(..., description="Description of the resource.")
```

---

### Connectors: Goal

```python
from pydantic import BaseModel, Field

class Goal(BaseModel):
    """Clearly stated objectives or goals.

    Instructions for identifying and extracting goals:
    1. Explicit statements of objectives or desired outcomes.
    2. Success indicators or measurable outcomes explicitly mentioned.
    """

    statement: str = Field(..., description="Clear statement of goal or objective.")
    success_indicators: str = Field(..., description="Indicators of successful achievement.")
```

---

### Connectors: Developer

```python
from pydantic import BaseModel, Field

class Developer(BaseModel):
    """Developer-specific working style and context.

    Instructions for identifying and extracting developer context:
    1. Explicit statements about developer working style or patterns.
    """

    name: str = Field(..., description="Developer's name.")
    working_style: str = Field(..., description="Developer's work patterns and habits.")
```

---

### Connectors: ContextBundle

```python
from pydantic import BaseModel, Field

class ContextBundle(BaseModel):
    """Aggregates contextual information or episodes.

    Instructions for identifying and extracting context bundles:
    1. Explicit bundles of historical context or related information.
    """

    name: str = Field(..., description="Context bundle name.")
    description: str = Field(..., description="Overview of contextual information.")
```

---

### Resources: Documentation

```python
from pydantic import BaseModel, Field

class Documentation(BaseModel):
    """Reference materials or documentation resources.

    Instructions for identifying and extracting documentation:
    1. Explicit titles or references to documentation.
    """

    title: str = Field(..., description="Title of documentation.")
    link: str = Field(..., description="Link to documentation.")
```

---

### Resources: Artifact

```python
from pydantic import BaseModel, Field

class Artifact(BaseModel):
    """Outputs or artifacts from work activities.

    Instructions for identifying and extracting artifacts:
    1. Explicit mentions of created outputs or artifacts.
    2. Include type and location clearly mentioned.
    """

    name: str = Field(..., description="Artifact name.")
    type: str = Field(..., description="Artifact type.")
    location: str = Field(..., description="Artifact location.")
```

---

### Resources: Tool

```python
from pydantic import BaseModel, Field

class Tool(BaseModel):
    """Tools used by agents or developers.

    Instructions for identifying and extracting tools:
    1. Explicit mentions of specific tools used.
    2. Clearly described functionality or usage contexts.
    """

    name: str = Field(..., description="Tool name.")
    description: str = Field(..., description="Tool usage context and purpose.")
```