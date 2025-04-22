import React, { useState, useEffect } from 'react'
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Avatar,
  TextField,
  IconButton
} from '@mui/material'
import SendIcon from '@mui/icons-material/Send'
import { keyframes } from '@emotion/react'

type Message = {
  sender: 'bot' | 'user'
  text: string
}

const SERVER_API = 'http://localhost:5000'

export const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { sender: 'bot', text: 'Hello! How may I assist you?' }
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)

  // load history from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem('chatMessages')
    if (stored) setMessages(JSON.parse(stored))
  }, [])

  // persist on every update
  useEffect(() => {
    localStorage.setItem('chatMessages', JSON.stringify(messages))
  }, [messages])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text) return

    setIsTyping(true)

    const userMsg: Message = { sender: 'user', text }
    setMessages((m) => [...m, userMsg])
    setInput('')

    try {
      const res = await fetch(`${SERVER_API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      })
      const { reply } = await res.json()
      const botMsg: Message = { sender: 'bot', text: reply }
      setMessages((m) => [...m, botMsg])
    } catch (err) {
      console.error(err)
    } finally {
      setIsTyping(false)
    }
  }

  const blink = keyframes`
    0%, 80%, 100% { opacity: 0; }
    40% { opacity: 1; }
  `

  return (
    <Box
      width='100%'
      maxWidth='428px'
      height='100vh'
      margin='0 auto'
      display='flex'
      flexDirection='column'
      bgcolor='background.default'
      border='1px solid'
      borderColor='divider'
    >
      <AppBar
        position='static'
        elevation={0}
        sx={{
          bgcolor: 'background.default',
          borderBottom: 1,
          borderColor: 'background.default'
        }}
      >
        <Toolbar variant='dense'>
          <Typography variant='h6' color='text.primary'>
            Scout Chatbot
          </Typography>
        </Toolbar>
      </AppBar>

      <Box
        flexGrow={1}
        p={2}
        overflow='auto'
        sx={{ background: 'background.default' }}
      >
        {messages.map((m, i) =>
          m.sender === 'bot' ? (
            <Box key={i} display='flex' alignItems='center' mb={2}>
              <Avatar
                src='/robot.png'
                alt='bot'
                sx={{ width: 32, height: 32 }}
              />
              <Box ml={1} maxWidth='75%'>
                <Box
                  p={1}
                  borderRadius={2}
                  sx={{
                    bgcolor: 'background.paper',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.2)'
                  }}
                >
                  <Typography variant='body2' color='text.primary'>
                    {m.text}
                  </Typography>
                </Box>
              </Box>
            </Box>
          ) : (
            <Box
              key={i}
              display='flex'
              justifyContent='flex-end'
              alignItems='center'
              mb={2}
            >
              <Box mr={2} maxWidth='75%'>
                <Box p={1} borderRadius={2} sx={{ bgcolor: 'primary.main' }}>
                  <Typography variant='body2' color='#FFFFFF'>
                    {m.text}
                  </Typography>
                </Box>
              </Box>
              <Avatar
                sx={{
                  bgcolor: 'primary.main',
                  width: 32,
                  height: 32,
                  fontSize: '0.875rem'
                }}
              >
                A
              </Avatar>
            </Box>
          )
        )}

        {isTyping && (
          <Box display='flex' alignItems='center' mb={2}>
            <Avatar src='/robot.png' alt='bot' sx={{ width: 32, height: 32 }} />
            <Box ml={2}>
              <Box
                p={1}
                borderRadius={2}
                sx={{
                  bgcolor: 'background.paper',
                  display: 'flex',
                  alignItems: 'center'
                }}
              >
                <Box
                  component='span'
                  sx={{
                    width: 6,
                    height: 6,
                    borderRadius: '50%',
                    bgcolor: 'text.secondary',
                    mr: 0.5,
                    animation: `${blink} 1.4s infinite`
                  }}
                />
                <Box
                  component='span'
                  sx={{
                    width: 6,
                    height: 6,
                    borderRadius: '50%',
                    bgcolor: 'text.secondary',
                    mr: 0.5,
                    animation: `${blink} 1.4s infinite`,
                    animationDelay: '0.2s'
                  }}
                />
                <Box
                  component='span'
                  sx={{
                    width: 6,
                    height: 6,
                    borderRadius: '50%',
                    bgcolor: 'text.secondary',
                    animation: `${blink} 1.4s infinite`,
                    animationDelay: '0.4s'
                  }}
                />
              </Box>
            </Box>
          </Box>
        )}
      </Box>

      <Box px={2} py={2} sx={{ bgcolor: 'background.default' }}>
        <Box
          display='flex'
          alignItems='center'
          sx={{
            bgcolor: 'background.paper',
            borderRadius: 2,
            px: 1,
            py: 0.5
          }}
        >
          <TextField
            fullWidth
            variant='standard'
            placeholder='Write your question here..'
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                sendMessage()
              }
            }}
            InputProps={{
              disableUnderline: true,
              sx: { ml: 1, color: 'text.primary', fontSize: '0.95rem' }
            }}
          />

          <IconButton
            onClick={sendMessage}
            size='small'
            sx={{
              bgcolor: 'primary.main',
              ml: 1,
              width: 32,
              height: 32,
              borderRadius: 1,
              '&:hover': { bgcolor: 'primary.dark' }
            }}
          >
            <SendIcon sx={{ color: '#FFFFFF', fontSize: '20px' }} />
          </IconButton>
        </Box>
      </Box>
    </Box>
  )
}
