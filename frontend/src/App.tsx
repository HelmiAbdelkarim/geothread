import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { DataProvider } from './context/DataContext'
import MainLayout from './layouts/MainLayout'
import FeedPage from './pages/FeedPage'
import PostDetailPage from './pages/PostDetailPage'
import SearchPage from './pages/SearchPage'
import SubredditPage from './pages/SubredditPage'
import UserProfilePage from './pages/UserProfilePage'

export default function App() {
  return (
    <AuthProvider>
      <DataProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<MainLayout />}>
              <Route index element={<FeedPage />} />
              <Route path="r/:subredditName" element={<SubredditPage />} />
              <Route path="post/:postId" element={<PostDetailPage />} />
              <Route path="u/:username" element={<UserProfilePage />} />
              <Route path="search" element={<SearchPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </DataProvider>
    </AuthProvider>
  )
}
