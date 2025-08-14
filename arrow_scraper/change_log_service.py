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
from user_database import UserDatabase


class ChangeLogService:
    """Service for logging and retrieving equipment and setup changes"""
    
    def __init__(self):
        self.user_db = UserDatabase()
    
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
                (bow_setup_id, equipment_id, user_id, change_type, field_name, 
                 old_value, new_value, change_description, change_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (bow_setup_id, equipment_id, user_id, change_type, field_name,
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
                    ecl.equipment_id,
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
                LEFT JOIN bow_equipment be ON ecl.equipment_id = be.id
                WHERE ecl.bow_setup_id = ? {date_filter}
                
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
                LEFT JOIN bow_equipment be ON ecl.equipment_id = be.id
                WHERE ecl.equipment_id = ?
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
            cursor.execute('''
                INSERT INTO arrow_change_log
                (bow_setup_id, arrow_id, user_id, change_type, field_name,
                 old_value, new_value, change_description, user_note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (bow_setup_id, arrow_id, user_id, change_type, field_name,
                  old_value, new_value, change_description, user_note))
            
            change_log_id = cursor.lastrowid
            conn.commit()
            
            print(f"📝 Logged arrow change: {change_type} for arrow {arrow_id}")
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
            
            # Use the unified view we created
            cursor.execute(f'''
                SELECT * FROM unified_change_history
                WHERE bow_setup_id = ? {date_filter}
                ORDER BY created_at DESC
                LIMIT ?
            ''', params + [limit])
            
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
                    SELECT id FROM equipment_change_log WHERE bow_setup_id = ?
                    UNION ALL 
                    SELECT id FROM setup_change_log WHERE bow_setup_id = ?
                    UNION ALL
                    SELECT id FROM arrow_change_log WHERE bow_setup_id = ?
                )
            ''', (bow_setup_id, bow_setup_id, bow_setup_id))
            stats['total_changes'] = cursor.fetchone()['total']
            
            # Changes by type (equipment)
            cursor.execute('''
                SELECT change_type, COUNT(*) as count
                FROM equipment_change_log 
                WHERE bow_setup_id = ?
                GROUP BY change_type
            ''', (bow_setup_id,))
            stats['equipment_changes_by_type'] = {row['change_type']: row['count'] for row in cursor.fetchall()}
            
            # Arrow changes by type
            cursor.execute('''
                SELECT change_type, COUNT(*) as count
                FROM arrow_change_log 
                WHERE bow_setup_id = ?
                GROUP BY change_type
            ''', (bow_setup_id,))
            stats['arrow_changes_by_type'] = {row['change_type']: row['count'] for row in cursor.fetchall()}
            
            # Recent activity (last 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)
            cursor.execute('''
                SELECT COUNT(*) as recent FROM (
                    SELECT id FROM equipment_change_log 
                    WHERE bow_setup_id = ? AND created_at >= ?
                    UNION ALL
                    SELECT id FROM setup_change_log 
                    WHERE bow_setup_id = ? AND created_at >= ?
                    UNION ALL
                    SELECT id FROM arrow_change_log 
                    WHERE bow_setup_id = ? AND created_at >= ?
                )
            ''', (bow_setup_id, cutoff_date.isoformat(), bow_setup_id, cutoff_date.isoformat(), bow_setup_id, cutoff_date.isoformat()))
            stats['changes_last_30_days'] = cursor.fetchone()['recent']
            
            # Most modified equipment
            cursor.execute('''
                SELECT 
                    ecl.equipment_id,
                    COUNT(*) as change_count,
                    be.manufacturer_name,
                    be.model_name,
                    be.category_name
                FROM equipment_change_log ecl
                LEFT JOIN bow_equipment be ON ecl.equipment_id = be.id
                WHERE ecl.bow_setup_id = ?
                GROUP BY ecl.equipment_id
                ORDER BY change_count DESC
                LIMIT 5
            ''', (bow_setup_id,))
            stats['most_modified_equipment'] = [dict(row) for row in cursor.fetchall()]
            
            # Most modified arrows
            cursor.execute('''
                SELECT 
                    acl.arrow_id,
                    COUNT(*) as change_count
                FROM arrow_change_log acl
                WHERE acl.bow_setup_id = ?
                GROUP BY acl.arrow_id
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