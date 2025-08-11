#!/usr/bin/env python3

import requests
import json

def test_api_scraping():
    """Test the updated API scraping endpoint"""
    
    # Reset the database first to ensure we see the difference
    print("=== Verifying current X10 Parallel Pro spine specifications ===")
    
    import sqlite3
    conn = sqlite3.connect('/home/paal/arrowtuner2/databases/arrow_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.id, a.model_name, COUNT(ss.id) as spine_count
        FROM arrows a
        LEFT JOIN spine_specifications ss ON a.id = ss.arrow_id
        WHERE a.manufacturer LIKE '%Easton%' AND a.model_name LIKE '%X10 Parallel Pro%'
        GROUP BY a.id, a.model_name
    ''')
    
    before_result = cursor.fetchone()
    if before_result:
        print(f"Before API call: {before_result[1]} has {before_result[2]} spine specifications")
    else:
        print("X10 Parallel Pro not found in database")
        return
    
    conn.close()
    
    # Test the API endpoint directly by making a request to the Flask server
    print("\n=== Testing API scraping endpoint ===")
    
    # Check if API is running
    try:
        health_response = requests.get("http://localhost:5000/api/health", timeout=5)
        print(f"API health check: {health_response.status_code}")
    except requests.RequestException as e:
        print(f"API server not running: {e}")
        return
    
    # Try to call the scraping endpoint
    url = "http://localhost:5000/api/admin/scrape-url"
    
    payload = {
        "url": "https://eastonarchery.com/arrows_/x10-parallel-pro/",
        "manufacturer": "Easton"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Calling API: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 401:
            print("\nNOTE: API requires authentication. Let's test the scraping logic directly.")
            return
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nSuccess! API response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"\nError response:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
                
    except Exception as e:
        print(f"Error calling API: {e}")
        return
    
    # Check the database again to see if anything changed
    print("\n=== Verifying database changes ===")
    
    conn = sqlite3.connect('/home/paal/arrowtuner2/databases/arrow_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.id, a.model_name, COUNT(ss.id) as spine_count
        FROM arrows a
        LEFT JOIN spine_specifications ss ON a.id = ss.arrow_id
        WHERE a.manufacturer LIKE '%Easton%' AND a.model_name LIKE '%X10 Parallel Pro%'
        GROUP BY a.id, a.model_name
    ''')
    
    after_result = cursor.fetchone()
    if after_result:
        print(f"After API call: {after_result[1]} has {after_result[2]} spine specifications")
        
        if before_result and after_result[2] > before_result[2]:
            added = after_result[2] - before_result[2]
            print(f"✅ SUCCESS: Added {added} new spine specifications!")
            
            # Show the new specifications
            cursor.execute('''
                SELECT spine, gpi_weight, outer_diameter
                FROM spine_specifications
                WHERE arrow_id = ?
                ORDER BY spine
            ''', (after_result[0],))
            
            specs = cursor.fetchall()
            print(f"\nAll spine specifications for {after_result[1]}:")
            for spec in specs:
                print(f"  Spine {spec[0]}: GPI={spec[1]}, Diameter={spec[2]}")
        else:
            print("No new specifications were added")
    
    conn.close()

if __name__ == "__main__":
    test_api_scraping()