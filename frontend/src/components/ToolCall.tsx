import React from 'react';
import { cn } from '@/lib/utils';

interface ToolCallProps {
  tool: string;
  args: Record<string, any>;
  result?: any;
  status: 'pending' | 'success' | 'error';
}

const toolColors = {
  search_policies: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
  get_latest_scan: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400',
  create_ticket: 'bg-green-500/10 border-green-500/30 text-green-400',
};

const toolIcons = {
  search_policies: '📚',
  get_latest_scan: '🔍',
  create_ticket: '🎫',
};

const toolNames = {
  search_policies: 'Search Security Policies',
  get_latest_scan: 'Get Latest Scan',
  create_ticket: 'Create Ticket',
};

export const ToolCall: React.FC<ToolCallProps> = ({ tool, args, result, status }) => {
  const [expanded, setExpanded] = React.useState(false);
  
  const colorClass = toolColors[tool as keyof typeof toolColors] || 'bg-gray-500/10 border-gray-500/30 text-gray-400';
  const icon = toolIcons[tool as keyof typeof toolIcons] || '🔧';
  const displayName = toolNames[tool as keyof typeof toolNames] || tool;

  return (
    <div className={cn(
      "border rounded-lg p-3 mb-2 animate-fade-in",
      colorClass
    )}>
      <div 
        className="flex items-start justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start gap-2 flex-1">
          <span className="text-xl">{icon}</span>
          <div className="flex-1">
            <div className="font-medium text-sm">{displayName}</div>
            <div className="text-xs opacity-70 mt-1">
              {Object.keys(args).map(key => (
                <span key={key} className="mr-2">
                  <span className="font-semibold">{key}:</span> {
                    typeof args[key] === 'string' && args[key].length > 50
                      ? args[key].substring(0, 50) + '...'
                      : JSON.stringify(args[key])
                  }
                </span>
              ))}
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {status === 'pending' && (
            <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
          )}
          {status === 'success' && (
            <div className="text-green-400">✓</div>
          )}
          {status === 'error' && (
            <div className="text-red-400">✗</div>
          )}
          <div className="text-xs opacity-50">
            {expanded ? '▼' : '▶'}
          </div>
        </div>
      </div>

      {expanded && result && (
        <div className="mt-3 pt-3 border-t border-current/20">
          <div className="text-xs font-semibold mb-2">Result:</div>
          <pre className="text-xs bg-black/20 p-2 rounded overflow-x-auto max-h-48 overflow-y-auto">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};
