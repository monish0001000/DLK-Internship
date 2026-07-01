export const ROLES = {
  ADMINISTRATOR: 'Administrator',
  SOC_ANALYST: 'SOC Analyst',
  THREAT_HUNTER: 'Threat Hunter',
  READ_ONLY: 'Read Only'
};

export const PERMISSIONS = {
  // Global
  VIEW_DASHBOARD: 'view:dashboard',
  VIEW_SETTINGS: 'view:settings',
  EDIT_SETTINGS: 'edit:settings',

  // Endpoints
  VIEW_ENDPOINTS: 'view:endpoints',
  ISOLATE_ENDPOINT: 'action:isolate_endpoint',
  KILL_PROCESS: 'action:kill_process',

  // Alerts & Investigations
  VIEW_ALERTS: 'view:alerts',
  INVESTIGATE_ALERT: 'action:investigate_alert',
  VIEW_INVESTIGATIONS: 'view:investigations',
  MANAGE_INVESTIGATIONS: 'manage:investigations',

  // Cases
  VIEW_CASES: 'view:cases',
  CREATE_CASE: 'create:case',
  EDIT_CASE: 'edit:case',

  // Threat Hunting
  VIEW_HUNTING: 'view:hunting',
  RUN_HUNT: 'action:run_hunt',
  SAVE_HUNT: 'action:save_hunt',

  // Rules
  VIEW_RULES: 'view:rules',
  CREATE_RULE: 'create:rule',
  EDIT_RULE: 'edit:rule',
  DELETE_RULE: 'delete:rule',

  // Simulations
  VIEW_SIMULATIONS: 'view:simulations',
  RUN_SIMULATION: 'action:run_simulation',

  // Audit & Health
  VIEW_AUDIT: 'view:audit',
  VIEW_HEALTH: 'view:health',
};

// Role to Permission mapping
export const ROLE_PERMISSIONS = {
  [ROLES.ADMINISTRATOR]: Object.values(PERMISSIONS), // Admin gets all permissions
  
  [ROLES.SOC_ANALYST]: [
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.VIEW_ENDPOINTS,
    PERMISSIONS.VIEW_ALERTS,
    PERMISSIONS.INVESTIGATE_ALERT,
    PERMISSIONS.VIEW_INVESTIGATIONS,
    PERMISSIONS.MANAGE_INVESTIGATIONS,
    PERMISSIONS.VIEW_CASES,
    PERMISSIONS.CREATE_CASE,
    PERMISSIONS.EDIT_CASE,
    PERMISSIONS.VIEW_RULES,
    PERMISSIONS.VIEW_SIMULATIONS,
    PERMISSIONS.RUN_SIMULATION,
    PERMISSIONS.VIEW_AUDIT,
  ],

  [ROLES.THREAT_HUNTER]: [
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.VIEW_ENDPOINTS,
    PERMISSIONS.VIEW_ALERTS,
    PERMISSIONS.VIEW_HUNTING,
    PERMISSIONS.RUN_HUNT,
    PERMISSIONS.SAVE_HUNT,
  ],

  [ROLES.READ_ONLY]: [
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.VIEW_ENDPOINTS,
    PERMISSIONS.VIEW_ALERTS,
    PERMISSIONS.VIEW_INVESTIGATIONS,
    PERMISSIONS.VIEW_CASES,
    PERMISSIONS.VIEW_HUNTING,
    PERMISSIONS.VIEW_RULES,
  ],
};

/**
 * Checks if a specific role has a required permission.
 * @param {string} role - The user's role
 * @param {string} permission - The permission to check
 * @returns {boolean}
 */
export const hasPermission = (role, permission) => {
  if (!role || !permission) return false;
  const permissions = ROLE_PERMISSIONS[role];
  if (!permissions) return false;
  return permissions.includes(permission);
};

/**
 * Checks if a specific role has ALL of the required permissions.
 * @param {string} role - The user's role
 * @param {string[]} permissions - The permissions to check
 * @returns {boolean}
 */
export const hasAllPermissions = (role, permissions) => {
  if (!role || !permissions || permissions.length === 0) return false;
  return permissions.every(p => hasPermission(role, p));
};

/**
 * Checks if a specific role has ANY of the required permissions.
 * @param {string} role - The user's role
 * @param {string[]} permissions - The permissions to check
 * @returns {boolean}
 */
export const hasAnyPermission = (role, permissions) => {
  if (!role || !permissions || permissions.length === 0) return false;
  return permissions.some(p => hasPermission(role, p));
};
