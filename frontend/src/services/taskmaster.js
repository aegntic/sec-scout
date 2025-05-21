/**
 * SecureScout Taskmaster Integration
 * 
 * This service provides integration with the Claude Taskmaster MCP for enhanced
 * AI-powered functionality within the SecureScout application.
 */

// Check if taskmaster is available globally
const hasTaskmaster = typeof window !== 'undefined' && window.taskmaster;

/**
 * Taskmaster service for memory and AI-powered features
 */
const taskmasterService = {
  /**
   * Check if taskmaster is available
   * @returns {boolean} True if taskmaster is available
   */
  isAvailable: () => {
    return hasTaskmaster;
  },

  /**
   * Initialize taskmaster with application context
   * @param {Object} config Configuration object with application settings
   * @returns {Promise<boolean>} True if initialization was successful
   */
  initialize: async (config = {}) => {
    if (!hasTaskmaster) {
      console.warn('Taskmaster not available - skipping initialization');
      return false;
    }

    try {
      // Initialize memory context with app information
      await window.taskmaster.memory.set('app_context', {
        name: 'SecureScout',
        version: '1.0.0',
        userRole: config.userRole || 'guest',
        theme: config.theme || 'dark',
        ...config
      });

      // Initialize security scan templates if provided
      if (config.scanTemplates) {
        await window.taskmaster.memory.set('scan_templates', config.scanTemplates);
      }

      console.log('Taskmaster initialized successfully');
      return true;
    } catch (error) {
      console.error('Failed to initialize taskmaster:', error);
      return false;
    }
  },

  /**
   * Store security scan results in memory
   * @param {string} scanId Unique scan identifier
   * @param {Object} scanResults Scan results object
   * @returns {Promise<boolean>} True if storing was successful
   */
  storeScanResults: async (scanId, scanResults) => {
    if (!hasTaskmaster) return false;

    try {
      // Store the scan results
      await window.taskmaster.memory.set(`scan_results_${scanId}`, scanResults);

      // Also update the list of recent scans
      const recentScans = await window.taskmaster.memory.get('recent_scans') || [];
      
      // Add this scan to the list if not already present
      if (!recentScans.find(scan => scan.id === scanId)) {
        recentScans.unshift({
          id: scanId,
          target: scanResults.target_url,
          timestamp: new Date().toISOString(),
          vulnerabilityCount: scanResults.findings?.length || 0
        });
        
        // Keep only last 10 scans
        if (recentScans.length > 10) {
          recentScans.pop();
        }
        
        await window.taskmaster.memory.set('recent_scans', recentScans);
      }
      
      return true;
    } catch (error) {
      console.error('Failed to store scan results:', error);
      return false;
    }
  },

  /**
   * Get security scan results from memory
   * @param {string} scanId Unique scan identifier
   * @returns {Promise<Object|null>} Scan results or null if not found
   */
  getScanResults: async (scanId) => {
    if (!hasTaskmaster) return null;

    try {
      return await window.taskmaster.memory.get(`scan_results_${scanId}`);
    } catch (error) {
      console.error('Failed to get scan results:', error);
      return null;
    }
  },

  /**
   * Get recent scan history
   * @returns {Promise<Array>} Array of recent scans
   */
  getRecentScans: async () => {
    if (!hasTaskmaster) return [];

    try {
      return await window.taskmaster.memory.get('recent_scans') || [];
    } catch (error) {
      console.error('Failed to get recent scans:', error);
      return [];
    }
  },

  /**
   * Store user preferences in memory
   * @param {string} userId User identifier
   * @param {Object} preferences User preferences object
   * @returns {Promise<boolean>} True if storing was successful
   */
  storeUserPreferences: async (userId, preferences) => {
    if (!hasTaskmaster) return false;

    try {
      await window.taskmaster.memory.set(`user_preferences_${userId}`, preferences);
      return true;
    } catch (error) {
      console.error('Failed to store user preferences:', error);
      return false;
    }
  },

  /**
   * Get user preferences from memory
   * @param {string} userId User identifier
   * @returns {Promise<Object|null>} User preferences or null if not found
   */
  getUserPreferences: async (userId) => {
    if (!hasTaskmaster) return null;

    try {
      return await window.taskmaster.memory.get(`user_preferences_${userId}`);
    } catch (error) {
      console.error('Failed to get user preferences:', error);
      return null;
    }
  },

  /**
   * Create a task with taskmaster
   * @param {Object} task Task object with details
   * @returns {Promise<string|null>} Task ID or null if failed
   */
  createTask: async (task) => {
    if (!hasTaskmaster) return null;

    try {
      const taskId = await window.taskmaster.tasks.create({
        title: task.title,
        description: task.description,
        status: task.status || 'pending',
        priority: task.priority || 'medium',
        dueDate: task.dueDate,
        assignee: task.assignee
      });
      
      return taskId;
    } catch (error) {
      console.error('Failed to create task:', error);
      return null;
    }
  },

  /**
   * Get tasks for a user
   * @param {string} userId User identifier
   * @returns {Promise<Array>} Array of tasks
   */
  getUserTasks: async (userId) => {
    if (!hasTaskmaster) return [];

    try {
      return await window.taskmaster.tasks.getByAssignee(userId);
    } catch (error) {
      console.error('Failed to get user tasks:', error);
      return [];
    }
  },

  /**
   * Update a task
   * @param {string} taskId Task identifier
   * @param {Object} updates Task updates
   * @returns {Promise<boolean>} True if update was successful
   */
  updateTask: async (taskId, updates) => {
    if (!hasTaskmaster) return false;

    try {
      await window.taskmaster.tasks.update(taskId, updates);
      return true;
    } catch (error) {
      console.error('Failed to update task:', error);
      return false;
    }
  },

  /**
   * Generate a vulnerability report using AI
   * @param {Object} scanResults Scan results to analyze
   * @returns {Promise<Object|null>} AI-generated report or null if failed
   */
  generateVulnerabilityReport: async (scanResults) => {
    if (!hasTaskmaster) return null;

    try {
      // Use the AI to analyze the scan results
      const report = await window.taskmaster.ai.analyze({
        type: 'vulnerability_report',
        data: scanResults,
        options: {
          includeRemediation: true,
          riskAssessment: true,
          complianceImpact: true
        }
      });
      
      return report;
    } catch (error) {
      console.error('Failed to generate vulnerability report:', error);
      return null;
    }
  },

  /**
   * Subscribe to taskmaster notifications
   * @param {Function} callback Callback function to handle notifications
   * @returns {Function} Unsubscribe function
   */
  subscribeToNotifications: (callback) => {
    if (!hasTaskmaster) return () => {};

    try {
      const unsubscribe = window.taskmaster.notifications.subscribe(callback);
      return unsubscribe;
    } catch (error) {
      console.error('Failed to subscribe to notifications:', error);
      return () => {};
    }
  }
};

export default taskmasterService;