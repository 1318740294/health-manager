import './MessageBubble.css'

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system' | 'tool'
  content: string
  /** tool 名称，role 为 tool 时使用 */
  toolName?: string
  /** tool 执行状态 */
  toolStatus?: 'calling' | 'done'
}

export default function MessageBubble({ role, content, toolName, toolStatus }: ChatMessage) {
  if (role === 'system') {
    return <div className="msg-system">{content}</div>
  }

  if (role === 'tool') {
    console.log('toolName---',toolName);
    
    const name = toolName || 'unknown'
    return (
      <div className="msg-tool">
        {toolStatus === 'calling' ? (
          <span className="msg-tool-calling">
            <span className="msg-tool-spinner" />
            {name}
          </span>
        ) : (
          <span className="msg-tool-done">
            {name} ✓
          </span>
        )}
      </div>
    )
  }

  return (
    <div className={`msg-row ${role === 'user' ? 'msg-row-right' : 'msg-row-left'}`}>
      {role === 'assistant' && <div className="msg-avatar">AI</div>}
      <div className={`msg-bubble ${role === 'user' ? 'msg-user' : 'msg-assistant'}`}>
        {content}
      </div>
    </div>
  )
}
