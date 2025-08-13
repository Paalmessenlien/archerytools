#!/usr/bin/env python3
"""
Equipment Learning Manager

Handles auto-learning functionality for manufacturers and models:
- Captures new manufacturer and model entries
- Provides intelligent suggestions based on usage patterns
- Manages manufacturer approval workflow
- Tracks equipment usage statistics

Created: August 2025
"""

import sqlite3
import json
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from user_database import UserDatabase

class EquipmentLearningManager:
    """Manages auto-learning of manufacturers and equipment models"""
    
    def __init__(self):
        self.user_db = UserDatabase()
    
    def learn_equipment_entry(self, manufacturer_name: str, model_name: str, 
                            category_name: str, user_id: int) -> Dict:
        """
        Learn from user equipment entry and update learning tables
        Returns info about what was learned
        """
        conn = self.user_db.get_connection()
        cursor = conn.cursor()
        
        learning_info = {
            'new_manufacturer': False,
            'new_model': False,
            'manufacturer_status': None,
            'model_usage_count': 0
        }
        
        try:
            # Check if this is a new manufacturer
            from arrow_database import ArrowDatabase
            arrow_db = ArrowDatabase()
            arrow_conn = arrow_db.get_connection()
            arrow_cursor = arrow_conn.cursor()
            
            # Check if manufacturer exists in main database
            arrow_cursor.execute('SELECT id FROM manufacturers WHERE LOWER(name) = LOWER(?)', 
                               (manufacturer_name,))
            existing_manufacturer = arrow_cursor.fetchone()
            arrow_conn.close()
            
            if not existing_manufacturer:
                # Check if it's already in pending manufacturers
                cursor.execute('''
                    SELECT id, usage_count FROM pending_manufacturers 
                    WHERE LOWER(name) = LOWER(?)
                ''', (manufacturer_name,))
                pending = cursor.fetchone()
                
                if pending:
                    # Update usage count for existing pending manufacturer
                    cursor.execute('''
                        UPDATE pending_manufacturers 
                        SET usage_count = usage_count + 1, last_seen = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (pending['id'],))
                    learning_info['manufacturer_status'] = 'pending_updated'
                else:
                    # Add new pending manufacturer
                    cursor.execute('''
                        INSERT INTO pending_manufacturers 
                        (name, category_context, usage_count, created_by_user_id)
                        VALUES (?, ?, 1, ?)
                    ''', (manufacturer_name, category_name, user_id))
                    learning_info['new_manufacturer'] = True
                    learning_info['manufacturer_status'] = 'pending_new'
            else:
                learning_info['manufacturer_status'] = 'existing'
            
            # Learn model name (always do this for usage statistics)
            cursor.execute('''
                INSERT OR REPLACE INTO equipment_models 
                (manufacturer_name, model_name, category_name, usage_count, last_used, created_by_user_id, first_seen)
                VALUES (
                    ?, ?, ?, 
                    COALESCE((SELECT usage_count FROM equipment_models 
                             WHERE manufacturer_name = ? AND model_name = ? AND category_name = ?), 0) + 1,
                    CURRENT_TIMESTAMP,
                    ?,
                    COALESCE((SELECT first_seen FROM equipment_models 
                             WHERE manufacturer_name = ? AND model_name = ? AND category_name = ?), CURRENT_TIMESTAMP)
                )
            ''', (manufacturer_name, model_name, category_name,
                  manufacturer_name, model_name, category_name,
                  user_id,
                  manufacturer_name, model_name, category_name))
            
            # Get the usage count for reporting
            cursor.execute('''
                SELECT usage_count FROM equipment_models 
                WHERE manufacturer_name = ? AND model_name = ? AND category_name = ?
            ''', (manufacturer_name, model_name, category_name))
            usage_result = cursor.fetchone()
            learning_info['model_usage_count'] = usage_result['usage_count'] if usage_result else 1
            
            if learning_info['model_usage_count'] == 1:
                learning_info['new_model'] = True
            
            # Update usage statistics
            self._update_usage_stats(cursor, manufacturer_name, model_name, category_name)
            
            conn.commit()
            
        except Exception as e:
            print(f"Error in equipment learning: {e}")
            conn.rollback()
        finally:
            conn.close()
        
        return learning_info
    
    def get_model_suggestions(self, manufacturer_name: str, category_name: str, 
                            query: str = "", limit: int = 10) -> List[Dict]:
        """
        Get model name suggestions based on manufacturer and category
        Returns models ordered by usage frequency and relevance
        """
        conn = self.user_db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Base query for models
            sql = '''
                SELECT model_name, usage_count, last_used,
                       (usage_count * 0.7 + 
                        (julianday('now') - julianday(last_used)) * -0.3) as relevance_score
                FROM equipment_models 
                WHERE LOWER(manufacturer_name) = LOWER(?) AND category_name = ?
            '''
            params = [manufacturer_name, category_name]
            
            # Add query filtering if provided
            if query:
                sql += ' AND LOWER(model_name) LIKE LOWER(?)'
                params.append(f'%{query}%')
            
            sql += ' ORDER BY relevance_score DESC, usage_count DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            suggestions = []
            for row in results:
                suggestions.append({
                    'model_name': row['model_name'],
                    'usage_count': row['usage_count'],
                    'last_used': row['last_used'],
                    'relevance_score': round(row['relevance_score'], 2)
                })
            
            return suggestions
            
        except Exception as e:
            print(f"Error getting model suggestions: {e}")
            return []
        finally:
            conn.close()
    
    def get_pending_manufacturers(self, status: str = 'pending', limit: int = 50) -> List[Dict]:
        """Get pending manufacturers for admin review"""
        conn = self.user_db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT pm.*, u.name as created_by_name
                FROM pending_manufacturers pm
                LEFT JOIN users u ON pm.created_by_user_id = u.id
                WHERE pm.status = ?
                ORDER BY pm.usage_count DESC, pm.first_seen ASC
                LIMIT ?
            ''', (status, limit))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
            
        except Exception as e:
            print(f"Error getting pending manufacturers: {e}")
            return []
        finally:
            conn.close()
    
    def approve_manufacturer(self, pending_id: int, admin_notes: str = "") -> bool:
        """
        Approve a pending manufacturer and add to main database
        Returns True if successful
        """
        conn = self.user_db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get pending manufacturer info
            cursor.execute('SELECT * FROM pending_manufacturers WHERE id = ?', (pending_id,))
            pending = cursor.fetchone()
            
            if not pending:
                return False
            
            # Add to main manufacturers database
            from arrow_database import ArrowDatabase
            arrow_db = ArrowDatabase()
            arrow_conn = arrow_db.get_connection()
            arrow_cursor = arrow_conn.cursor()
            
            try:
                arrow_cursor.execute('''
                    INSERT OR IGNORE INTO manufacturers (name, is_active, created_at)
                    VALUES (?, TRUE, CURRENT_TIMESTAMP)
                ''', (pending['name'],))
                arrow_conn.commit()
                
                # Update pending status
                cursor.execute('''
                    UPDATE pending_manufacturers 
                    SET status = 'approved', admin_notes = ?
                    WHERE id = ?
                ''', (admin_notes, pending_id))
                
                conn.commit()
                arrow_conn.close()
                return True
                
            except Exception as e:
                print(f"Error adding manufacturer to main database: {e}")
                arrow_conn.rollback()
                arrow_conn.close()
                return False
                
        except Exception as e:
            print(f"Error approving manufacturer: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def reject_manufacturer(self, pending_id: int, admin_notes: str = "") -> bool:
        """Reject a pending manufacturer"""
        conn = self.user_db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE pending_manufacturers 
                SET status = 'rejected', admin_notes = ?
                WHERE id = ?
            ''', (admin_notes, pending_id))
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error rejecting manufacturer: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_equipment_usage_analytics(self, category_name: str = None, 
                                    days: int = 30) -> Dict:
        """Get equipment usage analytics"""
        conn = self.user_db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get top models by category
            sql = '''
                SELECT manufacturer_name, model_name, category_name, 
                       usage_count, last_used
                FROM equipment_models 
                WHERE julianday('now') - julianday(last_used) <= ?
            '''
            params = [days]
            
            if category_name:
                sql += ' AND category_name = ?'
                params.append(category_name)
            
            sql += ' ORDER BY usage_count DESC LIMIT 20'
            
            cursor.execute(sql, params)
            top_models = [dict(row) for row in cursor.fetchall()]
            
            # Get category breakdown
            cursor.execute('''
                SELECT category_name, COUNT(*) as model_count, SUM(usage_count) as total_usage
                FROM equipment_models
                WHERE julianday('now') - julianday(last_used) <= ?
                GROUP BY category_name
                ORDER BY total_usage DESC
            ''', (days,))
            category_breakdown = [dict(row) for row in cursor.fetchall()]
            
            # Get pending manufacturer count
            cursor.execute('SELECT COUNT(*) as count FROM pending_manufacturers WHERE status = "pending"')
            pending_count = cursor.fetchone()['count']
            
            return {
                'top_models': top_models,
                'category_breakdown': category_breakdown,
                'pending_manufacturers': pending_count,
                'analysis_period_days': days
            }
            
        except Exception as e:
            print(f"Error getting usage analytics: {e}")
            return {}
        finally:
            conn.close()
    
    def _update_usage_stats(self, cursor, manufacturer_name: str, model_name: str, category_name: str):
        """Update monthly usage statistics"""
        try:
            # Get current month period
            now = datetime.now()
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Calculate next month start
            if now.month == 12:
                period_end = period_start.replace(year=now.year + 1, month=1)
            else:
                period_end = period_start.replace(month=now.month + 1)
            
            # Update or insert usage stats
            cursor.execute('''
                INSERT OR REPLACE INTO equipment_usage_stats 
                (manufacturer_name, model_name, category_name, monthly_usage, total_usage, 
                 period_start, period_end, last_updated)
                VALUES (
                    ?, ?, ?, 
                    COALESCE((SELECT monthly_usage FROM equipment_usage_stats 
                             WHERE manufacturer_name = ? AND model_name = ? AND category_name = ? 
                             AND period_start = ?), 0) + 1,
                    COALESCE((SELECT total_usage FROM equipment_usage_stats 
                             WHERE manufacturer_name = ? AND model_name = ? AND category_name = ?
                             AND period_start = ?), 0) + 1,
                    ?, ?, CURRENT_TIMESTAMP
                )
            ''', (manufacturer_name, model_name, category_name,
                  manufacturer_name, model_name, category_name, period_start.date(),
                  manufacturer_name, model_name, category_name, period_start.date(),
                  period_start.date(), period_end.date()))
                  
        except Exception as e:
            print(f"Warning: Could not update usage stats: {e}")

def test_equipment_learning():
    """Test the equipment learning functionality"""
    learning = EquipmentLearningManager()
    
    print("🧠 Testing Equipment Learning System")
    print("=" * 50)
    
    # Test learning new equipment
    test_cases = [
        ("Custom Bow Co", "Super Sight Pro", "Sight", 1),
        ("Axcel", "AccuHunter", "Sight", 1),
        ("Leupold", "VX-3HD", "Scope", 1),
        ("Beiter", "Plunger Elite", "Plunger", 1),
    ]
    
    for manufacturer, model, category, user_id in test_cases:
        print(f"\\n📝 Learning: {manufacturer} {model} ({category})")
        result = learning.learn_equipment_entry(manufacturer, model, category, user_id)
        print(f"   New manufacturer: {result['new_manufacturer']}")
        print(f"   New model: {result['new_model']}")
        print(f"   Manufacturer status: {result['manufacturer_status']}")
        print(f"   Model usage count: {result['model_usage_count']}")
    
    # Test model suggestions
    print(f"\\n💡 Model suggestions for Axcel Sight:")
    suggestions = learning.get_model_suggestions("Axcel", "Sight", limit=5)
    for suggestion in suggestions:
        print(f"   {suggestion['model_name']} (used {suggestion['usage_count']} times)")
    
    # Test pending manufacturers
    print(f"\\n⏳ Pending manufacturers:")
    pending = learning.get_pending_manufacturers()
    for p in pending[:3]:
        print(f"   {p['name']} - {p['usage_count']} uses")
    
    print(f"\\n✅ Equipment learning test completed!")

if __name__ == "__main__":
    test_equipment_learning()