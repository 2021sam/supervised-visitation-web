import AuthPanel from '../auth/AuthPanel'

export default function ProfilePage() {
  return (
    <main>
      <nav>
        <a href="/">← Back to Directory</a>
      </nav>

      <AuthPanel profilePage />
    </main>
  )
}
