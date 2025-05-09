from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query, UploadFile, File, Form
from fastapi.responses import JSONResponse, PlainTextResponse
from uuid import UUID

from app.core.config import settings
from app.modules.admin.templates.schemas import (
    DepartmentTemplateCreate, DepartmentTemplateUpdate, DepartmentTemplateOut,
    DepartmentFromTemplateRequest
)
from app.modules.admin.templates.services import (
    create_template, get_template, get_templates, update_template, delete_template,
    create_department_from_template, export_template_to_json, export_template_to_yaml,
    import_template_from_json, import_template_from_yaml
)

router = APIRouter()

@router.post("", response_model=DepartmentTemplateOut, status_code=201)
async def create_template_endpoint(template: DepartmentTemplateCreate):
    """Create a new department template."""
    return create_template(template.model_dump())

@router.get("", response_model=List[DepartmentTemplateOut])
async def get_templates_endpoint(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None
):
    """Get all department templates with optional filtering."""
    filters = {}
    if name:
        filters["name"] = name
    
    return get_templates(skip=skip, limit=limit, filters=filters)

@router.get("/{template_id}", response_model=DepartmentTemplateOut)
async def get_template_endpoint(template_id: int = Path(...)):
    """Get a department template by ID."""
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Department template not found")
    return template

@router.put("/{template_id}", response_model=DepartmentTemplateOut)
async def update_template_endpoint(
    template_update: DepartmentTemplateUpdate,
    template_id: int = Path(...)
):
    """Update a department template."""
    template = update_template(template_id, template_update.model_dump(exclude_unset=True))
    if not template:
        raise HTTPException(status_code=404, detail="Department template not found")
    return template

@router.delete("/{template_id}", response_model=dict)
async def delete_template_endpoint(template_id: int = Path(...)):
    """Delete a department template."""
    success = delete_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Department template not found")
    return {"success": True}

@router.post("/from-template", status_code=201)
async def create_department_from_template_endpoint(request: DepartmentFromTemplateRequest):
    """Create a new department from a template."""
    try:
        result = create_department_from_template(
            template_id=request.template_id,
            department_name=request.department_name,
            company_id=request.company_id,
            country=request.country,
            timezone=request.timezone,
            customize=request.customize
        )
        return {
            "success": True,
            "department_id": result["department"].id,
            "roles_created": len(result["roles"]),
            "functions_created": len(result["functions"]),
            "ai_profile_created": result["ai_profile"] is not None
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating department from template: {str(e)}")

@router.get("/{template_id}/export", response_class=JSONResponse)
async def export_template_endpoint(
    template_id: int = Path(...),
    format: str = Query("json", description="Export format: json or yaml")
):
    """Export a department template in JSON or YAML format."""
    try:
        if format.lower() == "json":
            json_data = export_template_to_json(template_id)
            return JSONResponse(content=json_data)
        elif format.lower() == "yaml":
            yaml_data = export_template_to_yaml(template_id)
            return PlainTextResponse(content=yaml_data, media_type="application/x-yaml")
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use 'json' or 'yaml'")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting template: {str(e)}")

@router.post("/import", response_model=DepartmentTemplateOut)
async def import_template_endpoint(
    file: UploadFile = File(...),
    format: str = Form("json", description="Import format: json or yaml")
):
    """Import a department template from a JSON or YAML file."""
    try:
        content = await file.read()
        content_str = content.decode("utf-8")
        
        if format.lower() == "json":
            template = import_template_from_json(content_str)
        elif format.lower() == "yaml":
            template = import_template_from_yaml(content_str)
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use 'json' or 'yaml'")
        
        return template
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid template format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing template: {str(e)}")
