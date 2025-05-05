from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query
from pydantic import EmailStr

from app.services.tasks.models.task import Task
from app.services.tasks.schemas.task import TaskCreate, TaskUpdate
from app.services.tasks.services.task_service import task_service

router = APIRouter()

@router.post("/", response_model=Task, status_code=201)
async def create_task_endpoint(task: TaskCreate):
    """Create a new task."""
    return await task_service.create_task(task)

@router.get("/", response_model=List[Task])
async def get_tasks_endpoint(
    skip: int = 0,
    limit: int = 100,
    assigned_to: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    related_contract_id: Optional[int] = None,
    related_client_id: Optional[int] = None,
    due_date_before: Optional[datetime] = None,
    ai_generated: Optional[bool] = None
):
    """Get tasks with optional filtering."""
    filters = {}
    if assigned_to:
        filters["assigned_to"] = assigned_to
    if status:
        filters["status"] = status
    if priority:
        filters["priority"] = priority
    if related_contract_id:
        filters["related_contract_id"] = related_contract_id
    if related_client_id:
        filters["related_client_id"] = related_client_id
    if ai_generated is not None:
        filters["ai_generated"] = ai_generated
    
    tasks = await task_service.get_tasks(skip=skip, limit=limit, filters=filters)
    
    if due_date_before:
        filtered_tasks = []
        for task in tasks:
            if task.due_date and task.due_date > due_date_before:
                continue
            filtered_tasks.append(task)
        return filtered_tasks
    
    return tasks

@router.get("/{task_id}", response_model=Task)
async def get_task_endpoint(task_id: int = Path(..., gt=0)):
    """Get a task by ID."""
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=Task)
async def update_task_endpoint(
    task_id: int = Path(..., gt=0),
    task_update: TaskUpdate = Body(...)
):
    """Update a task."""
    task = await task_service.update_task(task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}", response_model=Dict[str, bool])
async def delete_task_endpoint(task_id: int = Path(..., gt=0)):
    """Delete a task."""
    result = await task_service.delete_task(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True}
