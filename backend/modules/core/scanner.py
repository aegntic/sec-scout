#!/usr/bin/env python3
# SecureScout - Core Scanner Engine

import os
import time
import random
import threading
import queue
import logging
import requests
from urllib.parse import urlparse, urljoin
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Set, Tuple, Any, Optional, Callable, Union

# Configure logging
logger = logging.getLogger("securescout.scanner")

class ScannerEngine:
    """
    Core scanning engine for SecureScout.
    Coordinates the execution of all security test modules against the target.
    """
    
    def __init__(self, scan_id: str, config: Dict[str, Any]):
        """
        Initialize the scanner engine.
        
        Args:
            scan_id: Unique identifier for this scan
            config: Dictionary containing scan configuration settings
        """
        self.scan_id = scan_id
        self.config = config
        self.target_url = config.get('target_url')
        self.max_depth = config.get('max_depth', 3)
        self.max_pages = config.get('max_pages', 200)
        self.thread_count = config.get('threads', 10)
        self.request_delay = config.get('request_delay', 0.5)
        self.jitter = config.get('jitter', 0.2)
        self.modules = config.get('modules', [])
        self.scan_type = config.get('scan_type', 'standard')
        self.user_agent_rotation = config.get('user_agent_rotation', True)
        self.ip_rotation = config.get('ip_rotation', False)
        self.stealth_level = config.get('stealth_level', 'medium')
        self.custom_headers = config.get('custom_headers', {})
        self.custom_cookies = config.get('custom_cookies', {})
        self.authentication = config.get('authentication', None)
        
        # Initialize scan state
        self.start_time = datetime.utcnow()
        self.end_time = None
        self.status = "initializing"
        self.progress = 0
        self.paused = False
        self.stopped = False
        self.errors = []
        self.findings = []
        self.page_queue = queue.Queue()
        self.visited_urls = set()
        self.crawled_urls = set()
        self.current_module = None
        
        # Active test modules
        self.active_modules = []
        
        # Set up proxy if IP rotation is enabled
        self.proxies = self._setup_proxies() if self.ip_rotation else None
        
        # User agent list for rotation
        self.user_agents = self._load_user_agents()
        self.current_user_agent = self._get_random_user_agent()
        
        # Create session with default configuration
        self.session = self._create_session()
    
    def _setup_proxies(self) -> Dict[str, str]:
        """Set up proxy configuration if IP rotation is enabled."""
        # In a real implementation, this would configure proxy rotation
        # For demo purposes, just return a placeholder
        return None
    
    def _load_user_agents(self) -> List[str]:
        """Load a list of user agents for rotation."""
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36",
        ]
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent from the list."""
        return random.choice(self.user_agents)
    
    def _create_session(self) -> requests.Session:
        """Create and configure a requests session with default settings."""
        session = requests.Session()
        
        # Set default headers
        headers = {
            "User-Agent": self.current_user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "DNT": "1"  # Do Not Track header
        }
        
        # Add custom headers if provided
        if self.custom_headers:
            headers.update(self.custom_headers)
        
        session.headers.update(headers)
        
        # Add custom cookies if provided
        if self.custom_cookies:
            for key, value in self.custom_cookies.items():
                session.cookies.set(key, value)
        
        # Set proxies if IP rotation is enabled
        if self.proxies:
            session.proxies.update(self.proxies)
        
        return session
    
    def _rotate_user_agent(self):
        """Rotate to a different user agent if rotation is enabled."""
        if self.user_agent_rotation:
            new_user_agent = self._get_random_user_agent()
            # Ensure we don't use the same user agent twice in a row
            while new_user_agent == self.current_user_agent and len(self.user_agents) > 1:
                new_user_agent = self._get_random_user_agent()
            
            self.current_user_agent = new_user_agent
            self.session.headers.update({"User-Agent": self.current_user_agent})
    
    def _add_jitter(self, delay: float) -> float:
        """Add random jitter to delay time to avoid pattern detection."""
        if self.jitter <= 0:
            return delay
        
        jitter_amount = random.uniform(-self.jitter, self.jitter)
        new_delay = delay + (delay * jitter_amount)
        
        # Ensure the delay doesn't go below 0
        return max(0.1, new_delay)
    
    def _wait_between_requests(self):
        """Implement delay between requests with jitter."""
        delay = self._add_jitter(self.request_delay)
        time.sleep(delay)
    
    def _make_request(self, url: str, method: str = 'GET', 
                     data: Dict = None, json: Dict = None, 
                     headers: Dict = None, cookies: Dict = None,
                     allow_redirects: bool = True) -> Tuple[requests.Response, Any]:
        """
        Make an HTTP request with the configured session.
        
        Returns:
            Tuple of (response, error)
        """
        error = None
        response = None
        
        try:
            # Rotate user agent if enabled
            if self.user_agent_rotation:
                self._rotate_user_agent()
            
            # Apply request delay
            self._wait_between_requests()
            
            # Build request parameters
            request_params = {
                'method': method,
                'url': url,
                'allow_redirects': allow_redirects,
                'timeout': 30
            }
            
            if data:
                request_params['data'] = data
            
            if json:
                request_params['json'] = json
            
            if headers:
                request_params['headers'] = headers
            
            if cookies:
                request_params['cookies'] = cookies
            
            logger.debug(f"Making {method} request to {url}")
            response = self.session.request(**request_params)
            
            # Check for rate limiting or other anomalies
            if response.status_code == 429:
                logger.warning(f"Rate limiting detected at {url}. Increasing delays.")
                self.request_delay = min(self.request_delay * 2, 10)  # Increase delay up to max 10s
                
            # Log warnings for other error status codes
            elif response.status_code >= 400:
                logger.warning(f"Received status code {response.status_code} from {url}")
            
        except requests.exceptions.Timeout as e:
            error = f"Request timeout: {str(e)}"
            logger.warning(f"Timeout error for {url}: {error}")
        
        except requests.exceptions.ConnectionError as e:
            error = f"Connection error: {str(e)}"
            logger.warning(f"Connection error for {url}: {error}")
        
        except requests.exceptions.RequestException as e:
            error = f"Request error: {str(e)}"
            logger.warning(f"Request error for {url}: {error}")
        
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error for {url}: {error}")
        
        return response, error
    
    def _authenticate(self) -> bool:
        """
        Perform authentication if required.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self.authentication:
            return True
        
        auth_type = self.authentication.get('type')
        
        if auth_type == 'form':
            return self._form_authentication()
        elif auth_type == 'basic':
            return self._basic_authentication()
        elif auth_type == 'token':
            return self._token_authentication()
        else:
            logger.error(f"Unsupported authentication type: {auth_type}")
            return False
    
    def _form_authentication(self) -> bool:
        """Handle form-based authentication."""
        # Implementation would vary based on the specific application
        # This is a simplistic example
        try:
            auth_url = self.authentication.get('auth_url')
            username = self.authentication.get('username')
            password = self.authentication.get('password')
            
            if not auth_url or not username or not password:
                logger.error("Missing credentials for form authentication")
                return False
            
            # Simple form authentication - real implementations would need to handle
            # CSRF tokens, multi-step forms, etc.
            data = {
                'username': username,
                'password': password
            }
            
            response, error = self._make_request(
                url=auth_url,
                method='POST',
                data=data,
                allow_redirects=True
            )
            
            if error:
                logger.error(f"Authentication failed: {error}")
                return False
            
            # Check if authentication was successful (this would vary by application)
            # Could check for cookies, redirect to dashboard, etc.
            if response.status_code == 200 and 'login' not in response.url.lower():
                logger.info("Form authentication successful")
                return True
            else:
                logger.error(f"Form authentication failed with status code {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Form authentication error: {str(e)}")
            return False
    
    def _basic_authentication(self) -> bool:
        """Handle HTTP Basic Authentication."""
        try:
            username = self.authentication.get('username')
            password = self.authentication.get('password')
            
            if not username or not password:
                logger.error("Missing credentials for basic authentication")
                return False
            
            # Apply basic auth to session
            self.session.auth = (username, password)
            
            # Test authentication with a request to the base URL
            response, error = self._make_request(
                url=self.target_url,
                method='GET'
            )
            
            if error:
                logger.error(f"Authentication failed: {error}")
                return False
            
            if response.status_code == 200:
                logger.info("Basic authentication successful")
                return True
            else:
                logger.error(f"Basic authentication failed with status code {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Basic authentication error: {str(e)}")
            return False
    
    def _token_authentication(self) -> bool:
        """Handle token-based authentication."""
        try:
            token = self.authentication.get('token')
            
            if not token:
                logger.error("Missing token for token authentication")
                return False
            
            # Add token to headers
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
            
            # Test authentication with a request to the base URL
            response, error = self._make_request(
                url=self.target_url,
                method='GET'
            )
            
            if error:
                logger.error(f"Authentication failed: {error}")
                return False
            
            if response.status_code == 200:
                logger.info("Token authentication successful")
                return True
            else:
                logger.error(f"Token authentication failed with status code {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Token authentication error: {str(e)}")
            return False
    
    def start(self):
        """Start the scanning process."""
        try:
            logger.info(f"Starting scan {self.scan_id} for target {self.target_url}")
            self.status = "running"
            
            # Authenticate if required
            if self.authentication:
                logger.info("Authenticating to target application")
                if not self._authenticate():
                    self.status = "failed"
                    self.errors.append("Authentication failed")
                    logger.error("Scan aborted due to authentication failure")
                    return
            
            # Initialize module registry
            self._initialize_modules()
            
            # Start with discovery/crawling
            logger.info("Starting discovery phase")
            self._discovery_phase()
            
            # Run active test modules
            logger.info("Starting vulnerability testing phase")
            self._testing_phase()
            
            # Finalize scan
            logger.info("Finalizing scan")
            self._finalize_scan()
            
        except Exception as e:
            logger.error(f"Scan error: {str(e)}")
            self.status = "failed"
            self.errors.append(f"Scan error: {str(e)}")
    
    def _initialize_modules(self):
        """Initialize and prepare all test modules."""
        from modules.discovery import WebCrawler
        from modules.test_modules import SQLInjection, XSSScanner, CSRFScanner, HeaderAnalyzer
        
        # Set up core discovery module
        self.crawler = WebCrawler(self)
        
        # Initialize requested test modules based on scan config
        if 'injection' in self.modules:
            self.active_modules.append(SQLInjection(self))
        
        if 'xss' in self.modules:
            self.active_modules.append(XSSScanner(self))
        
        if 'csrf' in self.modules:
            self.active_modules.append(CSRFScanner(self))
        
        if 'headers' in self.modules:
            self.active_modules.append(HeaderAnalyzer(self))
        
        # Additional modules would be initialized here
        
        logger.info(f"Initialized {len(self.active_modules)} test modules")
    
    def _discovery_phase(self):
        """Run the discovery/crawling phase."""
        # Start with the target URL
        self.page_queue.put((self.target_url, 0))  # URL and depth
        
        # Set the current module for progress tracking
        self.current_module = "discovery"
        
        # Run the crawler
        self.crawler.crawl()
        
        logger.info(f"Discovery completed. Found {len(self.crawled_urls)} pages.")
    
    def _testing_phase(self):
        """Run all active test modules against discovered endpoints."""
        # Calculate progress increment per module
        if len(self.active_modules) > 0:
            progress_per_module = 75 / len(self.active_modules)
        else:
            progress_per_module = 0
        
        current_progress = 25  # Discovery phase is 25%
        
        # Run each test module
        for module in self.active_modules:
            if self.stopped:
                logger.info("Scan was stopped. Terminating testing phase.")
                break
            
            self.current_module = module.name
            self.progress = current_progress
            
            logger.info(f"Running test module: {module.name}")
            
            try:
                # Run the test module
                module.run()
                
                # Update progress
                current_progress += progress_per_module
                self.progress = min(current_progress, 100)
                
            except Exception as e:
                logger.error(f"Error in module {module.name}: {str(e)}")
                self.errors.append(f"Module {module.name} error: {str(e)}")
        
        # Ensure progress is at 100% when complete
        if not self.stopped:
            self.progress = 100
    
    def _finalize_scan(self):
        """Finalize the scan and prepare results."""
        if self.stopped:
            self.status = "stopped"
        else:
            self.status = "completed"
        
        self.end_time = datetime.utcnow()
        self.progress = 100
        logger.info(f"Scan {self.scan_id} completed with {len(self.findings)} findings")
    
    def pause(self):
        """Pause the scan."""
        self.paused = True
        self.status = "paused"
        logger.info(f"Scan {self.scan_id} paused")
    
    def resume(self):
        """Resume a paused scan."""
        self.paused = False
        self.status = "running"
        logger.info(f"Scan {self.scan_id} resumed")
    
    def stop(self):
        """Stop the scan."""
        self.stopped = True
        self.status = "stopping"
        logger.info(f"Scan {self.scan_id} stopping")
    
    def add_finding(self, finding: Dict[str, Any]):
        """
        Add a security finding to the scan results.
        
        Args:
            finding: Dictionary containing finding details
        """
        # Generate a unique ID for the finding
        if 'id' not in finding:
            finding['id'] = f"finding-{len(self.findings) + 1}"
        
        # Add timestamp if not present
        if 'timestamp' not in finding:
            finding['timestamp'] = datetime.utcnow().isoformat()
        
        self.findings.append(finding)
        logger.info(f"Added finding: {finding.get('title')} ({finding.get('severity')})")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current scan status.
        
        Returns:
            Dict containing scan status information
        """
        return {
            'scan_id': self.scan_id,
            'status': self.status,
            'progress': self.progress,
            'current_module': self.current_module,
            'target_url': self.target_url,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'findings_count': len(self.findings),
            'errors': self.errors
        }
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get the complete scan results.
        
        Returns:
            Dict containing full scan results
        """
        return {
            'scan_id': self.scan_id,
            'target_url': self.target_url,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'scan_type': self.scan_type,
            'modules': self.modules,
            'findings': self.findings,
            'errors': self.errors,
            'stats': {
                'pages_crawled': len(self.crawled_urls),
                'total_findings': len(self.findings),
                'findings_by_severity': self._count_findings_by_severity()
            }
        }
    
    def _count_findings_by_severity(self) -> Dict[str, int]:
        """Count findings by severity level."""
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        
        for finding in self.findings:
            severity = finding.get('severity', 'info').lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        return severity_counts