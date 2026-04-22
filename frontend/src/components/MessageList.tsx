import { useRef, useEffect } from 'react'
import MessageBubble, { type ChatMessage } from './MessageBubble'
import LoadingDots from './LoadingDots'
import './MessageList.css'

interface Props {
  messages: ChatMessage[]
  isTyping: boolean
}

export default function MessageList({ messages, isTyping }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  return (
    <div className="message-list">
      {messages.map((msg, i) => (
        <MessageBubble key={i} role={msg.role} content={msg.content} />
      ))}
      {isTyping && (
        <div className="msg-row msg-row-left">
          <div className="msg-avatar">AI</div>
          <div className="msg-bubble msg-assistant">
            <LoadingDots />
          </div>
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  )
}
