import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { hasPermission, hasAllPermissions, hasAnyPermission } from '../../utils/permissions';

/**
 * Wrapper component to conditionally render UI elements based on permissions.
 * 
 * @param {Object} props
 * @param {string} props.requiredPermission - A single permission string required to render children
 * @param {string[]} props.requireAll - Array of permissions; user must have ALL of them
 * @param {string[]} props.requireAny - Array of permissions; user must have AT LEAST ONE
 * @param {React.ReactNode} props.fallback - Fallback UI if permission is denied (default: null)
 * @param {React.ReactNode} props.children - UI to render if permission is granted
 */
const HasPermission = ({ 
  requiredPermission, 
  requireAll, 
  requireAny, 
  fallback = null, 
  children 
}) => {
  const { user, loading } = useAuth();

  if (loading || !user) {
    return fallback;
  }

  const role = user.role;
  let isAllowed = true;

  if (requiredPermission) {
    isAllowed = isAllowed && hasPermission(role, requiredPermission);
  }

  if (requireAll && requireAll.length > 0) {
    isAllowed = isAllowed && hasAllPermissions(role, requireAll);
  }

  if (requireAny && requireAny.length > 0) {
    isAllowed = isAllowed && hasAnyPermission(role, requireAny);
  }

  if (!isAllowed) {
    return fallback;
  }

  return <>{children}</>;
};

export default HasPermission;
