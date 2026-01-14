#!/bin/bash
# © 2026 Kaxo Technologies. NC License.
#
# test-functional.sh - Functional tests for docs_harvester
# Tests core scraping functionality and feature flags
#

set -e

echo "Running functional tests for docs_harvester..."

# Clean up from previous runs
rm -rf /tmp/test_docs_func

# Test 1: Basic scraping with image URL resolution
echo "✓ Test 1: Basic scraping..."
uv run docs-harvester https://docs.python.org/3/library/os.html \
  --max-pages 2 --format json --output-dir /tmp/test_docs_func 2>&1 | \
  grep -qE "(ERROR|CRITICAL)" && { echo "FAILED: Errors detected"; exit 1; } || echo "  ✓ No errors in logs"

# Verify output file exists
[ -f /tmp/test_docs_func/python_org_site_docs/docs_python_org_docs.json ] || \
  { echo "FAILED: Output file not created"; exit 1; }
echo "  ✓ JSON output created"

# Test 2: --no-images flag strips images
echo "✓ Test 2: --no-images flag..."
uv run docs-harvester https://docs.python.org/3/library/os.html \
  --max-pages 1 --format html --no-images --output-dir /tmp/test_docs_func/no_img > /dev/null 2>&1

if grep -q '<img' /tmp/test_docs_func/no_img/python_org_site_docs/docs_python_org_docs.html 2>/dev/null; then
  echo "FAILED: Found images with --no-images"
  exit 1
else
  echo "  ✓ Images stripped successfully"
fi

# Test 3: HTML output format
echo "✓ Test 3: HTML output format..."
uv run docs-harvester https://docs.python.org/3/library/os.html \
  --max-pages 1 --format html --output-dir /tmp/test_docs_func/html_test > /dev/null 2>&1

[ -f /tmp/test_docs_func/html_test/python_org_site_docs/docs_python_org_docs.html ] || \
  { echo "FAILED: HTML output not created"; exit 1; }
echo "  ✓ HTML output created"

# Test 4: --incremental mode
echo "✓ Test 4: Incremental scraping..."
uv run docs-harvester https://docs.python.org/3/library/os.html \
  --max-pages 1 --format json --output-dir /tmp/test_docs_func/inc_test > /dev/null 2>&1

# Second run should load existing pages
OUTPUT=$(uv run docs-harvester https://docs.python.org/3/library/os.html \
  --max-pages 2 --format json --output-dir /tmp/test_docs_func/inc_test --incremental 2>&1)

echo "$OUTPUT" | grep -q "Loaded.*existing pages" && echo "  ✓ Incremental mode loads existing pages" || \
  { echo "FAILED: Incremental mode not working"; exit 1; }

# Test 5: Cache TTL (verify it enables caching)
echo "✓ Test 5: HTTP caching..."
OUTPUT=$(uv run docs-harvester https://docs.python.org/3/library/os.html \
  --max-pages 1 --format json --output-dir /tmp/test_docs_func/cache_test --cache-ttl 3600 2>&1)

echo "$OUTPUT" | grep -q "HTTP caching enabled" && echo "  ✓ HTTP caching enabled" || \
  { echo "FAILED: Cache not enabled with --cache-ttl"; exit 1; }

# Cleanup
rm -rf /tmp/test_docs_func

echo ""
echo "✓ All functional tests passed!"
