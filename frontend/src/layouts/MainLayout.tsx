import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Navbar from '../components/Navbar'
import Sidebar from '../components/Sidebar'
import CreatePostModal from '../components/modals/CreatePostModal'
import CreateCommunityModal from '../components/modals/CreateCommunityModal'
import LoginModal from '../components/modals/LoginModal'

export default function MainLayout() {
  const [showCreatePost, setShowCreatePost] = useState(false)
  const [showCreateCommunity, setShowCreateCommunity] = useState(false)
  const [showLogin, setShowLogin] = useState(false)

  return (
    <div className="min-h-screen bg-[#dae0e6]">
      <Navbar
        onCreatePost={() => setShowCreatePost(true)}
        onShowLogin={() => setShowLogin(true)}
      />

      <div className="max-w-6xl mx-auto px-4 py-6 flex gap-6 items-start">
        <main className="flex-1 min-w-0">
          <Outlet />
        </main>
        <Sidebar
          onCreatePost={() => setShowCreatePost(true)}
          onCreateCommunity={() => setShowCreateCommunity(true)}
        />
      </div>

      {showCreatePost && <CreatePostModal onClose={() => setShowCreatePost(false)} />}
      {showCreateCommunity && <CreateCommunityModal onClose={() => setShowCreateCommunity(false)} />}
      {showLogin && <LoginModal onClose={() => setShowLogin(false)} />}
    </div>
  )
}
