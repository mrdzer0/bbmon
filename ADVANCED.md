# Advanced Bug Bounty Monitoring Guide

## Advanced Techniques for Finding Bugs

### 1. Historical Analysis

Track patterns over time to predict when new features drop:

```bash
# Analyze change frequency
for domain in $(cat targets.txt); do
  echo "=== $domain ==="
  find data/diffs -name "${domain}_*.json" | wc -l
done
```

**Strategy**: Targets that change frequently = active development = more bugs

### 2. Technology Stack Monitoring

Detect version changes and search for CVEs:

```python
# Add to monitor.py after technology detection
def check_cves_for_tech(tech_stack):
    """Check for known CVEs in detected technologies"""
    for tech, version in tech_stack.items():
        # Search CVE databases
        cves = search_cves(tech, version)
        if cves:
            notify_high_priority(f"CVE found in {tech} {version}: {cves}")
```

### 3. Diff Everything

Monitor more than just endpoints:

```yaml
# Enhanced monitoring
checks:
  advanced:
    robots_txt: true
    sitemap_xml: true
    security_txt: true
    cors_headers: true
    csp_headers: true
    cookies_flags: true
    html_comments: true
    meta_tags: true
```

### 4. Smart Wordlists

Use context-aware wordlists based on detected technology:

```python
def get_wordlist_for_tech(tech_stack):
    """Return appropriate wordlist based on tech stack"""
    if 'WordPress' in tech_stack:
        return '/usr/share/wordlists/dirb/vulns/wordpress.txt'
    elif 'Laravel' in tech_stack:
        return '/usr/share/wordlists/dirb/vulns/laravel.txt'
    # etc...
```

### 5. Continuous Screenshots

Visual diff to catch UI changes:

```bash
# Install
pip3 install selenium pillow

# Add screenshot comparison
def compare_screenshots(url, old_screenshot, new_screenshot):
    """Compare two screenshots pixel by pixel"""
    from PIL import Image, ImageChops

    img1 = Image.open(old_screenshot)
    img2 = Image.open(new_screenshot)

    diff = ImageChops.difference(img1, img2)

    if diff.getbbox():
        return True  # Screenshots differ
    return False
```

## Real-World Bug Finding Examples

### Example 1: New Subdomain → Subdomain Takeover

**Detection**:
```json
{
  "new_subdomains": ["temp-api.example.com"]
}
```

**Investigation**:
```bash
# Check DNS
dig temp-api.example.com

# Check CNAME
host temp-api.example.com

# Output: temp-api.example.com is an alias for example.herokuapp.com
# Heroku app not found = Takeover possible!
```

**Result**: High severity subdomain takeover

### Example 2: New Upload Endpoint

**Detection**:
```json
{
  "new_endpoints": ["https://example.com/api/upload-profile-pic"]
}
```

**Investigation**:
```bash
# Test file upload
curl -X POST https://example.com/api/upload-profile-pic \
  -F "file=@test.php" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check if PHP executed
curl https://example.com/uploads/test.php
```

**Result**: Unrestricted file upload → RCE

### Example 3: New JS Endpoint

**Detection**:
```json
{
  "new_js_endpoints": ["/api/admin/delete-user/{id}"]
}
```

**Investigation**:
```bash
# Test IDOR
curl -X DELETE https://example.com/api/admin/delete-user/1234 \
  -H "Authorization: Bearer YOUR_USER_TOKEN"

# Try deleting other user's account
curl -X DELETE https://example.com/api/admin/delete-user/5678 \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```

**Result**: IDOR vulnerability, can delete any user

### Example 4: Technology Version Change

**Detection**:
```json
{
  "changed_endpoints": [{
    "url": "https://example.com",
    "old": {"technologies": ["Apache 2.4.41"]},
    "new": {"technologies": ["Apache 2.4.49"]}
  }]
}
```

**Investigation**:
```bash
# Search for CVEs
searchsploit apache 2.4.49

# Output: Apache 2.4.49 - Path Traversal (CVE-2021-41773)

# Test the CVE
curl https://example.com/cgi-bin/.%2e/.%2e/.%2e/.%2e/etc/passwd
```

**Result**: Path traversal via known CVE

### Example 5: Removed Security Header

**Detection**:
```json
{
  "changed_endpoints": [{
    "url": "https://example.com/dashboard",
    "old": {"headers": {"X-Frame-Options": "DENY"}},
    "new": {"headers": {}}
  }]
}
```

**Investigation**:
```html
<!-- Test clickjacking -->
<iframe src="https://example.com/dashboard"></iframe>
```

**Result**: Clickjacking vulnerability

## Integration with Other Tools

### 1. Nuclei Integration

Auto-scan new endpoints:

```python
def scan_with_nuclei(url):
    """Run Nuclei on new endpoints"""
    cmd = f"nuclei -u {url} -t exposures,cves -severity critical,high,medium -json"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    findings = []
    for line in result.stdout.split('\n'):
        if line:
            findings.append(json.loads(line))

    return findings
```

### 2. Burp Suite Integration

Export to Burp for manual testing:

```python
def export_to_burp(endpoints):
    """Export new endpoints to Burp target"""
    burp_config = {
        "target": {
            "scope": {
                "include": [{"url": ep} for ep in endpoints]
            }
        }
    }

    with open('burp_targets.json', 'w') as f:
        json.dump(burp_config, f)
```

### 3. Notion Integration

Track findings in Notion:

```python
import requests

def add_to_notion(change_data):
    """Add changes to Notion database"""
    notion_token = "YOUR_NOTION_TOKEN"
    database_id = "YOUR_DATABASE_ID"

    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Domain": {"title": [{"text": {"content": change_data['domain']}}]},
            "Change Type": {"select": {"name": "New Endpoint"}},
            "URL": {"url": change_data['endpoint']},
            "Status": {"select": {"name": "To Test"}}
        }
    }

    requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
```

## Performance Optimization

### 1. Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_targets_parallel(targets):
    """Process multiple targets in parallel"""
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_target = {
            executor.submit(collect_baseline, target): target
            for target in targets
        }

        for future in as_completed(future_to_target):
            target = future_to_target[future]
            try:
                result = future.result()
                print(f"[+] Completed: {target}")
            except Exception as e:
                print(f"[!] Error processing {target}: {e}")
```

### 2. Caching

```python
import hashlib
import pickle
from pathlib import Path

def cache_result(func):
    """Cache function results"""
    cache_dir = Path('.cache')
    cache_dir.mkdir(exist_ok=True)

    def wrapper(*args, **kwargs):
        # Generate cache key
        key = hashlib.md5(str(args).encode()).hexdigest()
        cache_file = cache_dir / f"{func.__name__}_{key}.pkl"

        # Check cache
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return pickle.load(f)

        # Execute and cache
        result = func(*args, **kwargs)
        with open(cache_file, 'wb') as f:
            pickle.dump(result, f)

        return result

    return wrapper

@cache_result
def discover_subdomains(domain):
    # Expensive operation
    pass
```

### 3. Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_second=10):
    """Rate limit decorator"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed

            if left_to_wait > 0:
                time.sleep(left_to_wait)

            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret

        return wrapper
    return decorator

@rate_limit(calls_per_second=5)
def make_request(url):
    return requests.get(url)
```

## Machine Learning for Prioritization

Predict which changes are most likely to have bugs:

```python
from sklearn.ensemble import RandomForestClassifier
import numpy as np

class BugPredictor:
    def __init__(self):
        self.model = RandomForestClassifier()
        self.trained = False

    def extract_features(self, change):
        """Extract features from change"""
        features = [
            1 if 'admin' in change['url'] else 0,
            1 if 'upload' in change['url'] else 0,
            1 if 'api' in change['url'] else 0,
            len(change.get('new_parameters', [])),
            1 if 'staging' in change['url'] else 0,
            change.get('status_code', 0),
        ]
        return features

    def train(self, historical_changes, labels):
        """Train on historical data"""
        X = [self.extract_features(c) for c in historical_changes]
        self.model.fit(X, labels)
        self.trained = True

    def predict_bug_likelihood(self, change):
        """Predict if change likely has bugs"""
        if not self.trained:
            return 0.5

        features = self.extract_features(change)
        probability = self.model.predict_proba([features])[0][1]
        return probability

# Usage
predictor = BugPredictor()

# Train with historical data (1 = found bug, 0 = no bug)
historical_changes = load_historical_changes()
labels = [1, 0, 1, 1, 0, ...]  # Your findings
predictor.train(historical_changes, labels)

# Predict on new changes
for change in new_changes:
    score = predictor.predict_bug_likelihood(change)
    if score > 0.7:
        notify_high_priority(change)
```

## Multi-Target Correlation

Find patterns across multiple targets:

```python
def correlate_changes(all_targets_changes):
    """Find common patterns in changes"""

    # Example: Same third-party library updated across targets
    tech_changes = defaultdict(list)

    for target, changes in all_targets_changes.items():
        for change in changes.get('technology_changes', []):
            tech = change['technology']
            tech_changes[tech].append(target)

    # Alert if same tech changed in multiple targets
    for tech, targets in tech_changes.items():
        if len(targets) >= 3:
            print(f"[!] {tech} updated across {len(targets)} targets - possible widespread vulnerability")
```

## Custom Checks

Add your own monitoring checks:

```python
def check_cors_misconfiguration(url):
    """Check for CORS issues"""
    headers = {'Origin': 'https://evil.com'}
    response = requests.get(url, headers=headers)

    acao = response.headers.get('Access-Control-Allow-Origin')
    if acao == 'https://evil.com' or acao == '*':
        return {
            'vulnerability': 'CORS Misconfiguration',
            'severity': 'High',
            'url': url
        }
    return None

def check_open_redirect(url):
    """Check for open redirect"""
    payloads = ['//evil.com', 'https://evil.com']

    for payload in payloads:
        test_url = f"{url}?redirect={payload}"
        response = requests.get(test_url, allow_redirects=False)

        if response.status_code in [301, 302]:
            location = response.headers.get('Location', '')
            if 'evil.com' in location:
                return {
                    'vulnerability': 'Open Redirect',
                    'severity': 'Medium',
                    'url': test_url
                }
    return None

# Add to monitoring
custom_checks = [
    check_cors_misconfiguration,
    check_open_redirect,
    # Add more...
]

for endpoint in new_endpoints:
    for check in custom_checks:
        result = check(endpoint)
        if result:
            notify_finding(result)
```

## Best Practices

### 1. Incremental Monitoring

Don't scan everything every time:

```yaml
# config.yaml
incremental:
  enabled: true
  full_scan_frequency: 7  # Full scan every 7 days
  quick_scan_checks:
    - subdomain_discovery
    - http_responses
  # Skip slow checks on quick scans
```

### 2. Smart Notifications

Only notify for actionable changes:

```python
def is_actionable(change):
    """Determine if change is worth notifying"""

    # Always actionable
    if any(keyword in change['url'] for keyword in ['admin', 'upload', 'delete', 'internal']):
        return True

    # Check if new functionality
    if change['type'] == 'new_endpoint':
        return True

    # Ignore minor changes
    if change['type'] == 'content_change' and change['percent'] < 10:
        return False

    return True
```

### 3. Organized Workflow

```
1. Monitor runs (automated)
2. Changes detected
3. High-priority → Instant notification
4. Medium-priority → Daily digest
5. Low-priority → Weekly report
6. Review and test
7. Submit bug reports
8. Update historical data for ML
```

## Conclusion

The key to successful monitoring:
1. **Automate everything** - Let scripts do the boring work
2. **Focus on changes** - New features = new bugs
3. **Act fast** - Test before patches
4. **Track patterns** - Learn what works
5. **Integrate tools** - Build a complete workflow

Happy hunting! 🎯
