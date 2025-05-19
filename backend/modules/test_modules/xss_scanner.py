#!/usr/bin/env python3
# SecureScout - Cross-Site Scripting (XSS) Test Module

import logging
import re
import random
import string
import html
from typing import Dict, List, Any, Tuple, Set, Optional
from urllib.parse import parse_qs, urlparse, urlencode, urlunparse
from .base_module import BaseTestModule

logger = logging.getLogger("securescout.xss")

class XSSScanner(BaseTestModule):
    """
    Cross-Site Scripting (XSS) testing module.
    Tests for reflected, stored, and DOM-based XSS vulnerabilities.
    """
    
    def __init__(self, scanner):
        """Initialize the XSS test module."""
        super().__init__(scanner)
        self.name = "XSSScanner"
        self.description = "Tests for Cross-Site Scripting (XSS) vulnerabilities"
        self.category = "xss"
        
        # Generate unique identifiers for better tracking of payloads
        self.xss_token = self.generate_xss_token()
        
        # Payloads for detecting XSS vulnerabilities
        self.test_payloads = {
            # Basic XSS payloads
            "basic": [
                f"<script>console.log('{self.xss_token}')</script>",
                f"<img src=\"x\" onerror=\"console.log('{self.xss_token}')\">",
                f"<div onmouseover=\"console.log('{self.xss_token}')\">Test</div>",
                f"<svg onload=\"console.log('{self.xss_token}')\">",
                f"<body onload=\"console.log('{self.xss_token}')\">",
                f"<iframe onload=\"console.log('{self.xss_token}')\"></iframe>",
                f"javascript:console.log('{self.xss_token}')",
                f"<a href=\"javascript:console.log('{self.xss_token}')\">Click me</a>"
            ],
            
            # Payloads with common evasion techniques
            "evasion": [
                f"<img src=x onerror=console.log('{self.xss_token}')>",
                f"<script>console.log(String.fromCharCode(88,83,83,32,84,101,115,116,101,100))</script>",
                f"<scr<script>ipt>console.log('{self.xss_token}')</scr</script>ipt>",
                f"<scr\x00ipt>console.log('{self.xss_token}')</scr\x00ipt>",
                f"<SCRIPT>console.log('{self.xss_token}')</SCRIPT>",
                f"<IMG SRC=javascript:console.log('{self.xss_token}')>",
                f"<IMG SRC=\"jav&#x09;ascript:console.log('{self.xss_token}')\">",
                f"<IMG SRC=\"jav&#x0A;ascript:console.log('{self.xss_token}')\">",
                f"<IMG SRC=\"jav&#x0D;ascript:console.log('{self.xss_token}')\">",
                f"<IMG SRC=\" &#14;  javascript:console.log('{self.xss_token}')\">",
                f"<img src=`x` onerror=console.log('{self.xss_token}')>",
                f"<img src=1 onerror=console.log(`{self.xss_token}`)>"
            ],
            
            # DOM-based XSS payloads
            "dom": [
                f"#<script>console.log('{self.xss_token}')</script>",
                f"#<img src=x onerror=console.log('{self.xss_token}')>",
                f"#javascript:console.log('{self.xss_token}')",
                f"#'-console.log('{self.xss_token}')-'",
                f"#'-alert('{self.xss_token}')-'"
            ],
            
            # Payloads targeting common frameworks and templating engines
            "framework": [
                f"{{{{ console.log('{self.xss_token}') }}}}",  # Template injection (e.g., Angular, Handlebars)
                f"${{console.log('{self.xss_token}')}}",  # Template injection (e.g., JSP, JSF)
                f"<%= console.log('{self.xss_token}') %>",  # Template injection (e.g., ERB, EJS)
                f"#{{console.log('{self.xss_token}')}}",  # Template injection (e.g., Ruby)
                f"${{{console.log('{self.xss_token}')}}}",  # Template injection (e.g., React)
                f"<div data-bind=\"html: console.log('{self.xss_token}')\"></div>"  # Knockout.js
            ]
        }
        
        # XSS detection patterns for reflecting our payloads
        self.detection_patterns = [
            f"console\\.log\\(['\\\"]?{self.xss_token}['\\\"]?\\)",
            f"<img[^>]*?onerror=[^>]*?{self.xss_token}[^>]*?>",
            f"<svg[^>]*?onload=[^>]*?{self.xss_token}[^>]*?>",
            f"<div[^>]*?onmouseover=[^>]*?{self.xss_token}[^>]*?>",
            f"<body[^>]*?onload=[^>]*?{self.xss_token}[^>]*?>",
            f"<iframe[^>]*?onload=[^>]*?{self.xss_token}[^>]*?>",
            f"<script[^>]*?>{self.xss_token}",
            f"javascript:[^>]*?{self.xss_token}",
            f"{self.xss_token}"  # For simple reflection
        ]
        
        # Compile the detection patterns
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.detection_patterns]
    
    def generate_xss_token(self, length: int = 8) -> str:
        """Generate a random token for XSS testing."""
        return 'XSS_' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    
    def run(self) -> List[Dict[str, Any]]:
        """
        Run XSS tests against the target.
        
        Returns:
            List of findings dictionaries
        """
        logger.info("Starting Cross-Site Scripting (XSS) tests")
        
        self.findings = []
        tested_urls = set()
        
        # Get form inputs discovered during crawling
        forms = self.get_forms_from_crawler()
        
        # Get GET parameters from URLs
        urls_with_params = self.get_urls_with_parameters()
        
        # Test GET parameters for reflected XSS
        for url in urls_with_params:
            if url not in tested_urls:
                self.test_get_parameters(url)
                tested_urls.add(url)
        
        # Test forms for reflected XSS
        for form in forms:
            self.test_form(form)
        
        # Test URLs for DOM-based XSS
        self.test_dom_based_xss(self.scanner.crawled_urls)
        
        logger.info(f"XSS tests completed with {len(self.findings)} findings")
        return self.findings
    
    def get_forms_from_crawler(self) -> List[Dict[str, Any]]:
        """Get forms from crawler results."""
        if hasattr(self.scanner, 'crawler') and hasattr(self.scanner.crawler, 'results'):
            return self.scanner.crawler.results.get('forms', [])
        return []
    
    def get_urls_with_parameters(self) -> List[str]:
        """Extract URLs with query parameters from crawler results."""
        urls = []
        if hasattr(self.scanner, 'crawled_urls'):
            for url in self.scanner.crawled_urls:
                parsed = urlparse(url)
                if parsed.query:
                    urls.append(url)
        return urls
    
    def test_get_parameters(self, url: str) -> None:
        """
        Test GET parameters in a URL for reflected XSS vulnerabilities.
        
        Args:
            url: URL with query parameters to test
        """
        logger.debug(f"Testing GET parameters in {url} for XSS")
        
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Skip if no parameters
        if not query_params:
            return
            
        # Test each parameter
        for param, values in query_params.items():
            original_value = values[0] if values else ""
            
            # Test all XSS payload categories
            for category, payloads in self.test_payloads.items():
                # Skip DOM-based tests for parameter testing
                if category == "dom":
                    continue
                    
                for payload in payloads:
                    # URL-encode the payload
                    encoded_payload = payload
                    
                    # Replace the parameter with our payload
                    modified_params = query_params.copy()
                    modified_params[param] = [encoded_payload]
                    new_query = urlencode(modified_params, doseq=True)
                    
                    # Rebuild the URL with the modified query
                    test_url_parts = list(parsed_url)
                    test_url_parts[4] = new_query  # index 4 is the query part
                    test_url = urlunparse(test_url_parts)
                    
                    # Send the request
                    response, error = self.scanner._make_request(test_url, method='GET')
                    
                    if error or not response:
                        continue
                    
                    # Check if the payload is reflected in the response
                    if self.check_for_xss_reflection(response.text, payload):
                        self.report_xss_finding(url, param, payload, "reflected", response)
                        # Skip further tests for this parameter once a vulnerability is found
                        break
    
    def test_form(self, form: Dict[str, Any]) -> None:
        """
        Test a form for reflected XSS vulnerabilities.
        
        Args:
            form: Dictionary containing form details
        """
        form_url = form.get('action', '')
        form_method = form.get('method', 'GET').upper()
        inputs = form.get('inputs', [])
        
        # Skip if no action URL or no inputs
        if not form_url or not inputs:
            return
            
        logger.debug(f"Testing form at {form_url} with method {form_method} for XSS")
        
        # Prepare form data with default values
        form_data = {}
        
        for input_field in inputs:
            input_type = input_field.get('type', '')
            input_name = input_field.get('name', '')
            
            # Skip if no name
            if not input_name:
                continue
                
            # Skip file inputs, checkboxes, and radio buttons
            if input_type in ['file', 'checkbox', 'radio', 'submit', 'button', 'image', 'reset']:
                continue
                
            # Use provided value or a default
            if input_type == 'password':
                form_data[input_name] = 'testpassword123'
            elif input_type == 'email':
                form_data[input_name] = 'test@example.com'
            elif input_type == 'number':
                form_data[input_name] = '1'
            else:
                form_data[input_name] = 'testvalue'
        
        # Skip if no valid inputs to test
        if not form_data:
            return
        
        # Test each input field
        for input_name in form_data.keys():
            # Test each payload category
            for category, payloads in self.test_payloads.items():
                # Skip DOM-based tests for form testing
                if category == "dom":
                    continue
                    
                for payload in payloads:
                    # Prepare modified form data
                    test_data = form_data.copy()
                    test_data[input_name] = payload
                    
                    # Send request based on form method
                    if form_method == 'POST':
                        response, error = self.scanner._make_request(form_url, method='POST', data=test_data)
                    else:
                        params = urlencode(test_data)
                        url = f"{form_url}?{params}" if '?' not in form_url else f"{form_url}&{params}"
                        response, error = self.scanner._make_request(url, method='GET')
                    
                    if error or not response:
                        continue
                    
                    # Check if the payload is reflected in the response
                    if self.check_for_xss_reflection(response.text, payload):
                        self.report_xss_finding(form_url, input_name, payload, f"reflected ({form_method})", response)
                        # Skip further tests for this input once a vulnerability is found
                        break
    
    def test_dom_based_xss(self, urls: Set[str]) -> None:
        """
        Test for DOM-based XSS vulnerabilities.
        
        Args:
            urls: Set of URLs to test
        """
        # For DOM-based XSS, we'll test fragment identifiers
        # and look for JavaScript code that might use them insecurely
        
        # Filter to HTML pages
        html_urls = [url for url in urls if not url.endswith(('.css', '.js', '.jpg', '.png', '.gif', '.pdf'))]
        
        for url in html_urls:
            # First get the page content to analyze for potential DOM XSS vectors
            response, error = self.scanner._make_request(url, method='GET')
            
            if error or not response:
                continue
            
            # Look for potential DOM XSS sinks
            content = response.text
            
            # Check for common DOM XSS sinks
            dom_sinks = [
                "document.write",
                "document.writeln",
                "innerHTML",
                "outerHTML",
                "insertAdjacentHTML",
                "location",
                "location.href",
                "location.hash",
                "location.search",
                "eval(",
                "setTimeout(",
                "setInterval(",
                "document.URL",
                "document.documentURI",
                "Function(",
                "jQuery("
            ]
            
            dom_sources = [
                "location",
                "location.href",
                "location.hash",
                "location.search",
                "document.URL",
                "document.documentURI",
                "document.referrer",
                "window.name",
                "postMessage"
            ]
            
            # Check if page uses DOM sources
            using_dom_sources = any(source in content for source in dom_sources)
            
            # If the page doesn't use any DOM sources, skip DOM XSS testing
            if not using_dom_sources:
                continue
            
            # Test DOM XSS payloads
            for payload in self.test_payloads["dom"]:
                # Construct test URL with fragment identifier
                test_url = f"{url}{payload}"
                
                # Send the request
                response, error = self.scanner._make_request(test_url, method='GET')
                
                if error or not response:
                    continue
                
                # For DOM XSS, we need to check if the payload appears in JS-accessible content
                # This is challenging without browser execution, but we'll check for unsanitized reflection
                if self.check_for_xss_reflection(response.text, payload[1:]):  # Remove the leading # from the payload
                    self.report_xss_finding(url, "URL fragment", payload, "dom-based", response)
                    break
    
    def check_for_xss_reflection(self, content: str, payload: str) -> bool:
        """
        Check if an XSS payload is reflected in the response.
        
        Args:
            content: Response content to check
            payload: XSS payload to look for
            
        Returns:
            bool: True if the payload is reflected and potentially executable, False otherwise
        """
        if not content:
            return False
        
        # Convert the payload to its unencoded form for comparison
        unencoded_payload = html.unescape(payload)
        
        # Check if the payload appears in the content
        for pattern in self.compiled_patterns:
            if pattern.search(content):
                return True
        
        # Also check for direct reflection of the payload
        if payload in content or unencoded_payload in content:
            # Ensure it's not properly escaped/encoded
            escaped_payload = html.escape(payload)
            if escaped_payload != payload and escaped_payload in content:
                # The payload was properly escaped
                return False
            
            # Check if the payload is inside a context where it might be executed
            js_contexts = [
                "<script", 
                "javascript:", 
                " on", 
                "="
            ]
            
            for js_context in js_contexts:
                if js_context in content.lower():
                    return True
            
            # If we have the exact payload but can't confirm it's in an executable context,
            # we'll report it as a potential issue with lower severity
            return True
        
        return False
    
    def report_xss_finding(self, url: str, param: str, payload: str, 
                          xss_type: str, response) -> None:
        """
        Report a Cross-Site Scripting (XSS) finding.
        
        Args:
            url: URL where the vulnerability was found
            param: Parameter name that is vulnerable
            payload: XSS payload that worked
            xss_type: Type of XSS (reflected, stored, dom-based)
            response: HTTP response object
        """
        title = f"Cross-Site Scripting ({xss_type}) in {param}"
        
        description = f"""A Cross-Site Scripting ({xss_type}) vulnerability was detected in the '{param}' parameter.
        This vulnerability allows attackers to inject malicious client-side scripts into web pages viewed by other users,
        potentially leading to session hijacking, credential theft, or other client-side attacks.
        
        Payload: {payload}
        """
        
        evidence = f"URL: {url}\nParameter: {param}\nPayload: {payload}\nResponse Status: {response.status_code}"
        
        if response.text and len(response.text) < 1000:
            evidence += f"\nResponse excerpt: {response.text[:1000]}"
        
        remediation = """
        To fix Cross-Site Scripting vulnerabilities:
        
        1. Validate input on the server-side
        2. Use context-appropriate output encoding (HTML, JavaScript, CSS, URL encoding)
        3. Implement Content Security Policy (CSP)
        4. Use framework-provided XSS protection features
        5. Apply the principle of least privilege for JavaScript code
        6. Consider using Auto-Escaping template systems
        7. Use HttpOnly and Secure flags for sensitive cookies
        """
        
        references = [
            "https://owasp.org/www-community/attacks/xss/",
            "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html",
            "https://portswigger.net/web-security/cross-site-scripting"
        ]
        
        severity = "high" if xss_type in ["dom-based", "stored"] else "medium"
        
        self.add_finding(
            title=title,
            description=description,
            severity=severity,
            location=url,
            evidence=evidence,
            remediation=remediation,
            references=references,
            cwe_id="CWE-79",
            cvss_score=6.1
        )