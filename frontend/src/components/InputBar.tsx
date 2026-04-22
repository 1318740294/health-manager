import { useState, useRef } from 'react'
import { Input, Button } from 'antd-mobile'
import './InputBar.css'

interface Props {
  onSend: (text: string) => void
  disabled?: boolean
}

export default function InputBar({ onSend, disabled }: Props) {
  const [text, setText] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  function handleSend() {
    const trimmed = text.trim()
    if (!trimmed) return
    onSend(trimmed)
    setText('')
    inputRef.current?.focus()
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="input-bar">
      <Input
        ref={inputRef}
        className="input-bar-input"
        placeholder="输入健康问题..."
        value={text}
        onChange={setText}
        onKeyDown={handleKeyDown}
        disabled={disabled}
      />
      <Button
        className="input-bar-btn"
        color="primary"
        size="small"
        onClick={handleSend}
        disabled={disabled || !text.trim()}
      >
        发送
      </Button>
    </div>
  )
}
