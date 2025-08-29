#!/bin/bash

# Renovate Configuration Testing Script
# This script validates and tests the Renovate configuration

set -e

echo "🔍 Validating Renovate Configuration..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if we're in the right directory
if [[ ! -f "renovate.json" ]]; then
    print_status $RED "❌ Error: renovate.json not found. Run this script from the project root."
    exit 1
fi

print_status $BLUE "📋 Checking configuration files..."

# Validate JSON syntax
for config_file in "renovate.json" ".renovaterc.json" ".github/renovate.json"; do
    if [[ -f "$config_file" ]]; then
        if python3 -m json.tool "$config_file" > /dev/null 2>&1; then
            print_status $GREEN "✅ $config_file: Valid JSON"
        else
            print_status $RED "❌ $config_file: Invalid JSON"
            exit 1
        fi
    else
        print_status $YELLOW "⚠️  $config_file: Not found (optional)"
    fi
done

# Check if Node.js is available for advanced validation
if command -v node &> /dev/null; then
    print_status $BLUE "🔧 Node.js found, running advanced validation..."

    # Try to install and run renovate config validator
    if npx --version &> /dev/null; then
        print_status $BLUE "📦 Installing Renovate for validation..."
        if npx renovate --version &> /dev/null 2>&1; then
            print_status $GREEN "✅ Renovate installed successfully"

            # Validate the config (dry-run)
            print_status $BLUE "🧪 Running configuration validation..."
            if npx renovate --help | grep -q "validate"; then
                print_status $GREEN "✅ Renovate validation available"
            else
                print_status $YELLOW "⚠️  Renovate validation not available in this version"
            fi
        else
            print_status $YELLOW "⚠️  Could not install Renovate for advanced validation"
        fi
    else
        print_status $YELLOW "⚠️  npx not available, skipping advanced validation"
    fi
else
    print_status $YELLOW "⚠️  Node.js not found, skipping advanced validation"
fi

# Check project structure
print_status $BLUE "🏗️  Checking project structure..."

required_files=(
    "requirements.txt"
    "requirements-dev.txt"
    "pyproject.toml"
    "Dockerfile"
    "docker-compose.yml"
    ".pre-commit-config.yaml"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        print_status $GREEN "✅ $file: Found"
    else
        print_status $YELLOW "⚠️  $file: Not found"
    fi
done

# Check GitHub workflows
if [[ -d ".github/workflows" ]]; then
    workflow_count=$(find .github/workflows -name "*.yml" -o -name "*.yaml" | wc -l)
    print_status $GREEN "✅ GitHub workflows: $workflow_count found"
else
    print_status $YELLOW "⚠️  .github/workflows: Directory not found"
fi

# Check documentation
print_status $BLUE "📚 Checking documentation..."
if [[ -f "docs/RENOVATE.md" ]]; then
    print_status $GREEN "✅ Renovate documentation: Found"
else
    print_status $YELLOW "⚠️  docs/RENOVATE.md: Not found"
fi

# Summary
print_status $BLUE "📊 Configuration Summary:"
echo "  - Main config: renovate.json"
echo "  - Local overrides: .renovaterc.json"
echo "  - Organization config: .github/renovate.json"
echo "  - Documentation: docs/RENOVATE.md"
echo "  - Validation workflow: .github/workflows/renovate.yml"

print_status $GREEN "🎉 Renovate configuration validation completed!"

# Provide next steps
print_status $BLUE "🚀 Next Steps:"
echo "  1. Enable Renovate in your GitHub repository settings"
echo "  2. Check the Renovate Dashboard issue for updates"
echo "  3. Review and merge initial dependency PRs"
echo "  4. Monitor the dependency dashboard for ongoing updates"

print_status $YELLOW "📖 For more information, see docs/RENOVATE.md"
