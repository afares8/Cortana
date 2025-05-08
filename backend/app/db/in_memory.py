"""
In-memory database for compliance module with file persistence.
This module provides simple in-memory storage for compliance-related data
with basic file persistence to survive server restarts.
"""
from typing import Dict, List, Any, Optional
import logging
import json
import os
import pickle
from datetime import datetime

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)


class InMemoryDB:
    """Simple in-memory database for storing records with file persistence."""

    def __init__(self, name: str):
        self.name = name
        self.data: Dict[int, Any] = {}
        self.next_id = 1
        self.db_file = os.path.join(DATA_DIR, f"{name}_db.pickle")
        self._load_from_disk()
        logger.info(f"Initialized in-memory database: {name}")

    def _load_from_disk(self):
        """Load database from disk if file exists."""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'rb') as f:
                    db_data = pickle.load(f)
                    self.data = db_data.get('data', {})
                    self.next_id = db_data.get('next_id', 1)
                logger.info(f"Loaded {len(self.data)} records from {self.db_file}")
        except Exception as e:
            logger.error(f"Error loading database from disk: {str(e)}")

    def _save_to_disk(self):
        """Save database to disk."""
        try:
            with open(self.db_file, 'wb') as f:
                pickle.dump({'data': self.data, 'next_id': self.next_id}, f)
            logger.debug(f"Saved {len(self.data)} records to {self.db_file}")
        except Exception as e:
            logger.error(f"Error saving database to disk: {str(e)}")

    def create(self, record: Any) -> int:
        """Create a new record and return its ID."""
        record_id = self.next_id
        
        if isinstance(record, dict):
            record["id"] = record_id
            self.data[record_id] = record
        else:
            record.id = record_id
            self.data[record_id] = record
        
        self.next_id += 1
        logger.debug(f"Created record in {self.name} with ID: {record_id}")
        self._save_to_disk()
        return record_id

    def get(self, record_id: int) -> Optional[Any]:
        """Get a record by ID."""
        return self.data.get(record_id)

    def get_all(self) -> List[Any]:
        """Get all records."""
        return list(self.data.values())

    def update(self, record_id: int, record: Any) -> bool:
        """Update a record by ID."""
        if record_id not in self.data:
            logger.warning(f"Record with ID {record_id} not found in {self.name}")
            return False
        
        if isinstance(record, dict):
            record["id"] = record_id
            self.data[record_id] = record
        else:
            record.id = record_id
            self.data[record_id] = record
            
        logger.debug(f"Updated record in {self.name} with ID: {record_id}")
        self._save_to_disk()
        return True

    def delete(self, record_id: int) -> bool:
        """Delete a record by ID."""
        if record_id not in self.data:
            logger.warning(f"Record with ID {record_id} not found in {self.name}")
            return False
        
        del self.data[record_id]
        logger.debug(f"Deleted record in {self.name} with ID: {record_id}")
        self._save_to_disk()
        return True

    def filter(self, filter_func) -> List[Any]:
        """Filter records using a filter function."""
        return [record for record in self.data.values() if filter_func(record)]


compliance_reports_db = InMemoryDB("compliance_reports")
pep_screening_results_db = InMemoryDB("pep_screening_results")
sanctions_screening_results_db = InMemoryDB("sanctions_screening_results")
list_updates_db = InMemoryDB("list_updates")
