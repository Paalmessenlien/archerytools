#!/usr/bin/env python3
"""
Database Health Checker for ArrowTuner
Provides comprehensive database health analysis and maintenance recommendations
"""

import os
import sqlite3
import time
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

@dataclass
class TableStats:
    """Statistics for a database table"""
    name: str
    row_count: int
    size_bytes: int
    index_count: int
    has_primary_key: bool
    fragmentation_level: float
    last_analyzed: Optional[str]

@dataclass 
class DatabaseHealthReport:
    """Comprehensive database health report"""
    database_path: str
    database_size_mb: float
    total_tables: int
    total_indexes: int
    integrity_status: str
    performance_score: int  # 0-100
    recommendations: List[str]
    table_stats: List[TableStats]
    query_performance: Dict[str, float]
    storage_analysis: Dict[str, Any]
    last_maintenance: Optional[str]

class DatabaseHealthChecker:
    """Comprehensive database health analysis and maintenance"""
    
    def __init__(self, database_path: str = None):
        self.database_path = database_path or self._resolve_database_path()
        self.logger = logging.getLogger(__name__)
        
    def _resolve_database_path(self) -> str:
        """Resolve database path with fallback options"""
        # Try environment variable first
        env_path = os.environ.get('ARROW_DATABASE_PATH')
        if env_path and Path(env_path).exists():
            return env_path
            
        # Try common Docker paths
        docker_paths = [
            '/app/databases/arrow_database.db',
            '/app/arrow_data/arrow_database.db',
            '/app/arrow_database.db'
        ]
        
        for path in docker_paths:
            if Path(path).exists():
                return path
                
        # Try local development paths
        local_paths = [
            './databases/arrow_database.db',
            './arrow_database.db',
            '../databases/arrow_database.db'
        ]
        
        for path in local_paths:
            if Path(path).exists():
                return str(Path(path).resolve())
                
        # Default fallback
        return './arrow_database.db'
    
    def run_comprehensive_health_check(self) -> DatabaseHealthReport:
        """Run complete database health analysis"""
        try:
            print(f"🏥 Running comprehensive health check on: {self.database_path}")
            
            if not Path(self.database_path).exists():
                return DatabaseHealthReport(
                    database_path=self.database_path,
                    database_size_mb=0,
                    total_tables=0,
                    total_indexes=0,
                    integrity_status="DATABASE_NOT_FOUND",
                    performance_score=0,
                    recommendations=["Database file does not exist - check configuration"],
                    table_stats=[],
                    query_performance={},
                    storage_analysis={},
                    last_maintenance=None
                )
            
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            
            # Run all health checks
            integrity_status = self._check_integrity(conn)
            table_stats = self._analyze_tables(conn)
            query_performance = self._test_query_performance(conn)
            storage_analysis = self._analyze_storage(conn)
            
            # Calculate overall performance score
            performance_score = self._calculate_performance_score(
                integrity_status, table_stats, query_performance, storage_analysis
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                integrity_status, table_stats, query_performance, storage_analysis
            )
            
            # Get database statistics
            database_size_mb = Path(self.database_path).stat().st_size / (1024 * 1024)
            total_tables = len(table_stats)
            total_indexes = sum(stat.index_count for stat in table_stats)
            
            conn.close()
            
            report = DatabaseHealthReport(
                database_path=self.database_path,
                database_size_mb=round(database_size_mb, 2),
                total_tables=total_tables,
                total_indexes=total_indexes,
                integrity_status=integrity_status,
                performance_score=performance_score,
                recommendations=recommendations,
                table_stats=table_stats,
                query_performance=query_performance,
                storage_analysis=storage_analysis,
                last_maintenance=self._get_last_maintenance_time()
            )
            
            print(f"✅ Health check completed - Score: {performance_score}/100")
            return report
            
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return DatabaseHealthReport(
                database_path=self.database_path,
                database_size_mb=0,
                total_tables=0,
                total_indexes=0,
                integrity_status=f"ERROR: {str(e)}",
                performance_score=0,
                recommendations=[f"Health check failed: {str(e)}"],
                table_stats=[],
                query_performance={},
                storage_analysis={},
                last_maintenance=None
            )
    
    def _check_integrity(self, conn: sqlite3.Connection) -> str:
        """Check database integrity"""
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            result = cursor.fetchone()[0]
            
            if result == "ok":
                return "HEALTHY"
            else:
                return f"CORRUPTED: {result}"
                
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def _analyze_tables(self, conn: sqlite3.Connection) -> List[TableStats]:
        """Analyze all tables in the database"""
        table_stats = []
        cursor = conn.cursor()
        
        try:
            # Get all user tables
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            for table_name in tables:
                try:
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                    row_count = cursor.fetchone()[0]
                    
                    # Get table size (approximation)
                    cursor.execute(f"PRAGMA table_info(`{table_name}`)")
                    columns = cursor.fetchall()
                    
                    # Check for primary key
                    has_primary_key = any(col[5] for col in columns)  # pk column
                    
                    # Get index count
                    cursor.execute(f"PRAGMA index_list(`{table_name}`)")
                    indexes = cursor.fetchall()
                    index_count = len(indexes)
                    
                    # Estimate table size (rough calculation)
                    avg_row_size = len(columns) * 50  # Rough estimate
                    size_bytes = row_count * avg_row_size
                    
                    # Check if table was analyzed recently
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_stat1'")
                    has_stats = cursor.fetchone() is not None
                    last_analyzed = datetime.now().isoformat() if has_stats else None
                    
                    # Calculate fragmentation (simplified)
                    fragmentation_level = min(100.0, max(0.0, (size_bytes / 1024 / 1024) * 2))  # Rough estimate
                    
                    table_stats.append(TableStats(
                        name=table_name,
                        row_count=row_count,
                        size_bytes=size_bytes,
                        index_count=index_count,
                        has_primary_key=has_primary_key,
                        fragmentation_level=round(fragmentation_level, 2),
                        last_analyzed=last_analyzed
                    ))
                    
                except Exception as e:
                    print(f"⚠️  Error analyzing table {table_name}: {e}")
                    
        except Exception as e:
            print(f"❌ Error getting table list: {e}")
            
        return table_stats
    
    def _test_query_performance(self, conn: sqlite3.Connection) -> Dict[str, float]:
        """Test common query performance"""
        performance_tests = {}
        cursor = conn.cursor()
        
        test_queries = {
            'simple_select': "SELECT COUNT(*) FROM arrows",
            'join_query': "SELECT COUNT(*) FROM arrows a LEFT JOIN spine_specifications s ON a.id = s.arrow_id",
            'complex_filter': "SELECT COUNT(*) FROM arrows WHERE manufacturer LIKE '%Easton%'",
            'index_scan': "SELECT COUNT(*) FROM sqlite_master"
        }
        
        for test_name, query in test_queries.items():
            try:
                start_time = time.time()
                cursor.execute(query)
                cursor.fetchall()
                execution_time = (time.time() - start_time) * 1000  # ms
                performance_tests[test_name] = round(execution_time, 2)
            except Exception as e:
                performance_tests[test_name] = -1  # Error indicator
                print(f"⚠️  Performance test {test_name} failed: {e}")
        
        return performance_tests
    
    def _analyze_storage(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Analyze database storage characteristics"""
        cursor = conn.cursor()
        storage_info = {}
        
        try:
            # Page size and counts
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA freelist_count")
            free_pages = cursor.fetchone()[0]
            
            # Calculate storage metrics
            total_size = page_size * page_count
            free_size = page_size * free_pages
            used_size = total_size - free_size
            
            storage_info = {
                'page_size': page_size,
                'page_count': page_count,
                'free_pages': free_pages,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'used_size_mb': round(used_size / (1024 * 1024), 2),
                'free_size_mb': round(free_size / (1024 * 1024), 2),
                'fragmentation_percent': round((free_pages / page_count) * 100, 2) if page_count > 0 else 0,
                'efficiency_percent': round((used_size / total_size) * 100, 2) if total_size > 0 else 0
            }
            
        except Exception as e:
            print(f"⚠️  Storage analysis error: {e}")
            storage_info = {
                'page_size': 0,
                'page_count': 0,
                'free_pages': 0,
                'total_size_mb': 0,
                'used_size_mb': 0,
                'free_size_mb': 0,
                'fragmentation_percent': 0,
                'efficiency_percent': 0
            }
        
        return storage_info
    
    def _calculate_performance_score(self, integrity_status: str, table_stats: List[TableStats], 
                                   query_performance: Dict[str, float], storage_analysis: Dict[str, Any]) -> int:
        """Calculate overall performance score (0-100)"""
        score = 100
        
        # Integrity check (40 points)
        if integrity_status != "HEALTHY":
            score -= 40
        
        # Query performance (30 points)
        avg_query_time = sum(t for t in query_performance.values() if t > 0) / len(query_performance) if query_performance else 0
        if avg_query_time > 1000:  # > 1 second
            score -= 20
        elif avg_query_time > 500:  # > 500ms
            score -= 10
        elif avg_query_time > 100:  # > 100ms
            score -= 5
        
        # Storage efficiency (20 points)
        efficiency = storage_analysis.get('efficiency_percent', 100)
        if efficiency < 70:
            score -= 15
        elif efficiency < 85:
            score -= 10
        elif efficiency < 95:
            score -= 5
        
        # Table health (10 points)
        tables_without_pk = sum(1 for stat in table_stats if not stat.has_primary_key)
        if tables_without_pk > 0:
            score -= min(10, tables_without_pk * 3)
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self, integrity_status: str, table_stats: List[TableStats],
                                query_performance: Dict[str, float], storage_analysis: Dict[str, Any]) -> List[str]:
        """Generate maintenance recommendations"""
        recommendations = []
        
        # Integrity issues
        if integrity_status != "HEALTHY":
            recommendations.append("🚨 CRITICAL: Database integrity issues detected - backup and repair needed")
        
        # Performance issues  
        slow_queries = [name for name, time in query_performance.items() if time > 500]
        if slow_queries:
            recommendations.append(f"⚡ Optimize slow queries: {', '.join(slow_queries)}")
        
        # Storage issues
        fragmentation = storage_analysis.get('fragmentation_percent', 0)
        if fragmentation > 20:
            recommendations.append("🗜️  High fragmentation detected - run VACUUM to reclaim space")
        
        efficiency = storage_analysis.get('efficiency_percent', 100)
        if efficiency < 85:
            recommendations.append("📊 Low storage efficiency - consider database optimization")
        
        # Table issues
        tables_without_pk = [stat.name for stat in table_stats if not stat.has_primary_key]
        if tables_without_pk:
            recommendations.append(f"🔑 Add primary keys to tables: {', '.join(tables_without_pk)}")
        
        large_tables = [stat.name for stat in table_stats if stat.row_count > 100000]
        if large_tables:
            recommendations.append(f"📈 Consider indexing large tables: {', '.join(large_tables)}")
        
        # Maintenance recommendations
        if not self._get_last_maintenance_time():
            recommendations.append("🔧 No recent maintenance detected - schedule regular optimization")
        
        # General health
        if not recommendations:
            recommendations.append("✅ Database is healthy - no immediate action required")
        
        return recommendations
    
    def _get_last_maintenance_time(self) -> Optional[str]:
        """Get timestamp of last maintenance operation"""
        # This would typically check a maintenance log table
        # For now, return None to indicate no maintenance tracking
        return None
    
    def run_database_optimization(self) -> Dict[str, Any]:
        """Run database optimization operations"""
        results = {
            'operations_performed': [],
            'time_taken_ms': 0,
            'space_reclaimed_mb': 0,
            'errors': []
        }
        
        start_time = time.time()
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get size before optimization
            size_before = Path(self.database_path).stat().st_size
            
            print("🔧 Running database optimization...")
            
            # VACUUM - reclaim unused space
            try:
                print("   Running VACUUM...")
                cursor.execute("VACUUM;")
                results['operations_performed'].append('VACUUM')
                print("   ✅ VACUUM completed")
            except Exception as e:
                results['errors'].append(f"VACUUM failed: {str(e)}")
                print(f"   ❌ VACUUM failed: {e}")
            
            # ANALYZE - update table statistics
            try:
                print("   Running ANALYZE...")
                cursor.execute("ANALYZE;")
                results['operations_performed'].append('ANALYZE')
                print("   ✅ ANALYZE completed")
            except Exception as e:
                results['errors'].append(f"ANALYZE failed: {str(e)}")
                print(f"   ❌ ANALYZE failed: {e}")
            
            # REINDEX - rebuild indexes
            try:
                print("   Running REINDEX...")
                cursor.execute("REINDEX;")
                results['operations_performed'].append('REINDEX')
                print("   ✅ REINDEX completed")
            except Exception as e:
                results['errors'].append(f"REINDEX failed: {str(e)}")
                print(f"   ❌ REINDEX failed: {e}")
            
            conn.close()
            
            # Calculate results
            size_after = Path(self.database_path).stat().st_size
            results['space_reclaimed_mb'] = round((size_before - size_after) / (1024 * 1024), 2)
            results['time_taken_ms'] = round((time.time() - start_time) * 1000, 2)
            
            print(f"✅ Optimization completed in {results['time_taken_ms']}ms")
            if results['space_reclaimed_mb'] > 0:
                print(f"   💾 Reclaimed {results['space_reclaimed_mb']} MB of space")
            
        except Exception as e:
            results['errors'].append(f"Optimization failed: {str(e)}")
            print(f"❌ Optimization failed: {e}")
        
        return results
    
    def verify_schema_integrity(self) -> Dict[str, Any]:
        """Verify database schema matches expected structure"""
        verification_results = {
            'schema_valid': True,
            'missing_tables': [],
            'missing_columns': [],
            'extra_tables': [],
            'schema_version': None,
            'recommendations': []
        }
        
        # Expected schema definition - Updated August 2025 to match current production schema
        expected_schema = {
            'arrows': [
                'id', 'manufacturer', 'model_name', 'material', 'carbon_content',
                'arrow_type', 'description', 'image_url', 'source_url', 'scraped_at', 
                'created_at', 'retailer_data', 'manufacturer_id'
            ],
            'spine_specifications': [
                'id', 'arrow_id', 'spine', 'outer_diameter', 'gpi_weight', 
                'inner_diameter', 'diameter_category', 'length_options', 
                'wall_thickness', 'insert_weight_range', 'nock_size', 'notes',
                'straightness_tolerance', 'weight_tolerance', 'created_at'
            ]
        }
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get actual tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            actual_tables = set(row[0] for row in cursor.fetchall())
            
            expected_tables = set(expected_schema.keys())
            
            # Check for missing and extra tables
            verification_results['missing_tables'] = list(expected_tables - actual_tables)
            verification_results['extra_tables'] = list(actual_tables - expected_tables)
            
            # Check columns for existing tables
            for table_name in expected_tables.intersection(actual_tables):
                cursor.execute(f"PRAGMA table_info(`{table_name}`)")
                actual_columns = set(row[1] for row in cursor.fetchall())
                expected_columns = set(expected_schema[table_name])
                
                missing_cols = expected_columns - actual_columns
                if missing_cols:
                    verification_results['missing_columns'].extend([
                        f"{table_name}.{col}" for col in missing_cols
                    ])
            
            # Determine if schema is valid
            verification_results['schema_valid'] = (
                not verification_results['missing_tables'] and
                not verification_results['missing_columns']
            )
            
            # Generate recommendations
            if verification_results['missing_tables']:
                verification_results['recommendations'].append(
                    f"Create missing tables: {', '.join(verification_results['missing_tables'])}"
                )
            
            if verification_results['missing_columns']:
                verification_results['recommendations'].append(
                    f"Add missing columns: {', '.join(verification_results['missing_columns'])}"
                )
            
            if verification_results['extra_tables']:
                verification_results['recommendations'].append(
                    f"Review extra tables: {', '.join(verification_results['extra_tables'])}"
                )
            
            conn.close()
            
        except Exception as e:
            verification_results['schema_valid'] = False
            verification_results['recommendations'].append(f"Schema verification failed: {str(e)}")
        
        return verification_results

# Convenience function for API usage
def run_health_check(database_path: str = None) -> Dict[str, Any]:
    """Run health check and return results as dictionary"""
    checker = DatabaseHealthChecker(database_path)
    report = checker.run_comprehensive_health_check()
    
    # Convert dataclasses to dictionaries for JSON serialization
    return {
        'database_path': report.database_path,
        'database_size_mb': report.database_size_mb,
        'total_tables': report.total_tables,
        'total_indexes': report.total_indexes,
        'integrity_status': report.integrity_status,
        'performance_score': report.performance_score,
        'recommendations': report.recommendations,
        'table_stats': [
            {
                'name': stat.name,
                'row_count': stat.row_count,
                'size_bytes': stat.size_bytes,
                'index_count': stat.index_count,
                'has_primary_key': stat.has_primary_key,
                'fragmentation_level': stat.fragmentation_level,
                'last_analyzed': stat.last_analyzed
            }
            for stat in report.table_stats
        ],
        'query_performance': report.query_performance,
        'storage_analysis': report.storage_analysis,
        'last_maintenance': report.last_maintenance
    }

# For testing
if __name__ == "__main__":
    print("🧪 Testing Database Health Checker")
    print("=" * 50)
    
    checker = DatabaseHealthChecker()
    report = checker.run_comprehensive_health_check()
    
    print(f"\n📊 Health Report Summary:")
    print(f"Database: {report.database_path}")
    print(f"Size: {report.database_size_mb} MB")
    print(f"Performance Score: {report.performance_score}/100")
    print(f"Status: {report.integrity_status}")
    print(f"\nRecommendations:")
    for rec in report.recommendations:
        print(f"  • {rec}")