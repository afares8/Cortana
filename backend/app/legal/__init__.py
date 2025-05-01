from app.legal.routers import router
from app.legal.services import (
    create_client, get_client, get_clients, update_client, delete_client,
    
    create_contract, get_contract, get_contracts, update_contract, delete_contract,
    get_contract_version, get_contract_versions,
    
    create_workflow_template, get_workflow_template, get_workflow_templates,
    update_workflow_template, delete_workflow_template,
    create_workflow_instance, get_workflow_instance, get_workflow_instances,
    update_workflow_step,
    
    create_task, get_task, get_tasks, update_task, delete_task,
    
    get_audit_logs,
    
    init_legal_db
)
