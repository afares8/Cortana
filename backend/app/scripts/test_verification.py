"""
Test script for customer verification against PEP and sanctions lists.

This script tests the verification service for both natural persons and legal entities.
It can be used to verify the functionality of the customer verification endpoint.
"""

import asyncio
import json
import sys
import os
import logging
from datetime import date
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.services.compliance.schemas.verify import (
    CustomerVerifyRequest, EntityBase
)
from app.services.compliance.services.verification_service import verification_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_natural_person():
    """Test verification of a natural person"""
    logger.info("Testing natural person verification...")
    
    customer = EntityBase(
        name="John Doe",
        dob=date(1970, 1, 1),
        country="US",
        type="natural"
    )
    
    request = CustomerVerifyRequest(
        customer=customer,
        directors=[],
        ubos=[]
    )
    
    result = await verification_service.verify_customer(request)
    
    print("\n=== Natural Person Verification Results ===")
    print(f"Verification ID: {result.verification_id}")
    print(f"PEP Status: {result.pep.status}")
    print(f"OFAC Status: {result.ofac.status}")
    print(f"UN Status: {result.un.status}")
    print(f"EU Status: {result.eu.status}")
    
    print("\nEnriched Data:")
    print(f"Aliases: {result.enriched_data['customer'].get('aliases', [])}")
    
    print("\nDetailed Results:")
    print(json.dumps(result.dict(), indent=2))
    
    return result

async def test_legal_entity():
    """Test verification of a legal entity with directors and UBOs"""
    logger.info("Testing legal entity verification...")
    
    customer = EntityBase(
        name="Acme Corp",
        country="US",
        type="legal"
    )
    
    directors = [
        EntityBase(
            name="Jane Doe",
            dob=date(1980, 5, 15),
            country="US",
            type="natural"
        )
    ]
    
    ubos = [
        EntityBase(
            name="Jim Smith",
            dob=date(1965, 9, 30),
            country="US",
            type="natural"
        )
    ]
    
    request = CustomerVerifyRequest(
        customer=customer,
        directors=directors,
        ubos=ubos
    )
    
    result = await verification_service.verify_customer(request)
    
    print("\n=== Legal Entity Verification Results ===")
    print(f"Verification ID: {result.verification_id}")
    print(f"PEP Status: {result.pep.status}")
    print(f"OFAC Status: {result.ofac.status}")
    print(f"UN Status: {result.un.status}")
    print(f"EU Status: {result.eu.status}")
    
    print("\nEnriched Data:")
    print(f"Company Aliases: {result.enriched_data['customer'].get('aliases', [])}")
    print(f"Directors: {len(result.enriched_data['directors'])}")
    print(f"UBOs: {len(result.enriched_data['ubos'])}")
    
    print("\nDetailed Results:")
    print(json.dumps(result.dict(), indent=2))
    
    return result

async def main():
    parser = argparse.ArgumentParser(description="Test customer verification")
    parser.add_argument("--type", choices=["natural", "legal", "both"], default="both",
                       help="Type of entity to test (natural, legal, or both)")
    parser.add_argument("--mock", action="store_true", help="Use mock data instead of real API calls")
    
    args = parser.parse_args()
    
    if args.type in ["natural", "both"]:
        await test_natural_person()
    
    if args.type in ["legal", "both"]:
        await test_legal_entity()

if __name__ == "__main__":
    asyncio.run(main())
