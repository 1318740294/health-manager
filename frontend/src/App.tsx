import { useState, useRef } from 'react'
import ChatHeader from './components/ChatHeader'
import MessageList from './components/MessageList'
import InputBar from './components/InputBar'
import type { ChatMessage } from './components/MessageBubble'

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const sessionIdRef = useRef(crypto.randomUUID())

  async function handleSend(text: string) {
    const userMsg: ChatMessage = { role: 'user', content: text }
    setMessages(prev => [...prev, userMsg])
    setIsTyping(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionIdRef.current,
          message: text,
        }),
      })

      if (!res.ok || !res.body) {
        setMessages(prev => [...prev, { role: 'system', content: '请求失败，请稍后重试' }])
        setIsTyping(false)
        return
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let aiMsgCreated = false
      let fullText = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        let currentEvent = ''
        for (const line of lines) {
          if (line.startsWith('event: ')) {
            currentEvent = line.slice(7).trim()
          } else if (line.startsWith('data: ')) {
            const dataStr = line.slice(6).trim()
            if (!dataStr || !currentEvent) continue

            try {
              const data = JSON.parse(dataStr)

              if (currentEvent === 'token') {
                fullText += data.content
                console.log("data.content---",data.content)
                if (!aiMsgCreated) {
                  setIsTyping(false)
                  aiMsgCreated = true
                  setMessages(prev => [...prev, { role: 'assistant', content: fullText }])
                } else {
                  setMessages(prev => {
                    const updated = [...prev]
                    const last = updated[updated.length - 1]
                    if (last && last.role === 'assistant') {
                      updated[updated.length - 1] = { ...last, content: fullText }
                    }
                    return updated
                  })
                }
              } else if (currentEvent === 'tool_use') {
                setIsTyping(false)
                setMessages(prev => [...prev, { role: 'system', content: '正在查询你的健康数据...' }])
              } else if (currentEvent === 'tool_result') {
                // handled silently; token events will show final reply
              } else if (currentEvent === 'done') {
                setIsTyping(false)
                if (aiMsgCreated) {
                  setMessages(prev => {
                    const updated = [...prev]
                    const last = updated[updated.length - 1]
                    if (last && last.role === 'assistant') {
                      updated[updated.length - 1] = { ...last, content: data.content }
                    }
                    return updated
                  })
                }
              } else if (currentEvent === 'error') {
                setIsTyping(false)
                setMessages(prev => [...prev, { role: 'system', content: data.message || '发生错误' }])
              }
            } catch {
              // ignore parse errors
            }

            currentEvent = ''
          }
        }
      }
    } catch {
      setIsTyping(false)
      setMessages(prev => [...prev, { role: 'system', content: '网络错误，请检查连接' }])
    }
  }

  return (
    <>
      <ChatHeader />
      <MessageList messages={messages} isTyping={isTyping} />
      <InputBar onSend={handleSend} disabled={isTyping} />
    </>
  )
}

export default App
