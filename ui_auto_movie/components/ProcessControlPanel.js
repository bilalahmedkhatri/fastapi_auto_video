/**
 * Process Control Panel
 * 
 * This component provides controls for managing video generation processes,
 * including pause, resume, cancel, and retry functionality.
 */

import React, { useState } from 'react';
import { 
  Play, 
  Pause, 
  Square, 
  RotateCcw, 
  AlertTriangle,
  CheckCircle,
  Loader2,
  Clock,
  X
} from 'lucide-react';
import { toast } from 'react-hot-toast';

/**
 * Action button component
 */
function ActionButton({ 
  onClick, 
  disabled = false, 
  loading = false, 
  variant = 'primary', 
  icon: Icon, 
  children,
  className = ''
}) {
  const getVariantClasses = () => {
    switch (variant) {
      case 'primary':
        return 'bg-blue-600 hover:bg-blue-700 text-white border-blue-600';
      case 'secondary':
        return 'bg-gray-600 hover:bg-gray-700 text-white border-gray-600';
      case 'danger':
        return 'bg-red-600 hover:bg-red-700 text-white border-red-600';
      case 'warning':
        return 'bg-yellow-600 hover:bg-yellow-700 text-white border-yellow-600';
      case 'success':
        return 'bg-green-600 hover:bg-green-700 text-white border-green-600';
      default:
        return 'bg-blue-600 hover:bg-blue-700 text-white border-blue-600';
    }
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        inline-flex items-center gap-2 px-4 py-2 border rounded-md font-medium text-sm
        transition-colors duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        ${getVariantClasses()}
        ${className}
      `}
    >
      {loading ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : Icon ? (
        <Icon className="h-4 w-4" />
      ) : null}
      {children}
    </button>
  );
}

/**
 * Confirmation dialog component
 */
function ConfirmationDialog({ 
  isOpen, 
  onClose, 
  onConfirm, 
  title, 
  message, 
  confirmText = 'Confirm', 
  cancelText = 'Cancel',
  variant = 'danger'
}) {
  const [reason, setReason] = useState('');
  const [isConfirming, setIsConfirming] = useState(false);

  if (!isOpen) return null;

  const handleConfirm = async () => {
    setIsConfirming(true);
    try {
      await onConfirm(reason);
    } finally {
      setIsConfirming(false);
      setReason('');
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex items-center gap-3 mb-4">
          <AlertTriangle className="h-6 w-6 text-yellow-600" />
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        </div>
        
        <p className="text-gray-600 mb-4">{message}</p>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Reason (optional):
          </label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows="3"
            placeholder="Enter a reason for this action..."
          />
        </div>
        
        <div className="flex gap-3 justify-end">
          <ActionButton
            onClick={onClose}
            variant="secondary"
            disabled={isConfirming}
          >
            {cancelText}
          </ActionButton>
          <ActionButton
            onClick={handleConfirm}
            variant={variant}
            loading={isConfirming}
          >
            {confirmText}
          </ActionButton>
        </div>
      </div>
    </div>
  );
}

/**
 * Process status indicator
 */
function ProcessStatusIndicator({ processState, processError, className = '' }) {
  const getStatusConfig = () => {
    switch (processState) {
      case 'starting':
        return {
          icon: Clock,
          color: 'text-blue-600',
          bg: 'bg-blue-50',
          border: 'border-blue-200',
          text: 'Starting Process...'
        };
      case 'running':
        return {
          icon: Play,
          color: 'text-green-600',
          bg: 'bg-green-50',
          border: 'border-green-200',
          text: 'Process Running'
        };
      case 'paused':
        return {
          icon: Pause,
          color: 'text-yellow-600',
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          text: 'Process Paused'
        };
      case 'completed':
        return {
          icon: CheckCircle,
          color: 'text-green-600',
          bg: 'bg-green-50',
          border: 'border-green-200',
          text: 'Process Completed'
        };
      case 'failed':
        return {
          icon: AlertTriangle,
          color: 'text-red-600',
          bg: 'bg-red-50',
          border: 'border-red-200',
          text: 'Process Failed'
        };
      case 'cancelled':
        return {
          icon: X,
          color: 'text-gray-600',
          bg: 'bg-gray-50',
          border: 'border-gray-200',
          text: 'Process Cancelled'
        };
      default:
        return {
          icon: Clock,
          color: 'text-gray-600',
          bg: 'bg-gray-50',
          border: 'border-gray-200',
          text: 'Process Idle'
        };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  return (
    <div className={`flex items-center gap-3 p-3 rounded-lg border ${config.bg} ${config.border} ${className}`}>
      <Icon className={`h-5 w-5 ${config.color}`} />
      <div className="flex-1">
        <div className={`font-medium ${config.color}`}>
          {config.text}
        </div>
        {processError && (
          <div className="text-sm text-red-600 mt-1">
            Error: {processError.message || processError}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Main process control panel component
 */
function ProcessControlPanel({
  processState = 'idle',
  processId = null,
  canControl,
  onPause,
  onResume,
  onCancel,
  onRetry,
  processError = null,
  isLoading = false,
  className = ''
}) {
  const [showCancelDialog, setShowCancelDialog] = useState(false);
  const [showRetryDialog, setShowRetryDialog] = useState(false);
  const [actionLoading, setActionLoading] = useState(null);

  const handleAction = async (action, handler, reason = '') => {
    if (!handler) return;
    
    setActionLoading(action);
    try {
      await handler(reason);
      toast.success(`Process ${action}d successfully`);
    } catch (error) {
      console.error(`Failed to ${action} process:`, error);
      toast.error(`Failed to ${action} process: ${error.message}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handlePause = () => {
    handleAction('pause', onPause);
  };

  const handleResume = () => {
    handleAction('resume', onResume);
  };

  const handleCancel = (reason) => {
    return handleAction('cancel', onCancel, reason);
  };

  const handleRetry = (reason) => {
    return handleAction('retry', onRetry, reason);
  };

  // Don't show control panel if no process is active
  if (!processId || processState === 'idle') {
    return null;
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm border p-4 ${className}`}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Process Control</h3>
        <ProcessStatusIndicator 
          processState={processState} 
          processError={processError}
        />
      </div>
      
      <div className="flex gap-3 flex-wrap">
        {/* Pause Button */}
        {canControl('pause') && (
          <ActionButton
            onClick={handlePause}
            loading={actionLoading === 'pause'}
            disabled={isLoading}
            variant="warning"
            icon={Pause}
          >
            Pause Process
          </ActionButton>
        )}
        
        {/* Resume Button */}
        {canControl('resume') && (
          <ActionButton
            onClick={handleResume}
            loading={actionLoading === 'resume'}
            disabled={isLoading}
            variant="success"
            icon={Play}
          >
            Resume Process
          </ActionButton>
        )}
        
        {/* Retry Button */}
        {canControl('retry') && (
          <ActionButton
            onClick={() => setShowRetryDialog(true)}
            loading={actionLoading === 'retry'}
            disabled={isLoading}
            variant="primary"
            icon={RotateCcw}
          >
            Retry Process
          </ActionButton>
        )}
        
        {/* Cancel Button */}
        {canControl('cancel') && (
          <ActionButton
            onClick={() => setShowCancelDialog(true)}
            loading={actionLoading === 'cancel'}
            disabled={isLoading}
            variant="danger"
            icon={Square}
          >
            Cancel Process
          </ActionButton>
        )}
      </div>
      
      {/* Process Information */}
      <div className="mt-4 p-3 bg-gray-50 rounded-md">
        <div className="text-sm text-gray-600">
          <div><strong>Process ID:</strong> {processId}</div>
          <div><strong>Status:</strong> {processState}</div>
        </div>
      </div>
      
      {/* Cancel Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={showCancelDialog}
        onClose={() => setShowCancelDialog(false)}
        onConfirm={handleCancel}
        title="Cancel Process"
        message="Are you sure you want to cancel this video generation process? This action cannot be undone."
        confirmText="Cancel Process"
        variant="danger"
      />
      
      {/* Retry Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={showRetryDialog}
        onClose={() => setShowRetryDialog(false)}
        onConfirm={handleRetry}
        title="Retry Process"
        message="Do you want to retry the failed process step? This will restart from the current step."
        confirmText="Retry Process"
        variant="primary"
      />
    </div>
  );
}

/**
 * Compact control panel for smaller spaces
 */
export function CompactControlPanel({
  processState = 'idle',
  processId = null,
  canControl,
  onPause,
  onResume,
  onCancel,
  className = ''
}) {
  const [actionLoading, setActionLoading] = useState(null);

  const handleAction = async (action, handler) => {
    if (!handler) return;
    
    setActionLoading(action);
    try {
      await handler();
      toast.success(`Process ${action}d successfully`);
    } catch (error) {
      console.error(`Failed to ${action} process:`, error);
      toast.error(`Failed to ${action} process: ${error.message}`);
    } finally {
      setActionLoading(null);
    }
  };

  if (!processId || processState === 'idle') {
    return null;
  }

  return (
    <div className={`flex gap-2 ${className}`}>
      {canControl('pause') && (
        <button
          onClick={() => handleAction('pause', onPause)}
          disabled={actionLoading === 'pause'}
          className="p-2 text-yellow-600 hover:bg-yellow-50 rounded-md transition-colors"
          title="Pause Process"
        >
          {actionLoading === 'pause' ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Pause className="h-4 w-4" />
          )}
        </button>
      )}
      
      {canControl('resume') && (
        <button
          onClick={() => handleAction('resume', onResume)}
          disabled={actionLoading === 'resume'}
          className="p-2 text-green-600 hover:bg-green-50 rounded-md transition-colors"
          title="Resume Process"
        >
          {actionLoading === 'resume' ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Play className="h-4 w-4" />
          )}
        </button>
      )}
      
      {canControl('cancel') && (
        <button
          onClick={() => handleAction('cancel', onCancel)}
          disabled={actionLoading === 'cancel'}
          className="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
          title="Cancel Process"
        >
          {actionLoading === 'cancel' ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Square className="h-4 w-4" />
          )}
        </button>
      )}
    </div>
  );
}

export default ProcessControlPanel;