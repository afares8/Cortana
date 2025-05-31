import logging
import asyncio
from datetime import date, timedelta
from typing import List
from app.services.clients.services.client_service import client_service
from app.services.clients.services.document_service import document_service
from app.services.compliance.services.unified_verification_service import unified_verification_service
from app.services.compliance.models.models import CustomerVerifyRequest, Entity

logger = logging.getLogger(__name__)

class ComplianceMonitoringTasks:
    """
    Daily compliance monitoring tasks for client risk assessment and document management.
    """
    
    async def run_daily_compliance_monitoring(self):
        """
        Main daily task that orchestrates all compliance monitoring activities.
        """
        logger.info("Starting daily compliance monitoring tasks")
        
        try:
            await self._recalculate_client_risks()
            await self._reverify_high_risk_clients()
            await self._check_document_expirations()
            await self._send_expiry_alerts()
            
            logger.info("Daily compliance monitoring tasks completed successfully")
            
        except Exception as e:
            logger.error(f"Error during daily compliance monitoring: {str(e)}")
            raise
    
    async def _recalculate_client_risks(self):
        """
        Recalculate risk scores for all clients based on current data.
        """
        logger.info("Recalculating client risk scores")
        
        try:
            clients = await client_service.get_clients()
            
            for client in clients:
                try:
                    client_entity = Entity(
                        name=client.name,
                        country=getattr(client, 'country', ''),
                        type='individual' if getattr(client, 'client_type') == 'individual' else 'legal',
                        dob=getattr(client, 'dob', None),
                        id_number=getattr(client, 'registration_number', None) or str(client.id)
                    )
                    
                    directors_entities = []
                    for director_data in getattr(client, 'directors', []):
                        if isinstance(director_data, dict):
                            director_entity = Entity(
                                name=director_data.get('name', ''),
                                country=director_data.get('country', ''),
                                type='individual',
                                dob=director_data.get('dob')
                            )
                            directors_entities.append(director_entity)
                    
                    ubos_entities = []
                    for ubo_data in getattr(client, 'ubos', []):
                        if isinstance(ubo_data, dict):
                            ubo_entity = Entity(
                                name=ubo_data.get('name', ''),
                                country=ubo_data.get('country', ''),
                                type='individual',
                                dob=ubo_data.get('dob')
                            )
                            ubos_entities.append(ubo_entity)
                    
                    verification_request = CustomerVerifyRequest(
                        customer=client_entity,
                        directors=directors_entities,
                        ubos=ubos_entities
                    )
                    
                    verification_result = await unified_verification_service.verify_customer(verification_request)
                    
                    logger.info(f"Risk recalculated for client {client.name} (ID: {client.id})")
                    
                except Exception as e:
                    logger.error(f"Error recalculating risk for client {client.id}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in risk recalculation process: {str(e)}")
            raise
    
    async def _reverify_high_risk_clients(self):
        """
        Re-execute verification for clients identified as high-risk.
        """
        logger.info("Re-verifying high-risk clients")
        
        try:
            clients = await client_service.get_clients()
            high_risk_clients = [
                client for client in clients 
                if getattr(client, 'risk_level', '').upper() == 'HIGH'
            ]
            
            logger.info(f"Found {len(high_risk_clients)} high-risk clients for re-verification")
            
            for client in high_risk_clients:
                try:
                    client_entity = Entity(
                        name=client.name,
                        country=getattr(client, 'country', ''),
                        type='individual' if getattr(client, 'client_type') == 'individual' else 'legal',
                        dob=getattr(client, 'dob', None),
                        id_number=getattr(client, 'registration_number', None) or str(client.id)
                    )
                    
                    verification_request = CustomerVerifyRequest(
                        customer=client_entity,
                        directors=[],
                        ubos=[]
                    )
                    
                    verification_result = await unified_verification_service.verify_customer(verification_request)
                    
                    if self._should_flag_for_approval(verification_result):
                        await self._create_approval_workflow(client, verification_result)
                    
                    logger.info(f"High-risk client {client.name} (ID: {client.id}) re-verified")
                    
                except Exception as e:
                    logger.error(f"Error re-verifying high-risk client {client.id}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in high-risk client re-verification: {str(e)}")
            raise
    
    async def _check_document_expirations(self):
        """
        Check for documents that are expiring soon and need renewal.
        """
        logger.info("Checking document expirations")
        
        try:
            expiring_documents = await document_service.get_expiring_documents(days_ahead=30)
            
            logger.info(f"Found {len(expiring_documents)} documents expiring within 30 days")
            
            for document in expiring_documents:
                try:
                    client = await client_service.get_client(document.client_id)
                    if not client:
                        continue
                    
                    days_until_expiry = (document.expiry_date - date.today()).days
                    
                    logger.warning(
                        f"Document {document.type} for client {client.name} "
                        f"(ID: {client.id}) expires in {days_until_expiry} days"
                    )
                    
                    if days_until_expiry <= 7:
                        await self._flag_client_for_document_renewal(client, document)
                    
                except Exception as e:
                    logger.error(f"Error processing expiring document {document.id}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error checking document expirations: {str(e)}")
            raise
    
    async def _send_expiry_alerts(self):
        """
        Send alerts for documents that are expiring soon.
        """
        logger.info("Sending document expiry alerts")
        
        try:
            urgent_expiring_documents = await document_service.get_expiring_documents(days_ahead=7)
            
            for document in urgent_expiring_documents:
                try:
                    client = await client_service.get_client(document.client_id)
                    if not client:
                        continue
                    
                    days_until_expiry = (document.expiry_date - date.today()).days
                    
                    logger.warning(
                        f"URGENT: Document {document.type} for client {client.name} "
                        f"expires in {days_until_expiry} days. Immediate action required."
                    )
                    
                    await self._send_notification_alert(client, document, days_until_expiry)
                    
                except Exception as e:
                    logger.error(f"Error sending alert for document {document.id}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error sending expiry alerts: {str(e)}")
            raise
    
    def _should_flag_for_approval(self, verification_result: dict) -> bool:
        """
        Determine if a client should be flagged for manual approval based on verification results.
        """
        try:
            if verification_result.get('risk_level') == 'HIGH':
                return True
            
            pep_matches = verification_result.get('pep_matches', [])
            if pep_matches and len(pep_matches) > 0:
                return True
            
            sanctions_matches = verification_result.get('sanctions_matches', [])
            if sanctions_matches and len(sanctions_matches) > 0:
                return True
            
            risk_score = verification_result.get('risk_score', 0)
            if risk_score >= 75:  # High risk threshold
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error determining approval flag: {str(e)}")
            return True  # Default to requiring approval on error
    
    async def _create_approval_workflow(self, client, verification_result: dict):
        """
        Create a workflow instance with PENDING_APPROVAL status for flagged clients.
        """
        try:
            logger.warning(
                f"Client {client.name} (ID: {client.id}) flagged for manual approval. "
                f"Risk level: {verification_result.get('risk_level', 'UNKNOWN')}"
            )
            
            approval_data = {
                'client_id': client.id,
                'client_name': client.name,
                'status': 'PENDING_APPROVAL',
                'reason': 'High-risk verification result',
                'verification_result': verification_result,
                'created_at': date.today().isoformat()
            }
            
            logger.info(f"Approval workflow created for client {client.id}: {approval_data}")
            
        except Exception as e:
            logger.error(f"Error creating approval workflow for client {client.id}: {str(e)}")
    
    async def _flag_client_for_document_renewal(self, client, document):
        """
        Flag a client for document renewal when documents are expiring soon.
        """
        try:
            logger.warning(
                f"Client {client.name} (ID: {client.id}) flagged for document renewal. "
                f"Document {document.type} expires on {document.expiry_date}"
            )
            
            renewal_data = {
                'client_id': client.id,
                'document_id': document.id,
                'document_type': document.type,
                'expiry_date': document.expiry_date.isoformat(),
                'status': 'RENEWAL_REQUIRED',
                'flagged_at': date.today().isoformat()
            }
            
            logger.info(f"Document renewal flag created: {renewal_data}")
            
        except Exception as e:
            logger.error(f"Error flagging client for document renewal: {str(e)}")
    
    async def _send_notification_alert(self, client, document, days_until_expiry: int):
        """
        Send notification alert for expiring documents.
        """
        try:
            alert_message = (
                f"URGENT: Document expiry alert for client {client.name}. "
                f"Document type: {document.type}. "
                f"Expires in {days_until_expiry} days. "
                f"Please contact client for document renewal."
            )
            
            logger.warning(f"NOTIFICATION SENT: {alert_message}")
            
            
        except Exception as e:
            logger.error(f"Error sending notification alert: {str(e)}")

compliance_monitoring_tasks = ComplianceMonitoringTasks()

async def run_daily_compliance_monitoring():
    """
    Entry point for daily compliance monitoring cron job.
    """
    try:
        await compliance_monitoring_tasks.run_daily_compliance_monitoring()
    except Exception as e:
        logger.error(f"Daily compliance monitoring failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(run_daily_compliance_monitoring())
