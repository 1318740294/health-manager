import './MessageBubble.css'

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export default function MessageBubble({ role, content }: ChatMessage) {
  if (role === 'system') {
    return <div className="msg-system">{content}</div>
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
