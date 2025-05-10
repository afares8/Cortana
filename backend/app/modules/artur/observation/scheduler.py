import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore
from app.modules.artur.observation.services import observation_service
from app.modules.artur.evaluation.services import evaluation_service

logger = logging.getLogger(__name__)

class ArturObservationScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
    def start(self):
        """Start the Artur observation scheduler"""
        if self.is_running:
            logger.warning("Artur observation scheduler is already running")
            return
            
        self.scheduler.add_job(
            self._run_observation_cycle,
            IntervalTrigger(hours=6),  # Run every 6 hours
            id="artur_observation_cycle",
            replace_existing=True
        )
        
        self.scheduler.add_job(
            self._run_evaluation_cycle,
            IntervalTrigger(hours=24),  # Run daily
            id="artur_evaluation_cycle",
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info("Artur observation scheduler started")
        
    def stop(self):
        """Stop the Artur observation scheduler"""
        if not self.is_running:
            logger.warning("Artur observation scheduler is not running")
            return
            
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Artur observation scheduler stopped")
        
    async def _run_observation_cycle(self):
        """Run a complete observation cycle"""
        try:
            logger.info("Starting Artur observation cycle")
            start_time = datetime.utcnow()
            
            insights = await observation_service.run_all_monitors()
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Artur observation cycle completed in {duration:.2f} seconds. Generated {len(insights)} insights.")
        except Exception as e:
            logger.error(f"Error in Artur observation cycle: {e}")
            
    async def _run_evaluation_cycle(self):
        """Run a complete evaluation cycle based on collected insights"""
        try:
            logger.info("Starting Artur evaluation cycle")
            start_time = datetime.utcnow()
            
            suggestions = await evaluation_service.run_all_evaluations()
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Artur evaluation cycle completed in {duration:.2f} seconds. Generated {len(suggestions)} suggestions.")
        except Exception as e:
            logger.error(f"Error in Artur evaluation cycle: {e}")
            
    async def run_manual_observation_cycle(self):
        """Manually trigger an observation cycle"""
        await self._run_observation_cycle()
        
    async def run_manual_evaluation_cycle(self):
        """Manually trigger an evaluation cycle"""
        await self._run_evaluation_cycle()

observation_scheduler = ArturObservationScheduler()
