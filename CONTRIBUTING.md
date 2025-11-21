# Contributing to Bug Bounty Monitoring Framework

Thank you for your interest in contributing! This document provides guidelines for contributions.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow security best practices

## How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template**
3. **Include**:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment (OS, Python version, tool versions)
   - Relevant logs/screenshots

### Suggesting Features

1. **Open a feature request issue**
2. **Describe**:
   - The problem it solves
   - Proposed solution
   - Alternative solutions considered
   - Example use cases

### Code Contributions

#### Setup Development Environment

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/bb-monitor.git
cd bb-monitor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install black flake8 pytest
```

#### Coding Standards

1. **Python Style**:
   - Follow PEP 8
   - Use Black for formatting: `black *.py modules/*.py`
   - Use type hints where appropriate
   - Write docstrings for functions/classes

2. **Code Organization**:
   ```python
   # Good
   def discover_subdomains(domain: str) -> Set[str]:
       """
       Discover subdomains for a given domain.

       Args:
           domain: Target domain

       Returns:
           Set of discovered subdomains
       """
       pass
   ```

3. **Error Handling**:
   ```python
   # Good
   try:
       result = risky_operation()
   except SpecificException as e:
       logger.error(f"Operation failed: {e}")
       return default_value
   ```

4. **Testing**:
   - Write tests for new features
   - Ensure existing tests pass
   - Test edge cases

#### Commit Messages

Follow conventional commits:

```
feat: add screenshot comparison module
fix: resolve DNS timeout issue
docs: update configuration guide
style: format code with black
refactor: improve subdomain deduplication
test: add tests for http_monitor
chore: update dependencies
```

#### Pull Request Process

1. **Create a branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make changes**:
   - Write code
   - Add tests
   - Update documentation
   - Run tests: `pytest`
   - Format code: `black *.py modules/*.py`

3. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

4. **Push branch**:
   ```bash
   git push origin feature/amazing-feature
   ```

5. **Open Pull Request**:
   - Use the PR template
   - Link related issues
   - Describe changes clearly
   - Add screenshots/examples if applicable

6. **Address review comments**:
   - Make requested changes
   - Update PR

### Documentation Contributions

Documentation improvements are always welcome!

- Fix typos
- Improve clarity
- Add examples
- Update outdated information

## Project Structure

```
bb-monitor/
├── monitor.py          # Main script
├── config.yaml         # Configuration
├── modules/            # Core modules
│   ├── subdomain_finder.py
│   ├── http_monitor.py
│   ├── dashboard.py
│   └── notifier.py
├── utils/              # Utility scripts
├── docs/               # Documentation
└── tests/              # Test files (to be added)
```

## Adding New Modules

1. **Create module file** in `modules/`
2. **Follow structure**:
   ```python
   """Module description"""

   class NewModule:
       def __init__(self, config: Dict):
           self.config = config

       def main_function(self) -> Any:
           """Main functionality"""
           pass
   ```

3. **Update `modules/__init__.py`**:
   ```python
   from .new_module import NewModule
   __all__ = [..., 'NewModule']
   ```

4. **Add tests** in `tests/test_new_module.py`
5. **Update documentation**
6. **Add to README.md** features section

## Adding New Tools Integration

1. **Check if tool is available**:
   ```python
   if not shutil.which('tool_name'):
       print("Tool not found")
       return
   ```

2. **Add to config.yaml**:
   ```yaml
   tools:
     tool_name:
       enabled: true
       timeout: 300
   ```

3. **Implement wrapper function**:
   ```python
   def run_tool(self, domain: str) -> Set[str]:
       """Run tool and return results"""
       cmd = f"tool_name -d {domain}"
       output = self.run_command(cmd)
       return self.parse_output(output)
   ```

4. **Update documentation**

## Adding New Detection Signatures

For subdomain takeover or vulnerability detection:

1. **Add signature** in appropriate module:
   ```python
   self.signatures = {
       'new_service': {
           'cname': ['service.com'],
           'response': ['Error message']
       }
   }
   ```

2. **Test thoroughly**:
   - Verify no false positives
   - Check detection accuracy

3. **Document** in relevant docs

## Testing

### Manual Testing

```bash
# Test subdomain discovery
./utils/subdomain_scan.sh -d example.com

# Test HTTP monitoring
./modules/http_monitor.py -u https://example.com

# Test full flow
./monitor.py --init
./monitor.py --monitor
```

### Automated Testing (Coming Soon)

```bash
pytest tests/
```

## Release Process

1. Update version in `modules/__init__.py`
2. Update CHANGELOG.md
3. Create git tag: `git tag v1.x.x`
4. Push tag: `git push origin v1.x.x`
5. Create GitHub release

## Questions?

- Open an issue
- Join discussions
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Bug Bounty Monitoring Framework! 🎯
