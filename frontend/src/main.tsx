import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import ProfilePage from './registration/ProfilePage'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {window.location.pathname === '/profile'
      ? <ProfilePage />
      : <App />}
  </StrictMode>,
)
