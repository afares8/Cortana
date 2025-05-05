from typing import List, Optional, Dict, Any
from app.services.workflows.models.workflow import WorkflowTemplate, WorkflowInstance

class WorkflowsServiceInterface:
    """
    Interface for workflow operations.
    """
    
    async def create_workflow_template(self, template_data: Dict[str, Any]) -> WorkflowTemplate:
        """
        Create a new workflow template.
        """
        pass
    
    async def get_workflow_templates(self) -> List[WorkflowTemplate]:
        """
        Get all workflow templates.
        """
        pass
    
    async def get_workflow_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """
        Get a workflow template by ID.
        """
        pass
    
    async def update_workflow_template(
        self,
        template_id: str,
        template_data: Dict[str, Any]
    ) -> Optional[WorkflowTemplate]:
        """
        Update a workflow template.
        """
        pass
    
    async def delete_workflow_template(self, template_id: str) -> bool:
        """
        Delete a workflow template.
        """
        pass
    
    async def create_workflow_instance(self, instance_data: Dict[str, Any]) -> Optional[WorkflowInstance]:
        """
        Create a new workflow instance from a template.
        """
        pass
    
    async def get_workflow_instances(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[WorkflowInstance]:
        """
        Get workflow instances with optional filtering.
        """
        pass
    
    async def get_workflow_instance(self, instance_id: int) -> Optional[WorkflowInstance]:
        """
        Get a workflow instance by ID.
        """
        pass
    
    async def update_workflow_step(
        self,
        instance_id: int,
        step_id: str,
        step_data: Dict[str, Any]
    ) -> Optional[WorkflowInstance]:
        """
        Update a step in a workflow instance.
        """
        pass
