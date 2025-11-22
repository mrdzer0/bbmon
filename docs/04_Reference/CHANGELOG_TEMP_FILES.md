# Temporary File Management - Changelog

## Issue Fixed

**Problem**: Tool outputs (subfinder.txt, amass.txt, etc.) were saved directly to the output directory without domain-specific names. When scanning different domains, results would merge and create confusion.

**Example of the problem**:
```bash
# First scan
./utils/subdomain_scan.sh -d example.com -o output/
# Creates: output/subfinder.txt, output/amass.txt

# Second scan
./utils/subdomain_scan.sh -d another.com -o output/
# Overwrites: output/subfinder.txt, output/amass.txt
# OR appends to existing files, causing mixed results
```

## Solution Implemented

**Updated**: `modules/subdomain_finder.py`

### Changes Made

1. **Temporary Directory per Scan**
   - Each scan now creates a unique temporary directory: `/tmp/subdomain_{domain}_{random}/`
   - All tool outputs go to this temp directory
   - Temp directory is automatically cleaned up after processing

2. **Tool Output Files** (now temporary):
   - `subfinder.txt` → `/tmp/subdomain_example.com_abc123/subfinder.txt`
   - `amass.txt` → `/tmp/subdomain_example.com_abc123/amass.txt`
   - `dnsx_output.json` → `/tmp/subdomain_example.com_abc123/dnsx_output.json`
   - `chaos/` → `/tmp/subdomain_example.com_abc123/chaos/`

3. **Final Result Files** (kept permanently):
   - `{domain}_all_subdomains.txt` - All unique subdomains
   - `{domain}_by_source.json` - Results grouped by tool
   - `{domain}_stats.txt` - Statistics and summary
   - `{domain}_takeover_report.txt` - Takeover findings (if any)

### Code Changes

**Before**:
```python
def run_subfinder(self):
    output_file = self.output_dir / "subfinder.txt"  # Direct output
    cmd = f"subfinder -d {self.domain} -o {output_file}"
    # File stays in output directory
```

**After**:
```python
def __init__(self, domain, output_dir):
    # Create temporary directory
    self.temp_dir = tempfile.mkdtemp(prefix=f"subdomain_{domain}_")

def run_subfinder(self):
    temp_file = os.path.join(self.temp_dir, "subfinder.txt")  # Temp file
    cmd = f"subfinder -d {self.domain} -o {temp_file}"
    # File is temporary and will be cleaned up

def cleanup_temp_files(self):
    shutil.rmtree(self.temp_dir)  # Clean up after processing

def run_all(self):
    # ... run all tools ...
    self.save_results()  # Save final results
    self.cleanup_temp_files()  # Clean up temp files
```

## Benefits

### 1. No File Collisions
```bash
# Scan multiple domains safely
./utils/subdomain_scan.sh -d example.com -o output/
./utils/subdomain_scan.sh -d another.com -o output/
./utils/subdomain_scan.sh -d third.com -o output/

# Each creates domain-specific files:
# output/example.com_all_subdomains.txt
# output/another.com_all_subdomains.txt
# output/third.com_all_subdomains.txt
```

### 2. Cleaner Output Directory
```bash
# Only final processed results are saved
output/
├── example.com_all_subdomains.txt    # Final results
├── example.com_by_source.json        # Final results
├── example.com_stats.txt             # Final results
├── another.com_all_subdomains.txt    # Final results
└── another.com_by_source.json        # Final results

# No more clutter:
# ❌ subfinder.txt (removed - was temporary)
# ❌ amass.txt (removed - was temporary)
# ❌ chaos/ (removed - was temporary)
# ❌ dnsx_output.json (removed - was temporary)
```

### 3. Automatic Cleanup
- Temporary files are automatically deleted after each scan
- No manual cleanup required
- Disk space is freed immediately
- `/tmp` directory handles cleanup on reboot if needed

### 4. Parallel Scans Safe
```bash
# Run multiple scans in parallel - no conflicts
./utils/subdomain_scan.sh -d domain1.com -o output/ &
./utils/subdomain_scan.sh -d domain2.com -o output/ &
./utils/subdomain_scan.sh -d domain3.com -o output/ &
wait

# Each scan uses its own temp directory:
# /tmp/subdomain_domain1.com_abc123/
# /tmp/subdomain_domain2.com_xyz456/
# /tmp/subdomain_domain3.com_def789/
```

## File Lifecycle

### Temporary Files (Auto-deleted)
These are created during scanning and deleted after:
- Individual tool outputs (subfinder.txt, amass.txt, etc.)
- DNS validation JSON output
- Chaos zip files and extracted data
- Any intermediate processing files

**Location**: `/tmp/subdomain_{domain}_{random}/`
**Lifetime**: Duration of scan only
**Cleanup**: Automatic via `cleanup_temp_files()`

### Permanent Files (Saved)
These are the final processed results:
- `{domain}_all_subdomains.txt` - Deduplicated list of all subdomains
- `{domain}_by_source.json` - Which tool found which subdomain
- `{domain}_stats.txt` - Count per tool and total
- `{domain}_takeover_report.txt` - Verified takeover vulnerabilities

**Location**: User-specified output directory (e.g., `./output/`)
**Lifetime**: Permanent until manually deleted
**Cleanup**: Manual by user

## Examples

### Example 1: Single Domain Scan

```bash
./utils/subdomain_scan.sh -d hackerone.com -o results/

# During scan:
# /tmp/subdomain_hackerone.com_Xa5fQ/
# ├── subfinder.txt
# ├── assetfinder.txt (not saved, piped to memory)
# ├── chaos/
# │   └── hackerone.com.zip
# └── dnsx_output.json

# After scan:
# /tmp/subdomain_hackerone.com_Xa5fQ/  <- DELETED

# results/
# ├── hackerone.com_all_subdomains.txt     <- KEPT
# ├── hackerone.com_by_source.json         <- KEPT
# ├── hackerone.com_stats.txt              <- KEPT
# └── hackerone.com_takeover_report.txt    <- KEPT (if found)
```

### Example 2: Multiple Domain Scans

```bash
# Scan multiple domains to same output directory
for domain in hackerone.com bugcrowd.com intigriti.com; do
    ./utils/subdomain_scan.sh -d $domain -o combined_results/
done

# Each scan:
# 1. Creates unique temp dir: /tmp/subdomain_{domain}_RANDOM/
# 2. Runs all tools, saves to temp
# 3. Processes and saves final results to combined_results/
# 4. Cleans up temp directory

# Final structure:
combined_results/
├── hackerone.com_all_subdomains.txt
├── hackerone.com_by_source.json
├── hackerone.com_stats.txt
├── bugcrowd.com_all_subdomains.txt
├── bugcrowd.com_by_source.json
├── bugcrowd.com_stats.txt
├── intigriti.com_all_subdomains.txt
├── intigriti.com_by_source.json
└── intigriti.com_stats.txt
```

### Example 3: Monitoring Framework Integration

```bash
# When used by monitor.py
./monitor.py --init

# For each target domain:
# 1. SubdomainFinder creates temp dir
# 2. Runs all discovery tools
# 3. Saves to data/subdomain_scans/{domain}/
# 4. Cleans up temp files
# 5. Returns results to monitor.py

# No temp file accumulation!
```

## Troubleshooting

### Temp Files Not Cleaned Up

If temporary files aren't being cleaned up (script crashed before cleanup):

```bash
# Manual cleanup
rm -rf /tmp/subdomain_*

# Or let system cleanup on reboot
# /tmp is typically cleared on system restart
```

### Disk Space Issues

Temporary directory is in `/tmp`:
```bash
# Check /tmp space
df -h /tmp

# If needed, change temp location
export TMPDIR=/path/to/large/disk
./utils/subdomain_scan.sh -d example.com
```

### Debug Temporary Files

To see temp files during debugging:

```python
# In subdomain_finder.py, comment out cleanup
def run_all(self):
    # ... scanning ...
    self.save_results()

    # DEBUG: Comment out to keep temp files
    # self.cleanup_temp_files()

    print(f"DEBUG: Temp files at: {self.temp_dir}")
```

## Migration Guide

If you have old scan results with tool-specific files:

```bash
# Old structure (before fix)
output/
├── subfinder.txt          # Mixed results from multiple scans
├── amass.txt              # Mixed results
├── chaos.txt              # Mixed results
├── example.com_all_subdomains.txt
└── another.com_all_subdomains.txt

# Clean up old temporary files
rm output/subfinder.txt
rm output/amass.txt
rm output/chaos.txt
rm -rf output/chaos/
rm output/dnsx_output.json

# Keep domain-specific results
# These are the final processed outputs
```

## Version History

**v1.1.0** (Current)
- ✅ Temporary files for tool outputs
- ✅ Automatic cleanup after processing
- ✅ Domain-specific result filenames
- ✅ Parallel scan support

**v1.0.0** (Previous)
- ❌ Tool outputs saved directly
- ❌ No automatic cleanup
- ❌ File collision issues

## Related Changes

- Updated: `modules/subdomain_finder.py`
- Methods changed:
  - `__init__()` - Added temp directory creation
  - `run_subfinder()` - Uses temp file
  - `run_amass()` - Uses temp file
  - `run_chaos()` - Uses temp directory
  - `check_dns_with_dnsx()` - Uses temp file
  - `run_all()` - Calls cleanup
  - Added: `cleanup_temp_files()` - New method

## See Also

- [PATH_TROUBLESHOOTING.md](PATH_TROUBLESHOOTING.md) - Path configuration
- [USAGE.md](USAGE.md) - Usage guide
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration reference
