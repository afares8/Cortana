from typing import List, Optional, Dict, Any
from app.services.tasks.models.task import Task
from app.services.tasks.schemas.task import TaskCreate, TaskUpdate

class TasksServiceInterface:
    """
    Interface for task operations.
    """
    
    async def create_task(self, task_data: TaskCreate) -> Task:
        """
        Create a new task.
        """
        pass
    
    async def get_tasks(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Task]:
        """
        Get tasks with optional filtering.
        """
        pass
    
    async def get_task(self, task_id: int) -> Optional[Task]:
        """
        Get a task by ID.
        """
        pass
    
    async def update_task(
        self,
        task_id: int,
        task_data: TaskUpdate
    ) -> Optional[Task]:
        """
        Update a task.
        """
        pass
    
    async def delete_task(self, task_id: int) -> bool:
        """
        Delete a task.
        """
        pass
