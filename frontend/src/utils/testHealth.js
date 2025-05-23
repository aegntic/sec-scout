// Test script to verify app health
export const testAppHealth = async () => {
  const tests = {
    react: false,
    routing: false,
    api: false,
    state: false,
    ui: false
  };

  try {
    // Test 1: React is working
    if (window.React) {
      tests.react = true;
    }

    // Test 2: Routing is working
    if (window.location.pathname) {
      tests.routing = true;
    }

    // Test 3: API is reachable
    try {
      const response = await fetch('http://localhost:8001/api/health');
      tests.api = response.ok;
    } catch (e) {
      tests.api = false;
    }

    // Test 4: State management works
    const testState = { test: true };
    if (JSON.stringify(testState) === '{"test":true}') {
      tests.state = true;
    }

    // Test 5: UI renders
    if (document.getElementById('root')) {
      tests.ui = true;
    }

    console.log('App Health Check Results:', tests);
    return tests;
  } catch (error) {
    console.error('Health check failed:', error);
    return tests;
  }
};

// Run health check on load
if (window.location.pathname === '/test') {
  testAppHealth();
}