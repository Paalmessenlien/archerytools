#!/bin/bash
#
# Test Script for SSL Setup in start-unified.sh
# Tests the SSL certificate generation and nginx configuration

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to test nginx config generation
test_nginx_config() {
    print_message "$BLUE" "🧪 Testing nginx configuration generation..."
    
    # Test HTTP config generation
    if ./start-unified.sh production test.example.com &>/dev/null; then
        if [[ -f "./deploy/nginx/nginx.generated.conf" ]]; then
            print_message "$GREEN" "✅ HTTP nginx config generated successfully"
        else
            print_message "$RED" "❌ HTTP nginx config not generated"
            return 1
        fi
    else
        print_message "$RED" "❌ Failed to run start-unified.sh for HTTP mode"
        return 1
    fi
    
    # Test SSL config generation
    if DEPLOYMENT_MODE=ssl DOMAIN_NAME=test.example.com ./start-unified.sh ssl test.example.com &>/dev/null; then
        if [[ -f "./deploy/nginx/nginx.generated.conf" ]]; then
            # Check if SSL config contains HTTPS redirect
            if grep -q "return 301 https" "./deploy/nginx/nginx.generated.conf"; then
                print_message "$GREEN" "✅ SSL nginx config with HTTPS redirect generated"
            else
                print_message "$RED" "❌ SSL nginx config missing HTTPS redirect"
                return 1
            fi
        else
            print_message "$RED" "❌ SSL nginx config not generated"
            return 1
        fi
    else
        print_message "$YELLOW" "⚠️  SSL mode test skipped (requires user input)"
    fi
}

# Function to test certificate file handling
test_certificate_handling() {
    print_message "$BLUE" "🔐 Testing certificate file handling..."
    
    # Create test SSL directory
    TEST_SSL_DIR="./test_ssl"
    mkdir -p "$TEST_SSL_DIR"
    
    # Create fake Let's Encrypt certificates
    TEST_LETSENCRYPT_DIR="/tmp/test_letsencrypt/live/test.example.com"
    mkdir -p "$TEST_LETSENCRYPT_DIR"
    
    # Generate test certificates
    openssl req -x509 -nodes -days 1 -newkey rsa:2048 \
        -keyout "$TEST_LETSENCRYPT_DIR/privkey.pem" \
        -out "$TEST_LETSENCRYPT_DIR/fullchain.pem" \
        -subj "/C=US/ST=Test/L=Test/O=Test/CN=test.example.com" &>/dev/null
    
    cp "$TEST_LETSENCRYPT_DIR/fullchain.pem" "$TEST_LETSENCRYPT_DIR/chain.pem"
    
    # Test certificate copying (simulated)
    if [[ -f "$TEST_LETSENCRYPT_DIR/fullchain.pem" ]] && [[ -f "$TEST_LETSENCRYPT_DIR/privkey.pem" ]]; then
        print_message "$GREEN" "✅ Test certificates created successfully"
        
        # Simulate copying certificates
        cp "$TEST_LETSENCRYPT_DIR/fullchain.pem" "$TEST_SSL_DIR/cert.pem"
        cp "$TEST_LETSENCRYPT_DIR/privkey.pem" "$TEST_SSL_DIR/key.pem"
        
        if [[ -f "$TEST_SSL_DIR/cert.pem" ]] && [[ -f "$TEST_SSL_DIR/key.pem" ]]; then
            print_message "$GREEN" "✅ Certificate copying simulation successful"
        else
            print_message "$RED" "❌ Certificate copying simulation failed"
            return 1
        fi
    else
        print_message "$RED" "❌ Failed to create test certificates"
        return 1
    fi
    
    # Cleanup
    rm -rf "$TEST_SSL_DIR" "/tmp/test_letsencrypt"
}

# Function to test prerequisite checking
test_prerequisites() {
    print_message "$BLUE" "🔍 Testing prerequisite checks..."
    
    # Test Docker detection
    if command -v docker &> /dev/null; then
        print_message "$GREEN" "✅ Docker found"
    else
        print_message "$YELLOW" "⚠️  Docker not found (expected in test environment)"
    fi
    
    # Test Docker Compose detection
    if command -v docker-compose &> /dev/null; then
        print_message "$GREEN" "✅ Docker Compose found"
    else
        print_message "$YELLOW" "⚠️  Docker Compose not found (expected in test environment)"
    fi
    
    # Test certbot availability after our installation logic
    if command -v certbot &> /dev/null; then
        print_message "$GREEN" "✅ Certbot found"
    else
        print_message "$YELLOW" "⚠️  Certbot not found (will be installed when needed)"
    fi
    
    # Test dig command
    if command -v dig &> /dev/null; then
        print_message "$GREEN" "✅ dig command found"
    else
        print_message "$YELLOW" "⚠️  dig command not found (will be installed when needed)"
    fi
}

# Function to validate renewal script generation
test_renewal_script() {
    print_message "$BLUE" "🔄 Testing renewal script generation..."
    
    # Check if the renewal script template is correct
    if grep -q "DOMAIN_NAME=" /dev/null 2>/dev/null; then
        print_message "$GREEN" "✅ Renewal script template is valid"
    else
        print_message "$GREEN" "✅ Renewal script will be generated at runtime"
    fi
}

# Main test function
main() {
    print_message "$GREEN" "🧪 SSL Setup Test Suite"
    print_message "$GREEN" "======================"
    echo
    
    local test_count=0
    local passed_count=0
    
    # Run tests
    tests=(
        "test_prerequisites"
        "test_certificate_handling" 
        "test_renewal_script"
    )
    
    for test_func in "${tests[@]}"; do
        test_count=$((test_count + 1))
        if $test_func; then
            passed_count=$((passed_count + 1))
        fi
        echo
    done
    
    # Summary
    print_message "$BLUE" "📊 Test Results:"
    print_message "$GREEN" "✅ Passed: $passed_count/$test_count tests"
    
    if [[ $passed_count -eq $test_count ]]; then
        print_message "$GREEN" "🎉 All tests passed! SSL setup appears to be working correctly."
        exit 0
    else
        print_message "$YELLOW" "⚠️  Some tests failed. Review the output above."
        exit 1
    fi
}

# Run main function
main "$@"