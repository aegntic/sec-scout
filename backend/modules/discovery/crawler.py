#!/usr/bin/env python3
# SecureScout - Web Crawler Module

import re
import logging
import threading
import queue
from urllib.parse import urlparse, urljoin, urldefrag
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Set, Tuple, Any, Optional
import time
import random
from bs4 import BeautifulSoup
import requests

logger = logging.getLogger("securescout.crawler")

class WebCrawler:
    """
    Advanced web crawler for discovering application structure and endpoints.
    Implements intelligent crawling with depth control and resource prioritization.
    """
    
    def __init__(self, scanner):
        """
        Initialize the web crawler.
        
        Args:
            scanner: Reference to the parent ScannerEngine
        """
        self.scanner = scanner
        self.visited_urls = set()
        self.found_urls = set()
        self.crawled_pages = set()
        self.page_queue = queue.Queue()
        self.max_depth = scanner.max_depth
        self.max_pages = scanner.max_pages
        self.base_url = scanner.target_url
        self.domain = urlparse(scanner.target_url).netloc
        self.thread_count = scanner.thread_count
        self.results = {
            'endpoints': [],
            'forms': [],
            'inputs': [],
            'javascript_files': [],
            'static_files': [],
            'technologies': []
        }
        
        # Patterns for identifying different types of content
        self.patterns = {
            'robots': re.compile(r'^/robots\.txt$'),
            'sitemap': re.compile(r'^/sitemap\.xml$'),
            'api_endpoint': re.compile(r'^/api/|/v[0-9]+/'),
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
            ]
        }
    
    def is_same_domain(self, url: str) -> bool:
        """Check if a URL belongs to the same domain as the target."""
        parsed_url = urlparse(url)
        return parsed_url.netloc == self.domain
    
    def normalize_url(self, url: str, base_url: str = None) -> str:
        """
        Normalize a URL by joining it with the base URL if relative,
        and removing fragments.
        """
        if not url:
            return None
        
        # Remove fragments
        url = urldefrag(url)[0]
        
        # Skip non-HTTP URLs
        if url.startswith(('javascript:', 'mailto:', 'tel:', 'data:')):
            return None
        
        # Use provided base or the scanner's base URL
        if base_url is None:
            base_url = self.base_url
        
        # Convert relative URLs to absolute
        if not url.startswith(('http://', 'https://')):
            url = urljoin(base_url, url)
        
        return url
    
    def extract_links(self, html_content: str, base_url: str) -> Set[str]:
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
                if url and self.is_same_domain(url):
                    links.add(url)
            
            # Extract URLs from form actions
            for form in soup.find_all('form', action=True):
                url = self.normalize_url(form['action'], base_url)
                if url and self.is_same_domain(url):
                    links.add(url)
            
            # Extract URLs from iframes
            for iframe in soup.find_all('iframe', src=True):
                url = self.normalize_url(iframe['src'], base_url)
                if url and self.is_same_domain(url):
                    links.add(url)
            
            # Extract URLs from script tags
            for script in soup.find_all('script', src=True):
                url = self.normalize_url(script['src'], base_url)
                if url and self.is_same_domain(url):
                    links.add(url)
                    # Track JavaScript files
                    if url.endswith('.js'):
                        self.results['javascript_files'].append(url)
            
            # Extract URLs from link tags
            for link in soup.find_all('link', href=True):
                url = self.normalize_url(link['href'], base_url)
                if url and self.is_same_domain(url):
                    links.add(url)
                    # Track CSS files
                    if url.endswith('.css'):
                        self.results['static_files'].append(url)
            
            # Extract URLs from images
            for img in soup.find_all('img', src=True):
                url = self.normalize_url(img['src'], base_url)
                if url and self.is_same_domain(url):
                    links.add(url)
                    # Track image files
                    if self.patterns['static_file'].search(url):
                        self.results['static_files'].append(url)
            
        except Exception as e:
            logger.error(f"Error extracting links from {base_url}: {str(e)}")
        
        return links
    
    def extract_forms(self, html_content: str, base_url: str) -> List[Dict]:
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
                    
                    input_data = {
                        'type': input_type,
                        'name': input_name,
                        'value': input_value,
                        'id': input_id
                    }
                    
                    form_data['inputs'].append(input_data)
                    
                    # Track input fields separately for testing
                    self.results['inputs'].append({
                        'page_url': base_url,
                        'form_action': form_data['action'],
                        'form_method': form_data['method'],
                        'type': input_type,
                        'name': input_name,
                        'id': input_id
                    })
                
                forms.append(form_data)
                self.results['forms'].append(form_data)
                
        except Exception as e:
            logger.error(f"Error extracting forms from {base_url}: {str(e)}")
        
        return forms
    
    def extract_endpoints(self, html_content: str, base_url: str) -> List[Dict]:
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
                    if full_url:
                        endpoints.append({
                            'url': full_url,
                            'source': base_url,
                            'type': 'api',
                            'method': 'GET'  # Default, can't determine from static analysis
                        })
            
            # Extract API endpoints from fetch/axios calls
            api_calls = re.findall(r'(fetch|axios)\s*\(\s*["\']([^"\']+)["\']', html_content)
            for _, url in api_calls:
                full_url = self.normalize_url(url, base_url)
                if full_url:
                    endpoints.append({
                        'url': full_url,
                        'source': base_url,
                        'type': 'api',
                        'method': 'GET'  # Default, can't determine from static analysis
                    })
            
            # Look for URL patterns in JavaScript variables
            url_vars = re.findall(r'(url|endpoint|api)\s*[:=]\s*["\']([^"\']+)["\']', html_content, re.IGNORECASE)
            for _, url in url_vars:
                if url.startswith('/') or url.startswith('http'):
                    full_url = self.normalize_url(url, base_url)
                    if full_url:
                        endpoints.append({
                            'url': full_url,
                            'source': base_url,
                            'type': 'api',
                            'method': 'GET'  # Default
                        })
            
        except Exception as e:
            logger.error(f"Error extracting endpoints from {base_url}: {str(e)}")
        
        # Add unique endpoints to results
        for endpoint in endpoints:
            if endpoint not in self.results['endpoints']:
                self.results['endpoints'].append(endpoint)
        
        return endpoints
    
    def detect_technologies(self, response, html_content: str) -> List[str]:
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
        
        except Exception as e:
            logger.error(f"Error detecting technologies: {str(e)}")
        
        # Update global results
        for tech in detected:
            if tech not in self.results['technologies']:
                self.results['technologies'].append(tech)
        
        return detected
    
    def crawl_page(self, url: str, depth: int) -> None:
        """
        Crawl a single page, extract information, and queue new links.
        
        Args:
            url: URL to crawl
            depth: Current crawl depth
        """
        if self.scanner.stopped or depth > self.max_depth or len(self.crawled_pages) >= self.max_pages:
            return
        
        # Skip if already visited
        if url in self.visited_urls:
            return
        
        # Mark as visited to prevent duplicates
        self.visited_urls.add(url)
        
        logger.debug(f"Crawling {url} at depth {depth}")
        
        try:
            # Get the page content
            response, error = self.scanner._make_request(url=url, method='GET')
            
            if error or not response:
                logger.warning(f"Failed to crawl {url}: {error}")
                return
            
            # Skip non-HTML responses
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type and 'application/json' not in content_type:
                # For non-HTML responses, still mark as crawled but don't parse
                self.crawled_pages.add(url)
                return
            
            # Parse the HTML content
            html_content = response.text
            
            # Extract links
            links = self.extract_links(html_content, url)
            
            # Extract forms
            forms = self.extract_forms(html_content, url)
            
            # Extract endpoints
            endpoints = self.extract_endpoints(html_content, url)
            
            # Detect technologies
            technologies = self.detect_technologies(response, html_content)
            
            # Mark as successfully crawled
            self.crawled_pages.add(url)
            
            # Update scanner progress
            self.scanner.progress = min(25, int(len(self.crawled_pages) / self.max_pages * 25))
            
            # Queue new links for crawling if not at max depth
            if depth < self.max_depth:
                for link in links:
                    if link not in self.visited_urls and len(self.crawled_pages) < self.max_pages:
                        self.page_queue.put((link, depth + 1))
                        self.found_urls.add(link)
            
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
    
    def crawl(self) -> Dict:
        """
        Start the crawling process.
        
        Returns:
            Dict containing crawl results
        """
        # Add the initial URL to the queue
        self.page_queue.put((self.base_url, 0))
        self.found_urls.add(self.base_url)
        
        # Process special files first (robots.txt, sitemap.xml)
        self._process_special_files()
        
        # Use thread pool for concurrent crawling
        with ThreadPoolExecutor(max_workers=self.thread_count) as executor:
            while not self.page_queue.empty() and not self.scanner.stopped and len(self.crawled_pages) < self.max_pages:
                try:
                    # Get the next URL from the queue
                    url, depth = self.page_queue.get(block=False)
                    
                    # Submit the crawl task to the thread pool
                    executor.submit(self.crawl_page, url, depth)
                    
                    # Add a small delay to avoid overwhelming the thread pool
                    time.sleep(0.05)
                    
                except queue.Empty:
                    # Queue is empty, wait for running tasks to complete
                    time.sleep(0.5)
                    
                    # If the queue is still empty after waiting, we're done
                    if self.page_queue.empty():
                        break
                        
                except Exception as e:
                    logger.error(f"Error during crawl: {str(e)}")
        
        # Update the scanner's crawled URLs
        self.scanner.crawled_urls = self.crawled_pages
        
        # Set progress to 25% (crawler phase complete)
        self.scanner.progress = 25
        
        logger.info(f"Crawl completed. Found {len(self.crawled_pages)} pages, {len(self.results['forms'])} forms, and {len(self.results['endpoints'])} endpoints.")
        return self.results
    
    def _process_special_files(self) -> None:
        """Process special files like robots.txt and sitemap.xml."""
        # Process robots.txt
        robots_url = urljoin(self.base_url, '/robots.txt')
        response, error = self.scanner._make_request(url=robots_url, method='GET')
        
        if not error and response and response.status_code == 200:
            logger.info(f"Found robots.txt at {robots_url}")
            
            # Parse robots.txt to find disallowed paths and sitemaps
            try:
                lines = response.text.split('\n')
                for line in lines:
                    line = line.strip()
                    
                    # Extract sitemap URLs
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line[8:].strip()
                        if sitemap_url:
                            logger.info(f"Found sitemap reference: {sitemap_url}")
                            self._process_sitemap(sitemap_url)
                    
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
        self._process_sitemap(sitemap_url)
    
    def _process_sitemap(self, sitemap_url: str) -> None:
        """
        Process a sitemap file to extract URLs.
        
        Args:
            sitemap_url: URL of the sitemap file
        """
        response, error = self.scanner._make_request(url=sitemap_url, method='GET')
        
        if error or not response or response.status_code != 200:
            return
        
        logger.info(f"Processing sitemap: {sitemap_url}")
        
        try:
            # Check if this is a sitemap index with multiple sitemaps
            if '<sitemapindex' in response.text:
                soup = BeautifulSoup(response.text, 'xml')
                for sitemap in soup.find_all('sitemap'):
                    loc = sitemap.find('loc')
                    if loc:
                        child_sitemap_url = loc.text
                        # Process child sitemap
                        self._process_sitemap(child_sitemap_url)
            
            # Parse sitemap for URLs
            elif '<urlset' in response.text:
                soup = BeautifulSoup(response.text, 'xml')
                for url_element in soup.find_all('url'):
                    loc = url_element.find('loc')
                    if loc:
                        url = loc.text
                        # Only process URLs from the same domain
                        if self.is_same_domain(url):
                            # Add URL to queue if not already visited
                            if url not in self.visited_urls and url not in self.found_urls:
                                self.page_queue.put((url, 0))
                                self.found_urls.add(url)
                                logger.debug(f"Added URL from sitemap: {url}")
        
        except Exception as e:
            logger.error(f"Error processing sitemap {sitemap_url}: {str(e)}")

# Import at the end to avoid circular import
from modules.discovery import WebCrawler