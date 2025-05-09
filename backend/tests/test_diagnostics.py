import unittest
import asyncio
import json
import os
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

from app.services.diagnostics.checker import check_system_resources, check_docker_services, check_ai_service, check_database, run_all_checks
from app.services.diagnostics.docker_monitor import get_container_status, get_container_logs, check_model_container_health
from app.services.diagnostics.explainer import explain_issues
from app.services.diagnostics.code_suggester import suggest_action
from app.services.diagnostics.predictive import analyze_trends
from app.services.diagnostics.stats_tracker import log_diagnostic_run, get_diagnostic_history, get_component_history, get_diagnostic_stats
from app.services.diagnostics.interface import DiagnosticsService

class TestDiagnostics(unittest.TestCase):
    """Test cases for the diagnostics module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        self.sample_items = [
            {
                "component": "system_resources",
                "status": "healthy",
                "description": "System resources check",
                "timestamp": datetime.utcnow(),
                "details": {
                    "cpu_percent": 45,
                    "memory_percent": 60,
                    "disk_percent": 72
                }
            },
            {
                "component": "docker_ai-service",
                "status": "warning",
                "description": "Docker container: ai-service",
                "timestamp": datetime.utcnow(),
                "error_details": {
                    "error": "Container is restarting frequently"
                }
            },
            {
                "component": "ai_service",
                "status": "error",
                "description": "AI service status check",
                "timestamp": datetime.utcnow(),
                "error_details": {
                    "error": "Service is not responding"
                }
            },
            {
                "component": "database",
                "status": "healthy",
                "description": "Database check",
                "timestamp": datetime.utcnow()
            }
        ]
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.loop.close()
    
    @patch('app.services.diagnostics.checker.psutil')
    def test_check_system_resources(self, mock_psutil):
        """Test the system resources check."""
        mock_psutil.cpu_percent.return_value = 50
        mock_memory = MagicMock()
        mock_memory.percent = 60
        mock_memory.available = 4000000000
        mock_memory.total = 8000000000
        mock_psutil.virtual_memory.return_value = mock_memory
        
        mock_disk = MagicMock()
        mock_disk.percent = 70
        mock_disk.free = 50000000000
        mock_disk.total = 100000000000
        mock_psutil.disk_usage.return_value = mock_disk
        
        result = self.loop.run_until_complete(check_system_resources())
        
        self.assertEqual(result["component"], "system_resources")
        self.assertEqual(result["status"], "healthy")
        self.assertEqual(result["details"]["cpu_percent"], 50)
        self.assertEqual(result["details"]["memory_percent"], 60)
        self.assertEqual(result["details"]["disk_percent"], 70)
    
    @patch('app.services.diagnostics.docker_monitor.subprocess.run')
    def test_get_container_status(self, mock_run):
        """Test the container status check."""
        mock_process = MagicMock()
        mock_process.stdout = "ai-service|Up 2 days (healthy)|mistral-7b:latest|2 days\n" + \
                             "postgres|Up 2 days (healthy)|postgres:13|2 days"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        result = self.loop.run_until_complete(get_container_status())
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "ai-service")
        self.assertEqual(result[0]["health_status"], "healthy")
        self.assertEqual(result[0]["image"], "mistral-7b:latest")
        
        self.assertEqual(result[1]["name"], "postgres")
        self.assertEqual(result[1]["health_status"], "healthy")
        self.assertEqual(result[1]["image"], "postgres:13")
    
    @patch('app.services.diagnostics.docker_monitor.subprocess.run')
    def test_get_container_logs(self, mock_run):
        """Test the container logs retrieval."""
        mock_process = MagicMock()
        mock_process.stdout = "Container log line 1\nContainer log line 2"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        result = self.loop.run_until_complete(get_container_logs("ai-service"))
        
        self.assertEqual(result, "Container log line 1\nContainer log line 2")
    
    @patch('app.services.diagnostics.docker_monitor.get_container_status')
    @patch('app.services.diagnostics.docker_monitor.get_container_logs')
    def test_check_model_container_health_healthy(self, mock_logs, mock_status):
        """Test the model container health check when healthy."""
        mock_status.return_value = [{
            "name": "ai-service",
            "health_status": "healthy",
            "image": "mistral-7b:latest",
            "running_for": "2 days"
        }]
        
        status, error = self.loop.run_until_complete(check_model_container_health())
        
        self.assertEqual(status, "healthy")
        self.assertIsNone(error)
    
    @patch('app.services.diagnostics.docker_monitor.get_container_status')
    @patch('app.services.diagnostics.docker_monitor.get_container_logs')
    def test_check_model_container_health_error(self, mock_logs, mock_status):
        """Test the model container health check when error."""
        mock_status.return_value = [{
            "name": "ai-service",
            "health_status": "error",
            "image": "mistral-7b:latest",
            "running_for": "5 minutes"
        }]
        
        mock_logs.return_value = "Error: Out of memory"
        
        status, error = self.loop.run_until_complete(check_model_container_health())
        
        self.assertEqual(status, "error")
        self.assertIn("Error: Out of memory", error)
    
    @patch('app.services.diagnostics.explainer.mistral_client')
    def test_explain_issues(self, mock_mistral):
        """Test the issue explanation."""
        mock_mistral.generate.return_value = {
            "generated_text": "The system is experiencing issues with the AI service. The container is restarting frequently, which may indicate resource constraints or configuration problems."
        }
        
        result = self.loop.run_until_complete(explain_issues(self.sample_items))
        
        self.assertIn("The system is experiencing issues with the AI service", result)
    
    @patch('app.services.diagnostics.code_suggester.mistral_client')
    def test_suggest_action(self, mock_mistral):
        """Test the action suggestion."""
        mock_mistral.generate.return_value = {
            "generated_text": "Restart the AI service container and check for configuration issues."
        }
        
        result = self.loop.run_until_complete(suggest_action(self.sample_items[2]))
        
        self.assertIn("Restart the AI service container", result)
    
    def test_analyze_trends_insufficient_data(self):
        """Test the trend analysis with insufficient data."""
        result = self.loop.run_until_complete(analyze_trends("ai_service", []))
        
        self.assertEqual(result["prediction"], "Insufficient historical data for trend analysis")
        self.assertEqual(result["confidence"], 0.0)
        self.assertEqual(result["trend"], "unknown")
    
    def test_analyze_trends_deteriorating(self):
        """Test the trend analysis with deteriorating trend."""
        history = [
            {
                "component": "ai_service",
                "status": "healthy",
                "timestamp": "2025-05-09T08:00:00.000Z"
            },
            {
                "component": "ai_service",
                "status": "warning",
                "timestamp": "2025-05-09T09:00:00.000Z"
            },
            {
                "component": "ai_service",
                "status": "error",
                "timestamp": "2025-05-09T10:00:00.000Z"
            }
        ]
        
        result = self.loop.run_until_complete(analyze_trends("ai_service", history))
        
        self.assertIn("Component likely to continue experiencing errors", result["prediction"])
        self.assertGreater(result["confidence"], 0.5)
        self.assertEqual(result["trend"], "critical")
    
    @patch('app.services.diagnostics.stats_tracker.open', new_callable=mock_open)
    @patch('app.services.diagnostics.stats_tracker.json.dump')
    @patch('app.services.diagnostics.stats_tracker.json.load')
    @patch('app.services.diagnostics.stats_tracker.os.path.exists')
    def test_log_diagnostic_run(self, mock_exists, mock_load, mock_dump, mock_open):
        """Test logging a diagnostic run."""
        mock_exists.return_value = True
        
        mock_load.return_value = []
        
        result = self.loop.run_until_complete(log_diagnostic_run(self.sample_items))
        
        self.assertTrue(result)
        mock_dump.assert_called_once()
    
    @patch('app.services.diagnostics.stats_tracker.open', new_callable=mock_open)
    @patch('app.services.diagnostics.stats_tracker.json.load')
    @patch('app.services.diagnostics.stats_tracker.os.path.exists')
    def test_get_diagnostic_history(self, mock_exists, mock_load, mock_open):
        """Test getting diagnostic history."""
        mock_exists.return_value = True
        
        mock_load.return_value = self.sample_items
        
        result = self.loop.run_until_complete(get_diagnostic_history())
        
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0]["component"], "system_resources")
        self.assertEqual(result[0]["status"], "healthy")
    
    @patch('app.services.diagnostics.interface.run_all_checks')
    @patch('app.services.diagnostics.interface.explain_issues')
    @patch('app.services.diagnostics.interface.suggest_action')
    @patch('app.services.diagnostics.interface.log_diagnostic_run')
    def test_diagnostics_service_run_diagnostics(self, mock_log, mock_suggest, mock_explain, mock_checks):
        """Test the diagnostics service run_diagnostics method."""
        mock_checks.return_value = self.sample_items
        
        mock_explain.return_value = "The system is experiencing issues with the AI service."
        
        mock_suggest.return_value = "Restart the AI service container."
        
        mock_log.return_value = True
        
        service = DiagnosticsService()
        
        result = self.loop.run_until_complete(service.run_diagnostics())
        
        self.assertEqual(result["overall_status"], "error")
        self.assertEqual(len(result["items"]), 4)
        self.assertEqual(result["explanation"], "The system is experiencing issues with the AI service.")
        
        mock_checks.assert_called_once()
        mock_explain.assert_called_once()
        mock_suggest.assert_called()
        mock_log.assert_called_once()
    
    @patch('app.services.diagnostics.interface.get_diagnostic_stats')
    def test_diagnostics_service_get_stats(self, mock_stats):
        """Test the diagnostics service get_stats method."""
        mock_stats.return_value = {
            "total_runs": 10,
            "healthy_count": 25,
            "warning_count": 5,
            "error_count": 3,
            "components_checked": ["system_resources", "docker_ai-service", "ai_service", "database"],
            "last_run": datetime.utcnow().isoformat(),
            "history": {}
        }
        
        service = DiagnosticsService()
        
        result = self.loop.run_until_complete(service.get_stats())
        
        self.assertEqual(result["total_runs"], 10)
        self.assertEqual(result["healthy_count"], 25)
        self.assertEqual(result["warning_count"], 5)
        self.assertEqual(result["error_count"], 3)
        
        mock_stats.assert_called_once()

if __name__ == '__main__':
    unittest.main()
