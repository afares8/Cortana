from typing import List, Optional, Dict, Any
import json
import logging

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    logging.warning("PyYAML not available. YAML import/export functionality will be limited.")

from app.db.base import InMemoryDB
from app.modules.admin.templates.models import DepartmentTemplate
from app.modules.admin.departments.services import create_department
from app.modules.admin.roles.services import create_role
from app.modules.admin.functions.services import create_function
from app.modules.ai.services import create_ai_profile

templates_db = InMemoryDB[DepartmentTemplate](DepartmentTemplate)

def create_template(template_data: Dict[str, Any]) -> DepartmentTemplate:
    """Create a new department template."""
    return templates_db.create(obj_in=DepartmentTemplate(**template_data))

def get_template(template_id: int) -> Optional[DepartmentTemplate]:
    """Get a department template by ID."""
    return templates_db.get(id=template_id)

def get_templates(
    skip: int = 0, 
    limit: int = 100, 
    filters: Optional[Dict[str, Any]] = None
) -> List[DepartmentTemplate]:
    """Get department templates with optional filtering."""
    return templates_db.get_multi(skip=skip, limit=limit, filters=filters)

def update_template(template_id: int, template_data: Dict[str, Any]) -> Optional[DepartmentTemplate]:
    """Update a department template."""
    return templates_db.update(id=template_id, obj_in=DepartmentTemplate(**template_data))

def delete_template(template_id: int) -> bool:
    """Delete a department template."""
    template = templates_db.remove(id=template_id)
    return template is not None

def create_department_from_template(
    template_id: int,
    department_name: str,
    company_id: str,
    country: str,
    timezone: str,
    customize: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a new department from a template."""
    template = get_template(template_id)
    if not template:
        raise ValueError(f"Template with ID {template_id} not found")
    
    department_data = {
        "name": department_name,
        "type": customize.get("type", "standard") if customize else "standard",
        "ai_enabled": customize.get("ai_enabled", True) if customize else True,
        "country": country,
        "timezone": timezone,
        "company_id": company_id
    }
    
    department = create_department(department_data)
    
    created_roles = []
    for role_data in template.roles.get("items", []):
        role = create_role({
            "name": role_data.get("name"),
            "description": role_data.get("description", ""),
            "department_id": department.id,
            "permissions": role_data.get("permissions", [])
        })
        created_roles.append(role)
    
    created_functions = []
    for function_data in template.functions.get("items", []):
        function = create_function({
            "name": function_data.get("name"),
            "description": function_data.get("description", ""),
            "input_schema": function_data.get("input_schema", {}),
            "output_schema": function_data.get("output_schema", {}),
            "department_id": department.id
        })
        created_functions.append(function)
    
    ai_profile = None
    if template.ai_profile:
        ai_profile_data = template.ai_profile
        ai_profile = create_ai_profile({
            "name": ai_profile_data.get("name", f"{department_name} AI Profile"),
            "model": ai_profile_data.get("model", "mistral-7b"),
            "embedding_id": ai_profile_data.get("embedding_id", "default"),
            "temperature": ai_profile_data.get("temperature", 0.7),
            "top_p": ai_profile_data.get("top_p", 0.95),
            "context_type": ai_profile_data.get("context_type", "standard"),
            "department_id": department.id
        })
    
    return {
        "department": department,
        "roles": created_roles,
        "functions": created_functions,
        "ai_profile": ai_profile
    }

def export_template_to_json(template_id: int) -> str:
    """Export a template to JSON format."""
    template = get_template(template_id)
    if not template:
        raise ValueError(f"Template with ID {template_id} not found")
    
    return json.dumps(template.model_dump(), indent=2)

def export_template_to_yaml(template_id: int) -> str:
    """Export a template to YAML format."""
    if not YAML_AVAILABLE:
        raise NotImplementedError("YAML functionality is not available. Please install PyYAML package.")
        
    template = get_template(template_id)
    if not template:
        raise ValueError(f"Template with ID {template_id} not found")
    
    return yaml.dump(template.model_dump(), sort_keys=False)

def import_template_from_json(json_data: str) -> DepartmentTemplate:
    """Import a template from JSON format."""
    template_data = json.loads(json_data)
    return create_template(template_data)

def import_template_from_yaml(yaml_data: str) -> DepartmentTemplate:
    """Import a template from YAML format."""
    if not YAML_AVAILABLE:
        raise NotImplementedError("YAML functionality is not available. Please install PyYAML package.")
        
    template_data = yaml.safe_load(yaml_data)
    return create_template(template_data)
