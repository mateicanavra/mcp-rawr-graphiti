import os
import pydantic

# Ensure server imports treat environment as development
os.environ.setdefault('GRAPHITI_ENV', 'development')

# Importing graphiti_mcp_server applies the create_model patch
import graphiti_mcp_server  # noqa: F401


def test_create_model_additional_properties_false():
    model = pydantic.create_model('MyModel', foo=(int, ...))
    schema = model.model_json_schema()
    assert schema.get('additionalProperties') is False
