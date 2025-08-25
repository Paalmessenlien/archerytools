#!/usr/bin/env python3
"""
Change Log Service for Equipment Management System

This service provides comprehensive change logging functionality for:
- Equipment modifications (add, remove, settings changes)
- Setup changes (name, description, configuration)
- Historical tracking with before/after values
- Change retrieval and filtering capabilities
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from unified_database import UnifiedDatabase


class ChangeLogService:
    """Service for logging and retrieving equipment and setup changes"""
    
    def __init__(self):
        self.user_db = UnifiedDatabase()
    
    def log_equipment_change(self, 
                           bow_setup_id: int,
                           equipment_id: int, 
                           user_id: int,
                           change_type: str,
                           field_name: str = None,
                           old_value: str = None,
                           new_value: str = None,
                           change_description: str = None,
                           change_reason: str = None) -> int:
        """
        Log an equipment change
        
        Args:
            bow_setup_id: ID of the bow setup
            equipment_id: ID of the equipment (bow_equipment table ID)
            user_id: ID of the user making the change
            change_type: Type of change ('add', 'remove', 'modify', 'settings_change', 'activation_change')
            field_name: Specific field that changed (optional)
            old_value: Previous value (optional)
            new_value: New value (optional)
            change_description: Human-readable description of the change
            change_reason: User-provided reason for the change
        
        Returns:
            ID of the created change log entry
        """
        conn = self.user_db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO equipment_change_log 
                (bow_equipment_id, user_id, change_type, field_name, 
                 old_value, new_value, change_description, change_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (equipment_id, user_id, change_type, field_name,
                  old_value, new_value, change_description, change_reason))
            
            change_log_id = cursor.lastrowid
            conn.commit()
            
            print(f"📝 Logged equipment change: {change_type} for equipment {equipment_id}")
            return change_log_id
            
        except sqlite3.Error as e:
            print(f"❌ Error logging equipment change: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def log_setup_change(self,
                        bow_setup_id: int,
                        user_id: int, 
                        change_type: str,
                        field_name: str = None,
                        old_value: str = None,
                        new_value: str = None,
                        change_description: str = None) -> int:
        """
        Log a setup-level change
        
        Args:
            bow_setup_id: ID of the bow setup
            user_id: ID of the user making the change
            change_type: Type of change ('setup_modified', 'name_changed', 'description_changed', 'bow_info_changed', 'created')
            field_name: Specific field that changed (optional)
            old_value: Previous value (optional) 
            new_value: New value (optional)
            change_description: Human-readable description of the change
        
        Returns:
            ID of the created change log entry
        """
        conn = self.user_db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO setup_change_log
                (bow_setup_id, user_id, change_type, field_name,
                 old_value, new_value, change_description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (bow_setup_id, user_id, change_type, field_name,
                  old_value, new_value, change_description))
            
            change_log_id = cursor.lastrowid
            conn.commit()
            
            print(f"📝 Logged setup change: {change_type} for setup {bow_setup_id}")
            return change_log_id
            
        except sqlite3.Error as e:
            print(f"❌ Error logging setup change: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def log_equipment_field_changes(self,
                                  bow_setup_id: int,
                                  equipment_id: int,
                                  user_id: int,
                                  old_data: Dict[str, Any],
                                  new_data: Dict[str, Any],
                                  change_reason: str = None) -> List[int]:
        """
        Compare old and new equipment data and log individual field changes
        
        Args:
            bow_setup_id: ID of the bow setup
            equipment_id: ID of the equipment
            user_id: ID of the user making changes
            old_data: Dictionary of old equipment values
            new_data: Dictionary of new equipment values  
            change_reason: User-provided reason for changes
        
        Returns:
            List of change log entry IDs created
        """
        change_log_ids = []
        
        # Define fields to track for changes
        trackable_fields = {
            'installation_notes': 'Installation Notes',
            'custom_specifications': 'Custom Specifications', 
            'is_active': 'Active Status',
            'manufacturer_name': 'Manufacturer',
            'model_name': 'Model Name',
            'category_name': 'Category'
        }
        
        for field, display_name in trackable_fields.items():
            old_val = old_data.get(field)
            new_val = new_data.get(field)
            
            # Skip if values are the same
            if old_val == new_val:
                continue
            
            # Handle JSON fields
            if field == 'custom_specifications':
                if isinstance(old_val, str):
                    try:
                        old_val = json.loads(old_val) if old_val else {}
                    except json.JSONDecodeError:
                        old_val = {}
                if isinstance(new_val, str):
                    try:
                        new_val = json.loads(new_val) if new_val else {}
                    except json.JSONDecodeError:
                        new_val = {}
                
                # For specifications, log detailed changes
                if old_val != new_val:
                    change_description = f"{display_name} updated"
                    if isinstance(new_val, dict) and isinstance(old_val, dict):
                        # Track specific specification changes
                        for spec_key, spec_val in new_val.items():
                            if old_val.get(spec_key) != spec_val:
                                spec_change_id = self.log_equipment_change(
                                    bow_setup_id, equipment_id, user_id,
                                    'settings_change', f'spec_{spec_key}',
                                    str(old_val.get(spec_key, '')), str(spec_val),
                                    f"Specification '{spec_key}' changed",
                                    change_reason
                                )
                                change_log_ids.append(spec_change_id)
                    else:
                        # Log general specification change
                        change_id = self.log_equipment_change(
                            bow_setup_id, equipment_id, user_id,
                            'settings_change', field,
                            str(old_val), str(new_val),
                            change_description, change_reason
                        )
                        change_log_ids.append(change_id)
            else:
                # Log regular field changes
                change_description = f"{display_name} changed from '{old_val}' to '{new_val}'"
                change_id = self.log_equipment_change(
                    bow_setup_id, equipment_id, user_id,
                    'modify', field,
                    str(old_val) if old_val is not None else None,
                    str(new_val) if new_val is not None else None,
                    change_description, change_reason
                )
                change_log_ids.append(change_id)
        
        return change_log_ids
    
    def get_setup_change_history(self, 
                                bow_setup_id: int, 
                                user_id: int,
                                limit: int = 50,
                                days_back: int = None) -> List[Dict[str, Any]]:
        """
        Get complete change history for a bow setup
        
        Args:
            bow_setup_id: ID of the bow setup
            user_id: ID of the user (for access control)
            limit: Maximum number of changes to return
            days_back: Only return changes from this many days back
        
        Returns:
            List of change entries with metadata
        """
        conn = self.user_db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Verify user has access to this setup
            cursor.execute('SELECT user_id FROM bow_setups WHERE id = ?', (bow_setup_id,))
            setup = cursor.fetchone()
            if not setup or setup['user_id'] != user_id:
                return []
            
            # Build date filter
            date_filter = ""
            params = [bow_setup_id]
            if days_back:
                cutoff_date = datetime.now() - timedelta(days=days_back)
                date_filter = "AND created_at >= ?"
                params.append(cutoff_date.isoformat())
            
            # Get equipment changes
            cursor.execute(f'''
                SELECT 
                    'equipment' as change_source,
                    ecl.id,
                    ecl.bow_equipment_id as equipment_id,
                    ecl.change_type,
                    ecl.field_name,
                    ecl.old_value,
                    ecl.new_value,
                    ecl.change_description,
                    ecl.change_reason,
                    ecl.created_at,
                    be.manufacturer_name,
                    be.model_name,
                    be.category_name
                FROM equipment_change_log ecl
                LEFT JOIN bow_equipment be ON ecl.bow_equipment_id = be.id
                JOIN bow_setups bs ON be.bow_setup_id = bs.id
                WHERE bs.id = ? {date_filter}
                
                UNION ALL
                
                SELECT 
                    'setup' as change_source,
                    scl.id,
                    NULL as equipment_id,
                    scl.change_type,
                    scl.field_name,
                    scl.old_value,
                    scl.new_value,
                    scl.change_description,
                    NULL as change_reason,
                    scl.created_at,
                    NULL as manufacturer_name,
                    NULL as model_name,
                    NULL as category_name
                FROM setup_change_log scl
                WHERE scl.bow_setup_id = ? {date_filter}
                
                ORDER BY created_at DESC
                LIMIT ?
            ''', params + [bow_setup_id] + (params[1:] if days_back else []) + [limit])
            
            changes = []
            for row in cursor.fetchall():
                change = dict(row)
                # Parse timestamp
                change['created_at'] = datetime.fromisoformat(change['created_at'])
                changes.append(change)
            
            return changes
            
        except sqlite3.Error as e:
            print(f"❌ Error getting change history: {e}")
            return []
        finally:
            conn.close()
    
    def get_equipment_change_history(self,
                                   equipment_id: int,
                                   user_id: int,
                                   limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get change history for a specific piece of equipment
        
        Args:
            equipment_id: ID of the equipment (bow_equipment table)
            user_id: ID of the user (for access control)
            limit: Maximum number of changes to return
        
        Returns:
            List of change entries for the equipment
        """
        conn = self.user_db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Verify user has access to this equipment
            cursor.execute('''
                SELECT be.bow_setup_id, bs.user_id 
                FROM bow_equipment be
                JOIN bow_setups bs ON be.bow_setup_id = bs.id
                WHERE be.id = ?
            ''', (equipment_id,))
            equipment = cursor.fetchone()
            if not equipment or equipment['user_id'] != user_id:
                return []
            
            # Get changes for this equipment
            cursor.execute('''
                SELECT 
                    ecl.*,
                    be.manufacturer_name,
                    be.model_name,
                    be.category_name
                FROM equipment_change_log ecl
                LEFT JOIN bow_equipment be ON ecl.bow_equipment_id = be.id
                WHERE ecl.bow_equipment_id = ?
                ORDER BY ecl.created_at DESC
                LIMIT ?
            ''', (equipment_id, limit))
            
            changes = []
            for row in cursor.fetchall():
                change = dict(row)
                change['created_at'] = datetime.fromisoformat(change['created_at'])
                changes.append(change)
            
            return changes
            
        except sqlite3.Error as e:
            print(f"❌ Error getting equipment change history: {e}")
            return []
        finally:
            conn.close()
    
    def log_arrow_change(self,
                        bow_setup_id: int,
                        arrow_id: int,
                        user_id: int,
                        change_type: str,
                        field_name: str = None,
                        old_value: str = None,
                        new_value: str = None,
                        change_description: str = None,
                        user_note: str = None) -> int:
        """
        Log an arrow-related change
        
        Args:
            bow_setup_id: ID of the bow setup
            arrow_id: ID of the arrow (from arrows table)
            user_id: ID of the user making the change
            change_type: Type of change ('arrow_added', 'arrow_removed', 'arrow_modified', 'quantity_changed', 'specifications_changed', 'setup_changed')
            field_name: Specific field that changed (optional)
            old_value: Previous value (optional)
            new_value: New value (optional)
            change_description: Human-readable description of the change
            user_note: User-provided note explaining the change
        
        Returns:
            ID of the created change log entry
        """
        conn = self.user_db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Find the setup_arrow_id for this bow_setup and arrow combination
            cursor.execute('''
                SELECT id FROM setup_arrows 
                WHERE setup_id = ? AND arrow_id = ?
                ORDER BY created_at DESC LIMIT 1
            ''', (bow_setup_id, arrow_id))
            
            setup_arrow = cursor.fetchone()
            if not setup_arrow:
                print(f"⚠️ Warning: No setup_arrow found for bow_setup_id={bow_setup_id}, arrow_id={arrow_id}")
                # For removed arrows, we might not find the setup_arrow anymore
                # In this case, we'll create a log entry without setup_arrow_id (set to NULL)
                setup_arrow_id = None
            else:
                setup_arrow_id = setup_arrow['id']
            
            cursor.execute('''
                INSERT INTO arrow_change_log
                (setup_arrow_id, user_id, change_type, field_name,
                 old_value, new_value, change_description, change_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (setup_arrow_id, user_id, change_type, field_name,
                  old_value, new_value, change_description, user_note))
            
            change_log_id = cursor.lastrowid
            conn.commit()
            
            print(f"📝 Logged arrow change: {change_type} for arrow {arrow_id} (setup_arrow_id: {setup_arrow_id})")
            return change_log_id
            
        except sqlite3.Error as e:
            print(f"❌ Error logging arrow change: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def log_arrow_field_changes(self,
                               bow_setup_id: int,
                               arrow_id: int,
                               user_id: int,
                               old_data: Dict[str, Any],
                               new_data: Dict[str, Any],
                               user_note: str = None) -> List[int]:
        """
        Compare old and new arrow data and log individual field changes
        
        Args:
            bow_setup_id: ID of the bow setup
            arrow_id: ID of the arrow
            user_id: ID of the user making changes
            old_data: Dictionary of old arrow values
            new_data: Dictionary of new arrow values
            user_note: User-provided note for the changes
        
        Returns:
            List of change log entry IDs created
        """
        change_log_ids = []
        
        # Define fields to track for arrow changes
        trackable_fields = {
            'arrow_length': 'Arrow Length',
            'point_weight': 'Point Weight',
            'nock_weight': 'Nock Weight',
            'fletching_weight': 'Fletching Weight',
            'insert_weight': 'Insert Weight',
            'wrap_weight': 'Wrap Weight',
            'bushing_weight': 'Bushing Weight',
            'notes': 'Notes',
            'calculated_spine': 'Calculated Spine',
            'compatibility_score': 'Compatibility Score'
        }
        
        for field, display_name in trackable_fields.items():
            old_val = old_data.get(field)
            new_val = new_data.get(field)
            
            # Skip if values are the same
            if old_val == new_val:
                continue
            
            # Format values for display
            old_display = str(old_val) if old_val is not None else None
            new_display = str(new_val) if new_val is not None else None
            
            # Create appropriate change description
            if old_val is None:
                change_description = f"{display_name} set to '{new_val}'"
            elif new_val is None:
                change_description = f"{display_name} removed (was '{old_val}')"
            else:
                change_description = f"{display_name} changed from '{old_val}' to '{new_val}'"
            
            change_id = self.log_arrow_change(
                bow_setup_id, arrow_id, user_id,
                'arrow_modified', field,
                old_display, new_display,
                change_description, user_note
            )
            change_log_ids.append(change_id)
        
        return change_log_ids
    
    def get_unified_change_history(self,
                                 bow_setup_id: int,
                                 user_id: int,
                                 limit: int = 50,
                                 days_back: int = None) -> List[Dict[str, Any]]:
        """
        Get unified change history for a bow setup (arrows + equipment + setup)
        
        Args:
            bow_setup_id: ID of the bow setup
            user_id: ID of the user (for access control)
            limit: Maximum number of changes to return
            days_back: Only return changes from this many days back
        
        Returns:
            List of unified change entries with metadata
        """
        conn = self.user_db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Verify user has access to this setup
            cursor.execute('SELECT user_id FROM bow_setups WHERE id = ?', (bow_setup_id,))
            setup = cursor.fetchone()
            if not setup or setup['user_id'] != user_id:
                return []
            
            # Build date filter
            date_filter = ""
            params = [bow_setup_id]
            if days_back:
                cutoff_date = datetime.now() - timedelta(days=days_back)
                date_filter = "AND created_at >= ?"
                params.append(cutoff_date.isoformat())
            
            # Get unified changes with UNION query instead of view
            cursor.execute(f'''
                SELECT 
                    'equipment' as change_source,
                    ecl.id,
                    ecl.bow_equipment_id as item_id,
                    ecl.change_type,
                    ecl.field_name,
                    ecl.old_value,
                    ecl.new_value,
                    ecl.change_description,
                    ecl.change_reason,
                    ecl.created_at,
                    be.manufacturer_name,
                    be.model_name,
                    be.category_name
                FROM equipment_change_log ecl
                LEFT JOIN bow_equipment be ON ecl.bow_equipment_id = be.id
                JOIN bow_setups bs ON be.bow_setup_id = bs.id
                WHERE bs.id = ? {date_filter}
                
                UNION ALL
                
                SELECT 
                    'setup' as change_source,
                    scl.id,
                    NULL as item_id,
                    scl.change_type,
                    scl.field_name,
                    scl.old_value,
                    scl.new_value,
                    scl.change_description,
                    NULL as change_reason,
                    scl.created_at,
                    NULL as manufacturer_name,
                    NULL as model_name,
                    NULL as category_name
                FROM setup_change_log scl
                WHERE scl.bow_setup_id = ? {date_filter}
                
                UNION ALL
                
                SELECT 
                    'arrow' as change_source,
                    acl.id,
                    sa.arrow_id as item_id,
                    acl.change_type,
                    acl.field_name,
                    acl.old_value,
                    acl.new_value,
                    acl.change_description,
                    acl.change_reason,
                    acl.created_at,
                    a.manufacturer as manufacturer_name,
                    a.model_name,
                    NULL as category_name
                FROM arrow_change_log acl
                LEFT JOIN setup_arrows sa ON acl.setup_arrow_id = sa.id
                LEFT JOIN arrows a ON sa.arrow_id = a.id
                WHERE sa.setup_id = ? {date_filter}
                
                ORDER BY created_at DESC
                LIMIT ?
            ''', params + [bow_setup_id] + (params[1:] if days_back else []) + [bow_setup_id] + (params[1:] if days_back else []) + [limit])
            
            changes = []
            for row in cursor.fetchall():
                change = dict(row)
                # Parse timestamp if it's a string
                if isinstance(change['created_at'], str):
                    change['created_at'] = datetime.fromisoformat(change['created_at'])
                changes.append(change)
            
            return changes
            
        except sqlite3.Error as e:
            print(f"❌ Error getting unified change history: {e}")
            return []
        finally:
            conn.close()

    def log_tuning_test(self,
                       test_result_id: int,
                       user_id: int,
                       test_type: str,
                       arrow_id: int,
                       bow_setup_id: int,
                       test_number: int,
                       confidence_score: float,
                       change_description: str = None,
                       recommendations_count: int = 0,
                       conn=None) -> int:
        """
        Log a tuning test completion event
        
        Args:
            test_result_id: ID of the test result from tuning_test_results table
            user_id: ID of the user performing the test
            test_type: Type of tuning test ('paper_tuning', 'bareshaft_tuning', 'walkback_tuning')
            arrow_id: ID of the arrow being tested
            bow_setup_id: ID of the bow setup used
            test_number: Sequential test number for this arrow/bow combination
            confidence_score: Confidence score of the test result (0-100)
            change_description: Optional description of what was tested/changed
            recommendations_count: Number of recommendations generated
            conn: Optional existing database connection to reuse
        
        Returns:
            ID of the created change log entry
        """
        # Use provided connection or create new one
        if conn is None:
            conn = self.user_db.get_connection()
            should_close_conn = True
        else:
            should_close_conn = False
        
        cursor = conn.cursor()
        
        try:
            # Create a descriptive change description if none provided
            if not change_description:
                test_type_names = {
                    'paper_tuning': 'Paper Tuning',
                    'bareshaft_tuning': 'Bareshaft Tuning', 
                    'walkback_tuning': 'Walkback Tuning'
                }
                test_name = test_type_names.get(test_type, test_type)
                change_description = f"{test_name} test #{test_number} completed with {confidence_score:.1f}% confidence"
                if recommendations_count > 0:
                    change_description += f" and {recommendations_count} recommendations"
            
            # Create before_state with test details as JSON
            before_state = json.dumps({
                'test_type': test_type,
                'test_number': test_number,
                'confidence_score': confidence_score,
                'recommendations_count': recommendations_count
            })
            
            # Use the actual table schema from migration 035
            cursor.execute('''
                INSERT INTO tuning_change_log
                (user_id, arrow_id, bow_setup_id, test_result_id, change_type, description, before_state)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, arrow_id, bow_setup_id, test_result_id, 'test_completed', change_description, before_state))
            
            change_log_id = cursor.lastrowid
            
            # Only commit if we own the connection
            if should_close_conn:
                conn.commit()
            
            print(f"📝 Logged tuning test: {test_type} #{test_number} for arrow {arrow_id} (confidence: {confidence_score:.1f}%)")
            return change_log_id
            
        except sqlite3.Error as e:
            print(f"❌ Error logging tuning test: {e}")
            if should_close_conn:
                conn.rollback()
            raise
        finally:
            if should_close_conn:
                conn.close()
    
    def log_tuning_adjustment(self,
                            user_id: int,
                            bow_setup_id: int,
                            component: str,
                            adjustment_type: str,
                            old_value: str = None,
                            new_value: str = None,
                            reason: str = None,
                            test_result_id: int = None) -> int:
        """
        Log a tuning adjustment made based on test results
        
        Args:
            user_id: ID of the user making the adjustment
            bow_setup_id: ID of the bow setup being adjusted
            component: Equipment component being adjusted (e.g., 'rest', 'nock', 'sight')
            adjustment_type: Type of adjustment ('moved_left', 'moved_right', 'moved_up', 'moved_down', 'increased', 'decreased', 'replaced')
            old_value: Previous setting/value
            new_value: New setting/value 
            reason: Reason for adjustment (e.g., 'Paper tear showed right impact')
            test_result_id: ID of test result that prompted this adjustment
        
        Returns:
            ID of the created adjustment log entry
        """
        conn = self.user_db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO equipment_adjustment_log
                (user_id, bow_setup_id, component, adjustment_type,
                 old_value, new_value, reason, test_result_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, bow_setup_id, component, adjustment_type,
                  old_value, new_value, reason, test_result_id))
            
            adjustment_log_id = cursor.lastrowid
            conn.commit()
            
            print(f"📝 Logged tuning adjustment: {component} {adjustment_type} (bow setup {bow_setup_id})")
            return adjustment_log_id
            
        except sqlite3.Error as e:
            print(f"❌ Error logging tuning adjustment: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_tuning_history(self,
                          arrow_id: int = None,
                          bow_setup_id: int = None,
                          user_id: int = None,
                          test_type: str = None,
                          limit: int = 50,
                          days_back: int = None) -> List[Dict[str, Any]]:
        """
        Get tuning test history with optional filters
        
        Args:
            arrow_id: Filter by specific arrow ID
            bow_setup_id: Filter by specific bow setup ID
            user_id: Filter by user ID (required for access control)
            test_type: Filter by test type
            limit: Maximum number of results
            days_back: Only return tests from this many days back
        
        Returns:
            List of tuning test history entries
        """
        conn = self.user_db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Build WHERE clause
            where_conditions = []
            params = []
            
            if user_id:
                where_conditions.append("tcl.user_id = ?")
                params.append(user_id)
            
            if arrow_id:
                where_conditions.append("tcl.arrow_id = ?")
                params.append(arrow_id)
            
            if bow_setup_id:
                where_conditions.append("tcl.bow_setup_id = ?")
                params.append(bow_setup_id)
                
            if test_type:
                where_conditions.append("tcl.test_type = ?")
                params.append(test_type)
            
            if days_back:
                cutoff_date = datetime.now() - timedelta(days=days_back)
                where_conditions.append("tcl.created_at >= ?")
                params.append(cutoff_date.isoformat())
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            cursor.execute(f'''
                SELECT 
                    tcl.*,
                    bs.name as bow_setup_name,
                    a.manufacturer,
                    a.model_name,
                    ttr.test_data,
                    ttr.environmental_conditions,
                    ttr.shooting_distance,
                    ttr.notes
                FROM tuning_change_log tcl
                LEFT JOIN bow_setups bs ON tcl.bow_setup_id = bs.id
                LEFT JOIN arrows a ON tcl.arrow_id = a.id  
                LEFT JOIN tuning_test_results ttr ON tcl.test_result_id = ttr.id
                {where_clause}
                ORDER BY tcl.created_at DESC
                LIMIT ?
            ''', params + [limit])
            
            tests = []
            for row in cursor.fetchall():
                test = dict(row)
                # Parse timestamp if it's a string
                if isinstance(test['created_at'], str):
                    test['created_at'] = datetime.fromisoformat(test['created_at'])
                    
                # Parse JSON fields
                if test['test_data']:
                    try:
                        test['test_data'] = json.loads(test['test_data']) if isinstance(test['test_data'], str) else test['test_data']
                    except (json.JSONDecodeError, TypeError):
                        test['test_data'] = {}
                        
                if test['environmental_conditions']:
                    try:
                        test['environmental_conditions'] = json.loads(test['environmental_conditions']) if isinstance(test['environmental_conditions'], str) else test['environmental_conditions']
                    except (json.JSONDecodeError, TypeError):
                        test['environmental_conditions'] = {}
                        
                tests.append(test)
            
            return tests
            
        except sqlite3.Error as e:
            print(f"❌ Error getting tuning history: {e}")
            return []
        finally:
            conn.close()
    
    def get_adjustment_history(self,
                             bow_setup_id: int = None,
                             user_id: int = None,
                             component: str = None,
                             limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get equipment adjustment history
        
        Args:
            bow_setup_id: Filter by bow setup ID
            user_id: Filter by user ID (required for access control)
            component: Filter by component type
            limit: Maximum number of results
        
        Returns:
            List of adjustment history entries
        """
        conn = self.user_db.get_connection()
        cursor = conn.cursor()
        
        try:
            where_conditions = []
            params = []
            
            if user_id:
                where_conditions.append("eal.user_id = ?")
                params.append(user_id)
                
            if bow_setup_id:
                where_conditions.append("eal.bow_setup_id = ?")
                params.append(bow_setup_id)
                
            if component:
                where_conditions.append("eal.component = ?")
                params.append(component)
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            cursor.execute(f'''
                SELECT 
                    eal.*,
                    bs.name as bow_setup_name,
                    tcl.test_type as related_test_type,
                    tcl.test_number as related_test_number
                FROM equipment_adjustment_log eal
                LEFT JOIN bow_setups bs ON eal.bow_setup_id = bs.id
                LEFT JOIN tuning_change_log tcl ON eal.test_result_id = tcl.test_result_id
                {where_clause}
                ORDER BY eal.created_at DESC
                LIMIT ?
            ''', params + [limit])
            
            adjustments = []
            for row in cursor.fetchall():
                adjustment = dict(row)
                if isinstance(adjustment['created_at'], str):
                    adjustment['created_at'] = datetime.fromisoformat(adjustment['created_at'])
                adjustments.append(adjustment)
            
            return adjustments
            
        except sqlite3.Error as e:
            print(f"❌ Error getting adjustment history: {e}")
            return []
        finally:
            conn.close()

    def get_change_statistics(self, 
                            bow_setup_id: int, 
                            user_id: int) -> Dict[str, Any]:
        """
        Get statistics about changes made to a bow setup
        
        Args:
            bow_setup_id: ID of the bow setup
            user_id: ID of the user (for access control)
        
        Returns:
            Dictionary with change statistics
        """
        conn = self.user_db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Verify access
            cursor.execute('SELECT user_id FROM bow_setups WHERE id = ?', (bow_setup_id,))
            setup = cursor.fetchone()
            if not setup or setup['user_id'] != user_id:
                return {}
            
            stats = {}
            
            # Total changes (including arrows)
            cursor.execute('''
                SELECT COUNT(*) as total FROM (
                    SELECT ecl.id 
                    FROM equipment_change_log ecl
                    JOIN bow_equipment be ON ecl.bow_equipment_id = be.id
                    WHERE be.bow_setup_id = ?
                    UNION ALL 
                    SELECT id FROM setup_change_log WHERE bow_setup_id = ?
                    UNION ALL
                    SELECT acl.id 
                    FROM arrow_change_log acl
                    JOIN setup_arrows sa ON acl.setup_arrow_id = sa.id
                    WHERE sa.setup_id = ?
                )
            ''', (bow_setup_id, bow_setup_id, bow_setup_id))
            stats['total_changes'] = cursor.fetchone()['total']
            
            # Changes by type (equipment)
            cursor.execute('''
                SELECT ecl.change_type, COUNT(*) as count
                FROM equipment_change_log ecl
                JOIN bow_equipment be ON ecl.bow_equipment_id = be.id
                WHERE be.bow_setup_id = ?
                GROUP BY ecl.change_type
            ''', (bow_setup_id,))
            stats['equipment_changes_by_type'] = {row['change_type']: row['count'] for row in cursor.fetchall()}
            
            # Arrow changes by type
            cursor.execute('''
                SELECT acl.change_type, COUNT(*) as count
                FROM arrow_change_log acl
                JOIN setup_arrows sa ON acl.setup_arrow_id = sa.id
                WHERE sa.setup_id = ?
                GROUP BY acl.change_type
            ''', (bow_setup_id,))
            stats['arrow_changes_by_type'] = {row['change_type']: row['count'] for row in cursor.fetchall()}
            
            # Recent activity (last 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)
            cursor.execute('''
                SELECT COUNT(*) as recent FROM (
                    SELECT ecl.id 
                    FROM equipment_change_log ecl
                    JOIN bow_equipment be ON ecl.bow_equipment_id = be.id
                    WHERE be.bow_setup_id = ? AND ecl.created_at >= ?
                    UNION ALL
                    SELECT id FROM setup_change_log 
                    WHERE bow_setup_id = ? AND created_at >= ?
                    UNION ALL
                    SELECT acl.id 
                    FROM arrow_change_log acl
                    JOIN setup_arrows sa ON acl.setup_arrow_id = sa.id
                    WHERE sa.setup_id = ? AND acl.created_at >= ?
                )
            ''', (bow_setup_id, cutoff_date.isoformat(), bow_setup_id, cutoff_date.isoformat(), bow_setup_id, cutoff_date.isoformat()))
            stats['changes_last_30_days'] = cursor.fetchone()['recent']
            
            # Most modified equipment
            cursor.execute('''
                SELECT 
                    ecl.bow_equipment_id as equipment_id,
                    COUNT(*) as change_count,
                    be.manufacturer_name,
                    be.model_name,
                    be.category_name
                FROM equipment_change_log ecl
                LEFT JOIN bow_equipment be ON ecl.bow_equipment_id = be.id
                WHERE be.bow_setup_id = ?
                GROUP BY ecl.bow_equipment_id
                ORDER BY change_count DESC
                LIMIT 5
            ''', (bow_setup_id,))
            stats['most_modified_equipment'] = [dict(row) for row in cursor.fetchall()]
            
            # Most modified arrows
            cursor.execute('''
                SELECT 
                    sa.arrow_id,
                    COUNT(*) as change_count
                FROM arrow_change_log acl
                JOIN setup_arrows sa ON acl.setup_arrow_id = sa.id
                WHERE sa.setup_id = ?
                GROUP BY sa.arrow_id
                ORDER BY change_count DESC
                LIMIT 5
            ''', (bow_setup_id,))
            stats['most_modified_arrows'] = [dict(row) for row in cursor.fetchall()]
            
            return stats
            
        except sqlite3.Error as e:
            print(f"❌ Error getting change statistics: {e}")
            return {}
        finally:
            conn.close()