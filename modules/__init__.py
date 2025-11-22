"""
Bug Bounty Monitoring Modules
"""

from .subdomain_finder import SubdomainFinder
from .http_monitor import HTTPMonitor
from .dashboard import Dashboard
from .notifier import Notifier

# Optional integrations
__all__ = ['SubdomainFinder', 'HTTPMonitor', 'Dashboard', 'Notifier']

try:
    from .shodan_scanner import ShodanScanner
    __all__.append('ShodanScanner')
except ImportError:
    pass

try:
    from .wayback_analyzer import WaybackAnalyzer
    __all__.append('WaybackAnalyzer')
except ImportError:
    pass

__version__ = '1.0.0'
