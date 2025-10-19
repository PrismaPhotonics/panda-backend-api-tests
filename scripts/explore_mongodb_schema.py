#!/usr/bin/env python3
"""
MongoDB Schema Discovery Tool

Purpose:
    Automatically discover and document MongoDB database schema including:
    - All collections
    - Sample documents from each collection
    - Field types and patterns
    - Indexes
    - Data statistics

Usage:
    python scripts/explore_mongodb_schema.py --env k9s
    python scripts/explore_mongodb_schema.py --output schema_report.json

Author: QA Automation Team
"""

import argparse
import json
import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from bson import ObjectId
from pymongo import MongoClient
from pymongo.database import Database


# ============================================================================
# Logger Setup
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# MongoDB Schema Discovery Engine
# ============================================================================
class MongoDBSchemaDiscovery:
    """
    Discovers and analyzes MongoDB schema structure.
    
    This tool connects to MongoDB and automatically extracts:
    - Collection names
    - Document structure (fields and types)
    - Sample data
    - Indexes
    - Statistics (document count, size)
    """
    
    def __init__(self, connection_string: str, database_name: str):
        """
        Initialize MongoDB connection.
        
        Args:
            connection_string: MongoDB connection URI
            database_name: Name of database to analyze
        """
        self.client = MongoClient(connection_string)
        self.db: Database = self.client[database_name]
        self.database_name = database_name
        self.schema_report = {
            "discovery_timestamp": datetime.utcnow().isoformat(),
            "database_name": database_name,
            "collections": {}
        }
        
    def discover_all(self) -> Dict[str, Any]:
        """
        Run full schema discovery on all collections.
        
        Returns:
            Complete schema report as dictionary
        """
        logger.info(f"🔍 Starting schema discovery for database: {self.database_name}")
        
        # Get all collection names
        collections = self.db.list_collection_names()
        logger.info(f"📦 Found {len(collections)} collections: {collections}")
        
        # Analyze each collection
        for collection_name in collections:
            logger.info(f"\n{'='*60}")
            logger.info(f"Analyzing collection: {collection_name}")
            logger.info(f"{'='*60}")
            
            collection_schema = self._analyze_collection(collection_name)
            self.schema_report["collections"][collection_name] = collection_schema
            
        logger.info(f"\n✅ Schema discovery completed!")
        return self.schema_report
    
    def _analyze_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        Analyze a single collection.
        
        Args:
            collection_name: Name of collection to analyze
            
        Returns:
            Dictionary with collection schema information
        """
        collection = self.db[collection_name]
        
        # Get basic stats
        total_docs = collection.count_documents({})
        logger.info(f"  📊 Total documents: {total_docs}")
        
        schema = {
            "document_count": total_docs,
            "sample_documents": [],
            "field_analysis": {},
            "indexes": [],
            "unique_fields": set(),
            "nullable_fields": set()
        }
        
        if total_docs == 0:
            logger.warning(f"  ⚠️  Collection '{collection_name}' is empty!")
            return schema
        
        # Get sample documents
        sample_size = min(100, total_docs)  # Sample up to 100 documents
        logger.info(f"  🔬 Sampling {sample_size} documents...")
        
        sample_docs = list(collection.aggregate([{"$sample": {"size": sample_size}}]))
        schema["sample_documents"] = [self._serialize_doc(doc) for doc in sample_docs[:5]]  # Store first 5
        
        # Analyze field types
        logger.info(f"  🧬 Analyzing field types...")
        field_types = self._analyze_fields(sample_docs)
        schema["field_analysis"] = field_types
        
        # Get indexes
        logger.info(f"  🔑 Analyzing indexes...")
        indexes = self._get_indexes(collection)
        schema["indexes"] = indexes
        
        # Print summary
        self._print_collection_summary(collection_name, schema)
        
        return schema
    
    def _analyze_fields(self, documents: List[Dict]) -> Dict[str, Any]:
        """
        Analyze field types across documents.
        
        Args:
            documents: List of documents to analyze
            
        Returns:
            Dictionary mapping field names to type information
        """
        field_info = defaultdict(lambda: {
            "types": defaultdict(int),
            "null_count": 0,
            "present_count": 0,
            "sample_values": []
        })
        
        for doc in documents:
            # Flatten nested document
            flat_doc = self._flatten_dict(doc)
            
            # Track which fields are present in this document
            present_fields = set(flat_doc.keys())
            
            # Analyze each field
            for field, value in flat_doc.items():
                info = field_info[field]
                info["present_count"] += 1
                
                if value is None:
                    info["null_count"] += 1
                    info["types"]["null"] += 1
                else:
                    type_name = type(value).__name__
                    info["types"][type_name] += 1
                    
                    # Store sample values (max 5)
                    if len(info["sample_values"]) < 5:
                        info["sample_values"].append(self._serialize_value(value))
        
        # Convert defaultdict to regular dict for JSON serialization
        result = {}
        total_docs = len(documents)
        
        for field, info in field_info.items():
            result[field] = {
                "types": dict(info["types"]),
                "present_in_docs": f"{info['present_count']}/{total_docs}",
                "null_count": info["null_count"],
                "sample_values": info["sample_values"],
                "is_nullable": info["null_count"] > 0,
                "is_always_present": info["present_count"] == total_docs
            }
        
        return result
    
    def _get_indexes(self, collection) -> List[Dict[str, Any]]:
        """
        Get all indexes for a collection.
        
        Args:
            collection: PyMongo collection object
            
        Returns:
            List of index definitions
        """
        indexes = []
        
        for index in collection.list_indexes():
            index_info = {
                "name": index.get("name"),
                "keys": index.get("key", {}),
                "unique": index.get("unique", False),
                "sparse": index.get("sparse", False),
                "background": index.get("background", False)
            }
            indexes.append(index_info)
            
            # Log index
            unique_str = "UNIQUE" if index_info["unique"] else "NON-UNIQUE"
            logger.info(f"    🔑 {index_info['name']}: {index_info['keys']} ({unique_str})")
        
        return indexes
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """
        Flatten nested dictionary.
        
        Args:
            d: Dictionary to flatten
            parent_key: Parent key prefix
            sep: Separator for nested keys
            
        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict) and not isinstance(v, ObjectId):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    def _serialize_doc(self, doc: Dict) -> Dict:
        """Serialize MongoDB document for JSON output."""
        return {k: self._serialize_value(v) for k, v in doc.items()}
    
    def _serialize_value(self, value: Any) -> Any:
        """Serialize a single value for JSON output."""
        if isinstance(value, ObjectId):
            return str(value)
        elif isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, dict):
            return self._serialize_doc(value)
        elif isinstance(value, list):
            return [self._serialize_value(v) for v in value]
        else:
            return value
    
    def _print_collection_summary(self, name: str, schema: Dict):
        """Print human-readable summary of collection schema."""
        logger.info(f"\n  📋 Collection '{name}' Summary:")
        logger.info(f"     Total documents: {schema['document_count']}")
        logger.info(f"     Total fields: {len(schema['field_analysis'])}")
        logger.info(f"     Total indexes: {len(schema['indexes'])}")
        
        # Print required fields (always present)
        required = [f for f, info in schema['field_analysis'].items() 
                   if info.get('is_always_present', False) and f != '_id']
        if required:
            logger.info(f"     ✅ Required fields: {required}")
        
        # Print nullable fields
        nullable = [f for f, info in schema['field_analysis'].items() 
                   if info.get('is_nullable', False)]
        if nullable:
            logger.info(f"     ⚠️  Nullable fields: {nullable}")
    
    def save_report(self, output_path: str):
        """
        Save schema report to JSON file.
        
        Args:
            output_path: Path to output file
        """
        # Convert sets to lists for JSON serialization
        serialized_report = self._serialize_doc(self.schema_report)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serialized_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n💾 Schema report saved to: {output_file}")
    
    def generate_test_code(self, collection_name: str) -> str:
        """
        Generate pytest test code for collection validation.
        
        Args:
            collection_name: Name of collection
            
        Returns:
            Generated Python test code
        """
        if collection_name not in self.schema_report["collections"]:
            raise ValueError(f"Collection '{collection_name}' not found in schema report")
        
        schema = self.schema_report["collections"][collection_name]
        fields = schema["field_analysis"]
        
        # Get required fields
        required_fields = [f for f, info in fields.items() 
                          if info.get('is_always_present', False) and f != '_id']
        
        # Generate test code
        test_code = f'''
def test_{collection_name}_schema_validation(self):
    """
    Verify {collection_name} collection documents have required fields.
    
    Auto-generated from schema discovery.
    """
    self.logger.info("TEST: {collection_name} Schema Validation")
    
    try:
        # Access collection
        collection = self._get_collection("{collection_name}")
        
        # Get sample documents
        sample_docs = list(collection.aggregate([{{"$sample": {{"size": 50}}}}]))
        
        assert len(sample_docs) > 0, "{collection_name} collection is empty"
        
        # Required fields
        required_fields = {required_fields}
        
        # Validate each document
        for doc in sample_docs:
            for field in required_fields:
                assert field in doc, f"Missing required field: {{field}}"
                assert doc[field] is not None, f"Field {{field}} is null"
        
        self.logger.info(f"✅ All {{len(sample_docs)}} documents have required fields")
        
    except Exception as e:
        self.logger.error(f"❌ Schema validation failed: {{e}}")
        raise
'''
        return test_code


# ============================================================================
# Configuration Loader
# ============================================================================
def load_config(env: str) -> Dict[str, str]:
    """
    Load MongoDB connection config from environments.yaml.
    
    Args:
        env: Environment name (e.g., 'staging', 'local', 'production')
        
    Returns:
        Dictionary with connection details
    """
    config_path = Path(__file__).parent.parent / "config" / "environments.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    if env not in config["environments"]:
        available = list(config["environments"].keys())
        raise ValueError(f"Environment '{env}' not found. Available: {available}")
    
    env_config = config["environments"][env]
    mongo_config = env_config.get("mongodb", {})
    
    return {
        "host": mongo_config.get("host", "localhost"),
        "port": mongo_config.get("port", 27017),
        "database": mongo_config.get("database", "test"),
        "username": mongo_config.get("username"),
        "password": mongo_config.get("password")
    }


# ============================================================================
# Main Execution
# ============================================================================
def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MongoDB Schema Discovery Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--env",
        default="staging",
        help="Environment name from config (default: staging). Available: local, staging, production"
    )
    
    parser.add_argument(
        "--output",
        default="reports/mongodb_schema_report.json",
        help="Output file path (default: reports/mongodb_schema_report.json)"
    )
    
    parser.add_argument(
        "--generate-tests",
        action="store_true",
        help="Generate pytest test code from discovered schema"
    )
    
    args = parser.parse_args()
    
    # Load config
    logger.info(f"📋 Loading configuration for environment: {args.env}")
    config = load_config(args.env)
    
    # Build connection string
    if config.get("username") and config.get("password"):
        connection_string = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}"
    else:
        connection_string = f"mongodb://{config['host']}:{config['port']}"
    
    # Run discovery
    discovery = MongoDBSchemaDiscovery(connection_string, config["database"])
    schema_report = discovery.discover_all()
    
    # Save report
    discovery.save_report(args.output)
    
    # Generate test code if requested
    if args.generate_tests:
        logger.info("\n🧪 Generating pytest test code...")
        test_output = Path("tests/generated_mongodb_tests.py")
        
        with open(test_output, 'w', encoding='utf-8') as f:
            f.write('"""Auto-generated MongoDB schema validation tests."""\n\n')
            f.write('import pytest\n')
            f.write('from tests.integration.infrastructure.test_mongodb_data_quality import TestMongoDBDataQuality\n\n')
            
            for collection_name in schema_report["collections"].keys():
                test_code = discovery.generate_test_code(collection_name)
                f.write(test_code)
                f.write('\n\n')
        
        logger.info(f"💾 Test code saved to: {test_output}")
    
    logger.info("\n✨ Done!")


if __name__ == "__main__":
    main()

