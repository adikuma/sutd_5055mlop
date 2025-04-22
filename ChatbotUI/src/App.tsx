import React from 'react'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import { CssBaseline } from '@mui/material'
import { Chatbot } from '@features/chats'

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#635BFF' },
    background: {
      default: '#1E1E1E',
      paper: '#2C2C2E'
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#B0B0B0'
    },
    divider: 'rgba(255,255,255,0.12)'
  },
  typography: {
    fontFamily: [
      '"SF Pro Text"',
      '"Inter"',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif'
    ].join(','),
    h6: { fontWeight: 600 },
    body2: { fontSize: '0.9rem' },
    caption: { fontSize: '0.70rem' }
  }
})

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Chatbot />
    </ThemeProvider>
  )
}

export default App
