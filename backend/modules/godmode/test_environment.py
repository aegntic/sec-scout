"""
Real Test Environment - Legitimate Vulnerable Application for Testing
====================================================================

Real vulnerable web application for testing security tools against.
Contains actual vulnerabilities for validation, not simulated responses.
"""

from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os
import subprocess
import logging
from typing import Dict, Any

class RealTestEnvironment:
    """
    Real vulnerable web application for testing security scanning tools
    """
    
    def __init__(self, port: int = 8080):
        self.app = Flask(__name__)
        self.port = port
        self.logger = logging.getLogger(__name__)
        self.setup_database()
        self.setup_routes()
    
    def setup_database(self):
        """Setup SQLite database with test data"""
        
        conn = sqlite3.connect('test_db.sqlite')
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT,
                email TEXT,
                role TEXT
            )
        ''')
        
        # Insert test data
        cursor.execute("DELETE FROM users")  # Clear existing data
        test_users = [
            (1, 'admin', 'admin123', 'admin@test.com', 'admin'),
            (2, 'user', 'password', 'user@test.com', 'user'),
            (3, 'test', 'test123', 'test@test.com', 'user'),
            (4, 'guest', 'guest', 'guest@test.com', 'guest')
        ]
        
        cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?)", test_users)
        conn.commit()
        conn.close()
    
    def setup_routes(self):
        """Setup vulnerable routes for testing"""
        
        @self.app.route('/')
        def index():
            return '''
            <html>
            <head><title>SecureScout Test Environment</title></head>
            <body>
                <h1>SecureScout Test Environment</h1>
                <p>This is a legitimate vulnerable application for testing security tools.</p>
                <ul>
                    <li><a href="/login">Login (SQL Injection vulnerable)</a></li>
                    <li><a href="/search">Search (XSS vulnerable)</a></li>
                    <li><a href="/file">File Access (Path Traversal vulnerable)</a></li>
                    <li><a href="/exec">Command Execution (Command Injection vulnerable)</a></li>
                </ul>
            </body>
            </html>
            '''
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """Intentionally vulnerable login endpoint - SQL Injection"""
            
            if request.method == 'GET':
                return '''
                <html>
                <body>
                    <h2>Login</h2>
                    <form method="POST">
                        Username: <input type="text" name="username"><br><br>
                        Password: <input type="password" name="password"><br><br>
                        <input type="submit" value="Login">
                    </form>
                </body>
                </html>
                '''
            
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            
            # INTENTIONALLY VULNERABLE - SQL Injection
            query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            
            try:
                conn = sqlite3.connect('test_db.sqlite')
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    return f"Login successful! Welcome {result[1]}. Role: {result[4]}"
                else:
                    return "Login failed! Invalid credentials."
                    
            except sqlite3.Error as e:
                # This exposes database errors - another vulnerability
                return f"Database error: {str(e)}"
        
        @self.app.route('/search')
        def search():
            """Intentionally vulnerable search endpoint - XSS"""
            
            query = request.args.get('q', '')
            
            # INTENTIONALLY VULNERABLE - XSS (no output encoding)
            if query:
                return f'''
                <html>
                <body>
                    <h2>Search Results</h2>
                    <p>You searched for: {query}</p>
                    <p>No results found.</p>
                    <a href="/search">Search again</a>
                </body>
                </html>
                '''
            else:
                return '''
                <html>
                <body>
                    <h2>Search</h2>
                    <form method="GET">
                        <input type="text" name="q" placeholder="Enter search term">
                        <input type="submit" value="Search">
                    </form>
                </body>
                </html>
                '''
        
        @self.app.route('/file')
        def file_access():
            """Intentionally vulnerable file access - Path Traversal"""
            
            filename = request.args.get('file', 'default.txt')
            
            # INTENTIONALLY VULNERABLE - Path Traversal
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                return f'''
                <html>
                <body>
                    <h2>File Content</h2>
                    <pre>{content}</pre>
                    <a href="/file?file=default.txt">Back to default</a>
                </body>
                </html>
                '''
            except Exception as e:
                return f"Error reading file: {str(e)}"
        
        @self.app.route('/exec')
        def command_exec():
            """Intentionally vulnerable command execution - Command Injection"""
            
            cmd = request.args.get('cmd', 'echo "Hello World"')
            
            # INTENTIONALLY VULNERABLE - Command Injection
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return f'''
                <html>
                <body>
                    <h2>Command Execution</h2>
                    <p>Command: {cmd}</p>
                    <pre>Output: {result.stdout}</pre>
                    <pre>Error: {result.stderr}</pre>
                    <form method="GET">
                        <input type="text" name="cmd" value="{cmd}">
                        <input type="submit" value="Execute">
                    </form>
                </body>
                </html>
                '''
            except Exception as e:
                return f"Error executing command: {str(e)}"
        
        @self.app.route('/api/users/<int:user_id>')
        def get_user(user_id):
            """API endpoint with SQL injection vulnerability"""
            
            # INTENTIONALLY VULNERABLE - SQL Injection in API
            query = f"SELECT username, email, role FROM users WHERE id = {user_id}"
            
            try:
                conn = sqlite3.connect('test_db.sqlite')
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    return jsonify({
                        'username': result[0],
                        'email': result[1],
                        'role': result[2]
                    })
                else:
                    return jsonify({'error': 'User not found'}), 404
                    
            except sqlite3.Error as e:
                return jsonify({'error': f'Database error: {str(e)}'}), 500
        
        @self.app.route('/health')
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'service': 'SecureScout Test Environment',
                'vulnerabilities': [
                    'SQL Injection in /login',
                    'XSS in /search',
                    'Path Traversal in /file',
                    'Command Injection in /exec',
                    'SQL Injection in /api/users/<id>'
                ]
            })
    
    def create_test_files(self):
        """Create test files for path traversal testing"""
        
        # Create default.txt
        with open('default.txt', 'w') as f:
            f.write('This is the default test file.\nIt contains no sensitive information.')
        
        # Create a fake sensitive file (for testing only)
        os.makedirs('sensitive', exist_ok=True)
        with open('sensitive/config.txt', 'w') as f:
            f.write('# Test Configuration File\ndatabase_host=localhost\napi_key=test_key_12345')
    
    def run(self, debug: bool = False):
        """Run the test environment"""
        
        self.create_test_files()
        self.logger.info(f"Starting SecureScout Test Environment on port {self.port}")
        self.logger.warning("WARNING: This is a vulnerable application for testing only!")
        
        self.app.run(host='127.0.0.1', port=self.port, debug=debug)

def start_test_environment(port: int = 8080):
    """Start the test environment"""
    
    env = RealTestEnvironment(port)
    env.run()

if __name__ == '__main__':
    start_test_environment()

# Export the test environment
__all__ = ['RealTestEnvironment', 'start_test_environment']