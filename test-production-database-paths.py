#!/usr/bin/env python3
"""
Test script to verify database paths in production configuration
"""

import os
import subprocess
import json
from pathlib import Path

def run_command(cmd, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else None
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None

def check_production_containers():
    """Check what containers are currently running"""
    print("🔍 Checking current production containers...")
    
    # Check running containers
    containers = run_command("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'")
    if containers:
        print("Current containers:")
        print(containers)
    else:
        print("No containers running or Docker not accessible")
    
    # Check for arrowtuner containers specifically
    arrowtuner_containers = run_command("docker ps --filter 'name=arrowtuner' --format '{{.Names}}'")
    if arrowtuner_containers:
        return arrowtuner_containers.split('\n')
    else:
        return []

def check_database_paths_in_container(container_name):
    """Check database paths in a specific container"""
    print(f"\n📊 Checking database paths in {container_name}...")
    
    # Check environment variables
    env_vars = run_command(f"docker exec {container_name} bash -c 'echo ARROW_DATABASE_PATH=$ARROW_DATABASE_PATH; echo USER_DATABASE_PATH=$USER_DATABASE_PATH'")
    if env_vars:
        print("Environment variables:")
        print(env_vars)
    
    # Check actual database files
    db_files = run_command(f"docker exec {container_name} find /app -name '*.db' -type f 2>/dev/null")
    if db_files:
        print("Database files found:")
        for db_file in db_files.split('\n'):
            if db_file:
                size_info = run_command(f"docker exec {container_name} ls -lh {db_file}")
                print(f"  {db_file}: {size_info}")
    
    # Check API health if it's an API container
    if 'api' in container_name:
        health = run_command(f"docker exec {container_name} curl -s http://localhost:5000/api/health")
        if health:
            try:
                health_data = json.loads(health)
                print("API Health:")
                print(f"  Status: {health_data.get('status', 'unknown')}")
                db_stats = health_data.get('database_stats', {})
                print(f"  Arrows: {db_stats.get('total_arrows', 'unknown')}")
                print(f"  Manufacturers: {db_stats.get('total_manufacturers', 'unknown')}")
            except json.JSONDecodeError:
                print(f"API Response (raw): {health[:200]}...")

def check_docker_compose_files():
    """Check what docker-compose files exist"""
    print("\n📋 Checking docker-compose files...")
    
    compose_files = [
        "docker-compose.yml",
        "docker-compose.unified.yml", 
        "docker-compose.enhanced-ssl.yml",
        "docker-compose.ssl.yml",
        "docker-compose.prod.yml"
    ]
    
    for compose_file in compose_files:
        if Path(compose_file).exists():
            print(f"  ✅ {compose_file} exists")
            # Check which one might be currently used
            if compose_file == "docker-compose.yml":
                running_services = run_command(f"docker-compose -f {compose_file} ps --services")
                if running_services:
                    print(f"    Services from {compose_file}: {running_services}")
        else:
            print(f"  ❌ {compose_file} not found")

def main():
    print("🏹 Production Database Path Verification")
    print("=" * 50)
    
    # Check current containers
    containers = check_production_containers()
    
    # Check database paths in each container
    for container in containers:
        if container:
            check_database_paths_in_container(container)
    
    # Check docker-compose files
    check_docker_compose_files()
    
    print("\n" + "=" * 50)
    print("✅ Production database path check complete")

if __name__ == "__main__":
    main()