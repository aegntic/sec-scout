#!/usr/bin/env python3
# SecureScout - Advanced Asynchronous Web Crawler

import re
import logging
import asyncio
import aiohttp
from urllib.parse import urlparse, urljoin, urldefrag
from typing import Dict, List, Set, Tuple, Any, Optional
import time
import random
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
import json

logger = logging.getLogger("securescout.async_crawler")

@dataclass
class CrawlResult:
    """Result of a crawling operation."""
    urls: Set[str] = field(default_factory=set)
    forms: List[Dict[str, Any]] = field(default_factory=list)
    inputs: List[Dict[str, Any]] = field(default_factory=list)
    endpoints: List[Dict[str, Any]] = field(default_factory=list)
    javascript_files: List[str] = field(default_factory=list)
    static_files: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    sitemap_urls: Set[str] = field(default_factory=set)
    api_endpoints: Set[str] = field(default_factory=set)

class AsyncWebCrawler:
    """
    Advanced asynchronous web crawler for discovering application structure and endpoints.
    Implements intelligent crawling with depth control and resource prioritization.
    """
    
    def __init__(self, scanner):
        """
        Initialize the web crawler.
        
        Args:
            scanner: Reference to the parent AsyncScannerEngine
        """
        self.scanner = scanner
        self.visited_urls = set()
        self.found_urls = set()
        self.crawled_pages = set()
        self.url_queue = asyncio.Queue()
        self.max_depth = scanner.config.max_depth
        self.max_pages = scanner.config.max_pages
        self.base_url = scanner.config.target.url
        self.domain = urlparse(scanner.config.target.url).netloc
        self.concurrency = scanner.config.concurrency
        self.results = CrawlResult()
        
        # Patterns for identifying different types of content
        self.patterns = {
            'robots': re.compile(r'^/robots\.txt$'),
            'sitemap': re.compile(r'^/sitemap\.xml$'),
            'api_endpoint': re.compile(r'^/api/|/v[0-9]+/|graphql|/rest/'),
            'static_file': re.compile(r'\.(css|js|jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot)$', re.IGNORECASE),
            'document': re.compile(r'\.(pdf|doc|docx|xls|xlsx|txt|rtf|csv)$', re.IGNORECASE),
            'email': re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
            'phone': re.compile(r'\b(?:\+?[0-9]{1,3}[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'),
        }
        
        # Detect technologies
        self.tech_signatures = {
            'wordpress': [
                {'type': 'url', 'pattern': '/wp-content/'},
                {'type': 'url', 'pattern': '/wp-includes/'},
                {'type': 'header', 'name': 'X-Powered-By', 'pattern': 'WordPress'}
            ],
            'drupal': [
                {'type': 'url', 'pattern': '/sites/default/files/'},
                {'type': 'header', 'name': 'X-Generator', 'pattern': 'Drupal'}
            ],
            'joomla': [
                {'type': 'url', 'pattern': '/administrator/'},
                {'type': 'meta', 'name': 'generator', 'pattern': 'Joomla'}
            ],
            'php': [
                {'type': 'header', 'name': 'X-Powered-By', 'pattern': 'PHP'}
            ],
            'aspnet': [
                {'type': 'header', 'name': 'X-AspNet-Version', 'pattern': ''},
                {'type': 'header', 'name': 'X-Powered-By', 'pattern': 'ASP.NET'}
            ],
            'nginx': [
                {'type': 'header', 'name': 'Server', 'pattern': 'nginx'}
            ],
            'apache': [
                {'type': 'header', 'name': 'Server', 'pattern': 'Apache'}
            ],
            'jquery': [
                {'type': 'script', 'pattern': 'jquery'}
            ],
            'bootstrap': [
                {'type': 'script', 'pattern': 'bootstrap'},
                {'type': 'css', 'pattern': 'bootstrap'}
            ],
            'react': [
                {'type': 'script', 'pattern': 'react'},
                {'type': 'meta', 'name': 'react-router'}
            ],
            'angular': [
                {'type': 'script', 'pattern': 'angular'},
                {'type': 'attribute', 'name': 'ng-'}
            ],
            'vue': [
                {'type': 'script', 'pattern': 'vue.js'},
                {'type': 'attribute', 'name': 'v-'}
            ],
            'laravel': [
                {'type': 'header', 'name': 'Set-Cookie', 'pattern': 'laravel_session'},
                {'type': 'meta', 'name': 'csrf-token', 'pattern': ''}
            ],
            'django': [
                {'type': 'header', 'name': 'X-Framework', 'pattern': 'Django'},
                {'type': 'header', 'name': 'Set-Cookie', 'pattern': 'csrftoken'}
            ],
            'express': [
                {'type': 'header', 'name': 'X-Powered-By', 'pattern': 'Express'}
            ],
            'graphql': [
                {'type': 'url', 'pattern': '/graphql'},
                {'type': 'response', 'pattern': '"errors":[{"message":"Must provide query string."'}
            ],
            'aws': [
                {'type': 'header', 'name': 'Server', 'pattern': 'AmazonS3'},
                {'type': 'header', 'name': 'x-amz-', 'pattern': ''}
            ],
            'cloudflare': [
                {'type': 'header', 'name': 'CF-Ray', 'pattern': ''},
                {'type': 'header', 'name': 'cf-cache-status', 'pattern': ''}
            ],
            'jwt': [
                {'type': 'header', 'name': 'Authorization', 'pattern': 'Bearer ey'},
                {'type': 'cookie', 'name': 'jwt', 'pattern': ''}
            ]
        }
    
    def is_same_domain(self, url: str) -> bool:
        """Check if a URL belongs to the same domain as the target."""
        parsed_url = urlparse(url)
        return parsed_url.netloc == self.domain
    
    def is_in_scope(self, url: str) -> bool:
        """Check if a URL is within the defined scan scope."""
        return self.scanner.config.target.is_in_scope(url)
    
    def normalize_url(self, url: str, base_url: str = None) -> Optional[str]:
        """
        Normalize a URL by joining it with the base URL if relative,
        and removing fragments.
        """
        if not url:
            return None
        
        # Remove fragments
        url = urldefrag(url)[0]
        
        # Skip non-HTTP URLs
        if url.startswith(('javascript:', 'mailto:', 'tel:', 'data:', '#')):
            return None
        
        # Use provided base or the scanner's base URL
        if base_url is None:
            base_url = self.base_url
        
        # Convert relative URLs to absolute
        if not url.startswith(('http://', 'https://')):
            url = urljoin(base_url, url)
        
        return url
    
    def prioritize_url(self, url: str, in_links_count: int = 0) -> int:
        """
        Assign a priority score to a URL for crawling.
        Higher scores are crawled first.
        """
        parsed_url = urlparse(url)
        path = parsed_url.path
        query = parsed_url.query
        
        # Base priority score
        priority = 100
        
        # Priority adjustments based on URL characteristics
        if path == '/' or path == '':
            priority += 100  # Homepage is highest priority
        
        # URLs with fewer path segments are higher priority
        segments = [s for s in path.split('/') if s]
        priority -= len(segments) * 5
        
        # API endpoints get higher priority
        if self.patterns['api_endpoint'].search(path):
            priority += 50
        
        # URLs with query parameters get lower priority
        if query:
            priority -= 10 + 2 * len(query.split('&'))
        
        # URLs with more incoming links get higher priority
        priority += in_links_count * 3
        
        # Static files get lower priority
        if self.patterns['static_file'].search(path):
            priority -= 30
        
        # Documents get lower priority
        if self.patterns['document'].search(path):
            priority -= 30
        
        return priority
    
    async def extract_links(self, html_content: str, base_url: str) -> Set[str]:
        """
        Extract all links from HTML content.
        
        Args:
            html_content: HTML content to parse
            base_url: Base URL for resolving relative links
            
        Returns:
            Set of absolute URLs
        """
        links = set()
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract URLs from anchor tags
            for a_tag in soup.find_all('a', href=True):
                url = self.normalize_url(a_tag['href'], base_url)
                if url and self.is_in_scope(url):
                    links.add(url)
            
            # Extract URLs from form actions
            for form in soup.find_all('form', action=True):
                url = self.normalize_url(form['action'], base_url)
                if url and self.is_in_scope(url):
                    links.add(url)
            
            # Extract URLs from iframes
            for iframe in soup.find_all('iframe', src=True):
                url = self.normalize_url(iframe['src'], base_url)
                if url and self.is_in_scope(url):
                    links.add(url)
            
            # Extract URLs from script tags
            for script in soup.find_all('script', src=True):
                url = self.normalize_url(script['src'], base_url)
                if url and self.is_in_scope(url):
                    links.add(url)
                    # Track JavaScript files
                    if url.endswith('.js'):
                        self.results.javascript_files.append(url)
            
            # Extract URLs from link tags
            for link in soup.find_all('link', href=True):
                url = self.normalize_url(link['href'], base_url)
                if url and self.is_in_scope(url):
                    links.add(url)
                    # Track CSS files
                    if url.endswith('.css'):
                        self.results.static_files.append(url)
            
            # Extract URLs from images
            for img in soup.find_all('img', src=True):
                url = self.normalize_url(img['src'], base_url)
                if url and self.is_in_scope(url):
                    links.add(url)
                    # Track image files
                    if self.patterns['static_file'].search(url):
                        self.results.static_files.append(url)
            
        except Exception as e:
            logger.error(f"Error extracting links from {base_url}: {str(e)}")
        
        return links
    
    async def extract_forms(self, html_content: str, base_url: str) -> List[Dict]:
        """
        Extract forms from HTML content.
        
        Args:
            html_content: HTML content to parse
            base_url: Base URL for resolving relative links
            
        Returns:
            List of dictionaries containing form information
        """
        forms = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for form in soup.find_all('form'):
                form_data = {
                    'page_url': base_url,
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get').upper(),
                    'inputs': []
                }
                
                # Normalize the action URL
                if form_data['action']:
                    form_data['action'] = self.normalize_url(form_data['action'], base_url)
                else:
                    form_data['action'] = base_url
                
                # Extract all input fields
                for input_field in form.find_all(['input', 'textarea', 'select']):
                    input_type = input_field.get('type', 'text') if input_field.name == 'input' else input_field.name
                    input_name = input_field.get('name', '')
                    input_value = input_field.get('value', '')
                    input_id = input_field.get('id', '')
                    input_required = input_field.get('required', False)
                    input_placeholder = input_field.get('placeholder', '')
                    
                    input_data = {
                        'type': input_type,
                        'name': input_name,
                        'value': input_value,
                        'id': input_id,
                        'required': bool(input_required),
                        'placeholder': input_placeholder
                    }
                    
                    form_data['inputs'].append(input_data)
                    
                    # Track input fields separately for testing
                    self.results.inputs.append({
                        'page_url': base_url,
                        'form_action': form_data['action'],
                        'form_method': form_data['method'],
                        'type': input_type,
                        'name': input_name,
                        'id': input_id,
                        'required': bool(input_required),
                        'placeholder': input_placeholder
                    })
                
                # Look for hidden CSRF tokens
                csrf_inputs = [i for i in form_data['inputs'] 
                              if (i['type'] == 'hidden' and 
                                 ('csrf' in i['name'].lower() or 
                                  'token' in i['name'].lower()))]
                
                if csrf_inputs:
                    form_data['has_csrf'] = True
                    form_data['csrf_field'] = csrf_inputs[0]['name']
                else:
                    form_data['has_csrf'] = False
                
                # Check for file uploads
                file_inputs = [i for i in form_data['inputs'] if i['type'] == 'file']
                form_data['has_file_upload'] = len(file_inputs) > 0
                
                # Check for password fields
                password_inputs = [i for i in form_data['inputs'] if i['type'] == 'password']
                form_data['has_password'] = len(password_inputs) > 0
                
                # Assess form purpose
                form_data['purpose'] = self._assess_form_purpose(form_data)
                
                forms.append(form_data)
                self.results.forms.append(form_data)
                
        except Exception as e:
            logger.error(f"Error extracting forms from {base_url}: {str(e)}")
        
        return forms
    
    def _assess_form_purpose(self, form_data: Dict) -> str:
        """Assess the likely purpose of a form based on its fields."""
        inputs = form_data['inputs']
        input_names = [i['name'].lower() for i in inputs if i['name']]
        input_types = [i['type'].lower() for i in inputs if i['type']]
        input_placeholders = [i['placeholder'].lower() for i in inputs if i['placeholder']]
        
        # Login form detection
        if ('password' in input_types and 
            any(name in ' '.join(input_names) for name in ['user', 'email', 'login', 'name'])):
            return 'login'
        
        # Registration form detection
        if ('password' in input_types and 
            ('confirm' in ' '.join(input_names) or 
             'password' in ' '.join(input_names) and input_names.count('password') > 1)):
            return 'registration'
        
        # Search form detection
        if (len(inputs) == 1 and 
            any(term in ' '.join(input_names + input_placeholders) 
                for term in ['search', 'find', 'query', 'q'])):
            return 'search'
        
        # Contact form detection
        if (any(term in ' '.join(input_names + input_placeholders) 
               for term in ['contact', 'message', 'email', 'name', 'subject'])):
            return 'contact'
        
        # File upload form detection
        if 'file' in input_types:
            return 'file_upload'
        
        # Payment form detection
        if any(term in ' '.join(input_names + input_placeholders) 
              for term in ['card', 'credit', 'payment', 'cvv', 'ccv']):
            return 'payment'
        
        return 'unknown'
    
    async def extract_endpoints(self, html_content: str, base_url: str) -> List[Dict]:
        """
        Extract potential API endpoints and other interesting URLs.
        
        Args:
            html_content: HTML content to parse
            base_url: Base URL of the page
            
        Returns:
            List of dictionaries containing endpoint information
        """
        endpoints = []
        try:
            # Extract URLs from JavaScript code
            js_urls = re.findall(r'["\'](/[^"\']*?)["\']', html_content)
            for url in js_urls:
                if self.patterns['api_endpoint'].search(url):
                    full_url = self.normalize_url(url, base_url)
                    if full_url and self.is_in_scope(full_url):
                        endpoints.append({
                            'url': full_url,
                            'source': base_url,
                            'type': 'api',
                            'method': 'GET'  # Default, can't determine from static analysis
                        })
                        self.results.api_endpoints.add(full_url)
            
            # Extract API endpoints from fetch/axios calls
            api_calls = re.findall(r'(fetch|axios)\s*\(\s*["\']([^"\']+)["\']', html_content)
            for _, url in api_calls:
                full_url = self.normalize_url(url, base_url)
                if full_url and self.is_in_scope(full_url):
                    endpoints.append({
                        'url': full_url,
                        'source': base_url,
                        'type': 'api',
                        'method': 'GET'  # Default, can't determine from static analysis
                    })
                    self.results.api_endpoints.add(full_url)
            
            # Look for URL patterns in JavaScript variables
            url_vars = re.findall(r'(url|endpoint|api)\s*[:=]\s*["\']([^"\']+)["\']', html_content, re.IGNORECASE)
            for _, url in url_vars:
                if url.startswith('/') or url.startswith('http'):
                    full_url = self.normalize_url(url, base_url)
                    if full_url and self.is_in_scope(full_url):
                        endpoints.append({
                            'url': full_url,
                            'source': base_url,
                            'type': 'api',
                            'method': 'GET'  # Default
                        })
                        self.results.api_endpoints.add(full_url)
            
            # Look for GraphQL endpoints
            graphql_patterns = [
                r'(graphql|gql)\s*:\s*["\']([^"\']+)["\']',
                r'(GraphQL|GQL).*["\']([^"\']+/graphql[^"\']*)["\']'
            ]
            
            for pattern in graphql_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for _, url in matches:
                    full_url = self.normalize_url(url, base_url)
                    if full_url and self.is_in_scope(full_url):
                        endpoints.append({
                            'url': full_url,
                            'source': base_url,
                            'type': 'graphql',
                            'method': 'POST'  # GraphQL typically uses POST
                        })
                        self.results.api_endpoints.add(full_url)
            
        except Exception as e:
            logger.error(f"Error extracting endpoints from {base_url}: {str(e)}")
        
        # Add unique endpoints to results
        for endpoint in endpoints:
            if endpoint not in self.results.endpoints:
                self.results.endpoints.append(endpoint)
        
        return endpoints
    
    async def detect_technologies(self, response, html_content: str) -> List[str]:
        """
        Detect technologies used by the website.
        
        Args:
            response: HTTP response object
            html_content: HTML content to analyze
            
        Returns:
            List of detected technologies
        """
        detected = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for tech, signatures in self.tech_signatures.items():
                for signature in signatures:
                    if signature['type'] == 'header' and response:
                        header_value = response.headers.get(signature['name'])
                        if header_value and (not signature['pattern'] or signature['pattern'] in header_value):
                            if tech not in detected:
                                detected.append(tech)
                    
                    elif signature['type'] == 'meta':
                        meta = soup.find('meta', attrs={'name': signature['name']})
                        if meta and 'content' in meta.attrs:
                            if not signature['pattern'] or signature['pattern'] in meta['content']:
                                if tech not in detected:
                                    detected.append(tech)
                    
                    elif signature['type'] == 'script':
                        scripts = soup.find_all('script', src=True)
                        for script in scripts:
                            if signature['pattern'] in script['src'].lower():
                                if tech not in detected:
                                    detected.append(tech)
                    
                    elif signature['type'] == 'css':
                        links = soup.find_all('link', rel="stylesheet", href=True)
                        for link in links:
                            if signature['pattern'] in link['href'].lower():
                                if tech not in detected:
                                    detected.append(tech)
                    
                    elif signature['type'] == 'url' and response:
                        if signature['pattern'] in response.url:
                            if tech not in detected:
                                detected.append(tech)
                    
                    elif signature['type'] == 'attribute':
                        elements = soup.find_all(lambda tag: any(attr.startswith(signature['name']) for attr in tag.attrs))
                        if elements:
                            if tech not in detected:
                                detected.append(tech)
                    
                    elif signature['type'] == 'cookie' and response:
                        cookies = response.cookies
                        if signature['name'] in cookies:
                            if tech not in detected:
                                detected.append(tech)
                    
                    elif signature['type'] == 'response' and isinstance(html_content, str):
                        if signature['pattern'] in html_content:
                            if tech not in detected:
                                detected.append(tech)
        
        except Exception as e:
            logger.error(f"Error detecting technologies: {str(e)}")
        
        # Update global results
        for tech in detected:
            if tech not in self.results.technologies:
                self.results.technologies.append(tech)
                # Also update scanner state for reporting
                if hasattr(self.scanner.state, 'detected_technologies'):
                    self.scanner.state.detected_technologies.append(tech)
        
        return detected
    
    async def crawl_page(self, url: str, depth: int) -> None:
        """
        Crawl a single page, extract information, and queue new links.
        
        Args:
            url: URL to crawl
            depth: Current crawl depth
        """
        # Skip if out of bounds or stopped
        if (self.scanner.stop_event.is_set() or 
            depth > self.max_depth or 
            len(self.crawled_pages) >= self.max_pages):
            return
        
        # Skip if already visited
        if url in self.visited_urls:
            return
        
        # Wait if scan is paused
        await self.scanner.pause_event.wait()
        
        # Mark as visited to prevent duplicates
        self.visited_urls.add(url)
        
        logger.debug(f"Crawling {url} at depth {depth}")
        
        try:
            # Get the page content
            response, data, error = await self.scanner.fetch(url=url, method='GET')
            
            if error or not response:
                logger.warning(f"Failed to crawl {url}: {error}")
                return
            
            # Skip non-HTML responses for parsing but still mark as crawled
            content_type = response.headers.get('Content-Type', '')
            if not isinstance(data, str) or ('text/html' not in content_type and 'application/json' not in content_type):
                self.crawled_pages.add(url)
                return
            
            # For JSON responses, look for API endpoints
            if 'application/json' in content_type and isinstance(data, (dict, list)):
                self.crawled_pages.add(url)
                # Add this as an API endpoint
                api_endpoint = {
                    'url': url,
                    'source': 'crawler',
                    'type': 'api',
                    'method': 'GET'
                }
                self.results.endpoints.append(api_endpoint)
                self.results.api_endpoints.add(url)
                return
            
            # Parse the HTML content
            html_content = data
            
            # Extract links
            links = await self.extract_forms(html_content, url)
            
            # Extract forms
            forms = await self.extract_forms(html_content, url)
            
            # Extract endpoints
            endpoints = await self.extract_endpoints(html_content, url)
            
            # Detect technologies
            technologies = await self.detect_technologies(response, html_content)
            
            # Extract links
            links = await self.extract_links(html_content, url)
            
            # Mark as successfully crawled
            self.crawled_pages.add(url)
            self.results.urls.add(url)
            
            # Update scanner progress
            self.scanner.state.pages_crawled = len(self.crawled_pages)
            self.scanner.state.calculate_progress(self.scanner.config)
            
            # Queue new links for crawling if not at max depth
            if depth < self.max_depth:
                for link in links:
                    if (link not in self.visited_urls and 
                        link not in self.found_urls and 
                        len(self.crawled_pages) < self.max_pages):
                        priority = self.prioritize_url(link)
                        await self.url_queue.put((priority, link, depth + 1))
                        self.found_urls.add(link)
            
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
    
    async def process_queue(self):
        """Process URLs from the priority queue."""
        active_tasks = set()
        
        while True:
            try:
                # Check if we should stop
                if (self.scanner.stop_event.is_set() or 
                    len(self.crawled_pages) >= self.max_pages or
                    self.url_queue.empty() and len(active_tasks) == 0):
                    break
                
                # Clean up finished tasks
                active_tasks = {task for task in active_tasks if not task.done()}
                
                # Check if we can start more tasks
                if len(active_tasks) >= self.concurrency:
                    # Wait for a task to complete if we're at max concurrency
                    await asyncio.sleep(0.1)
                    continue
                
                try:
                    # Try to get from queue with a timeout so we can check conditions
                    priority, url, depth = await asyncio.wait_for(self.url_queue.get(), timeout=0.1)
                    
                    # Create and track the task
                    task = asyncio.create_task(self.crawl_page(url, depth))
                    active_tasks.add(task)
                    
                    # Mark task as done in the queue
                    self.url_queue.task_done()
                    
                except asyncio.TimeoutError:
                    # No items in queue, check if all tasks are done
                    if len(active_tasks) == 0 and self.url_queue.empty():
                        break
                    continue
            
            except Exception as e:
                logger.error(f"Error in queue processing: {str(e)}")
                await asyncio.sleep(0.1)
        
        # Wait for remaining tasks to complete
        if active_tasks:
            await asyncio.gather(*active_tasks, return_exceptions=True)
    
    async def crawl(self, start_url: str = None) -> Set[str]:
        """
        Start the crawling process.
        
        Args:
            start_url: Optional URL to start crawling from (defaults to base_url)
            
        Returns:
            Set of crawled URLs
        """
        if not start_url:
            start_url = self.base_url
        
        # Process special files first
        await self._process_special_files()
        
        # Add the initial URL to the queue with high priority
        await self.url_queue.put((1000, start_url, 0))
        self.found_urls.add(start_url)
        
        # Start the queue processing
        await self.process_queue()
        
        # Return the set of crawled URLs
        return self.crawled_pages
    
    async def _process_special_files(self) -> None:
        """Process special files like robots.txt and sitemap.xml."""
        # Process robots.txt
        robots_url = urljoin(self.base_url, '/robots.txt')
        response, data, error = await self.scanner.fetch(url=robots_url, method='GET')
        
        if not error and response and response.status_code == 200 and isinstance(data, str):
            logger.info(f"Found robots.txt at {robots_url}")
            
            # Parse robots.txt to find disallowed paths and sitemaps
            try:
                lines = data.split('\n')
                for line in lines:
                    line = line.strip()
                    
                    # Extract sitemap URLs
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line[8:].strip()
                        if sitemap_url:
                            logger.info(f"Found sitemap reference: {sitemap_url}")
                            await self._process_sitemap(sitemap_url)
                    
                    # Extract disallowed paths (we'll still crawl these, but it's good to know)
                    elif line.lower().startswith('disallow:'):
                        path = line[9:].strip()
                        if path:
                            full_url = urljoin(self.base_url, path)
                            logger.debug(f"Found disallowed path: {full_url}")
            except Exception as e:
                logger.error(f"Error parsing robots.txt: {str(e)}")
        
        # Check for sitemap.xml if not found in robots.txt
        sitemap_url = urljoin(self.base_url, '/sitemap.xml')
        await self._process_sitemap(sitemap_url)
    
    async def _process_sitemap(self, sitemap_url: str) -> None:
        """
        Process a sitemap file to extract URLs.
        
        Args:
            sitemap_url: URL of the sitemap file
        """
        response, data, error = await self.scanner.fetch(url=sitemap_url, method='GET')
        
        if error or not response or response.status != 200 or not isinstance(data, str):
            return
        
        logger.info(f"Processing sitemap: {sitemap_url}")
        
        try:
            # Check if this is a sitemap index with multiple sitemaps
            if '<sitemapindex' in data:
                soup = BeautifulSoup(data, 'xml')
                for sitemap in soup.find_all('sitemap'):
                    loc = sitemap.find('loc')
                    if loc:
                        child_sitemap_url = loc.text
                        # Process child sitemap
                        await self._process_sitemap(child_sitemap_url)
            
            # Parse sitemap for URLs
            elif '<urlset' in data:
                soup = BeautifulSoup(data, 'xml')
                for url_element in soup.find_all('url'):
                    loc = url_element.find('loc')
                    if loc:
                        url = loc.text
                        # Add to sitemap URLs
                        self.results.sitemap_urls.add(url)
                        
                        # Only process URLs from the same domain and in scope
                        if self.is_in_scope(url):
                            # Add URL to queue if not already visited
                            if url not in self.visited_urls and url not in self.found_urls:
                                priority = self.prioritize_url(url, in_links_count=2)  # Higher priority for sitemap URLs
                                await self.url_queue.put((priority, url, 0))
                                self.found_urls.add(url)
                                logger.debug(f"Added URL from sitemap: {url}")
        
        except Exception as e:
            logger.error(f"Error processing sitemap {sitemap_url}: {str(e)}")

# For testing
async def test_crawler(url: str):
    """Test the crawler on a given URL."""
    from async_scanner import ScannerEngine, ScanConfig, ScanTarget
    
    # Create scan configuration
    target = ScanTarget(url=url)
    config = ScanConfig(
        scan_id="test",
        target=target,
        max_depth=2,
        max_pages=20,
        concurrency=5
    )
    
    # Create scanner engine
    scanner = ScannerEngine(config)
    
    # Create and run crawler
    crawler = AsyncWebCrawler(scanner)
    crawled_urls = await crawler.crawl()
    
    print(f"Crawled {len(crawled_urls)} URLs:")
    for url in sorted(crawled_urls):
        print(f"  {url}")
    
    print(f"\nDetected technologies: {crawler.results.technologies}")
    
    print(f"\nFound {len(crawler.results.forms)} forms")
    print(f"Found {len(crawler.results.endpoints)} potential API endpoints")
    
    return crawler.results

if __name__ == "__main__":
    import sys
    import asyncio
    
    if len(sys.argv) < 2:
        print("Usage: python async_crawler.py <target_url>")
        sys.exit(1)
    
    target_url = sys.argv[1]
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_crawler(target_url))