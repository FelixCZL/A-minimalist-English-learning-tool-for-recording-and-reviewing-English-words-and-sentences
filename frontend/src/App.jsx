import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom'
import axios from 'axios'
import Login from './Login.jsx'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const DEVICE_ID_KEY = 'english_study_device_id'
const LAST_SYNC_KEY = 'english_study_last_sync'
const LOCAL_DATA_KEY = 'english_study_local_data'
const TOKEN_KEY = 'english_study_token'

function EnglishStudyApp({ username, onLogout }) {
  const [content, setContent] = useState('')
  const [source, setSource] = useState('')
  const [note, setNote] = useState('')
  const [entries, setEntries] = useState([])
  const [selectedEntry, setSelectedEntry] = useState(null)
  const [similarEntries, setSimilarEntries] = useState([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [deviceId, setDeviceId] = useState('')
  const [syncStatus, setSyncStatus] = useState('idle')
  const [lastSyncTime, setLastSyncTime] = useState(null)
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const navigate = useNavigate()

  const api = axios.create({
    baseURL: API_BASE,
    headers: {
      Authorization: `Bearer ${localStorage.getItem(TOKEN_KEY)}`,
    },
  })

  const getDeviceId = () => {
    let id = localStorage.getItem(DEVICE_ID_KEY)
    if (!id) {
      id = 'device_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
      localStorage.setItem(DEVICE_ID_KEY, id)
    }
    return id
  }

  const saveLocalData = (data) => {
    localStorage.setItem(LOCAL_DATA_KEY, JSON.stringify(data))
  }

  const loadLocalData = () => {
    const data = localStorage.getItem(LOCAL_DATA_KEY)
    return data ? JSON.parse(data) : []
  }

  const syncData = async () => {
    if (!isOnline) {
      setSyncStatus('offline')
      return
    }

    try {
      setSyncStatus('syncing')
      const localEntries = loadLocalData()
      
      const response = await api.post('/sync', {
        device_id: deviceId,
        local_entries: localEntries
      })

      const { server_entries, conflicts, last_sync_time } = response.data

      if (conflicts.length > 0) {
        setMessage(`发现 ${conflicts.length} 个冲突，请手动处理`)
        setSyncStatus('conflict')
      } else {
        setSyncStatus('synced')
        localStorage.setItem(LAST_SYNC_KEY, last_sync_time)
        setLastSyncTime(last_sync_time)
      }

      const allEntries = [...server_entries]
      const localIds = new Set(localEntries.map(e => e.id))
      server_entries.forEach(se => {
        localIds.delete(se.id)
      })
      localEntries.filter(e => localIds.has(e.id) && !e.deleted).forEach(le => {
        allEntries.push(le)
      })

      setEntries(allEntries.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)))
      saveLocalData([])

      if (conflicts.length === 0) {
        setMessage('同步完成')
      }
    } catch (error) {
      console.error('Sync error:', error)
      setSyncStatus('error')
      setMessage('同步失败: ' + (error.response?.data?.detail || error.message))
    }
  }

  const loadEntries = async () => {
    try {
      const response = await api.get('/entries')
      setEntries(response.data)
      saveLocalData([])
    } catch (error) {
      console.error('Error loading entries:', error)
      setMessage('加载条目失败')
      setSyncStatus('offline')
    }
  }

  useEffect(() => {
    const id = getDeviceId()
    setDeviceId(id)
    const lastSync = localStorage.getItem(LAST_SYNC_KEY)
    setLastSyncTime(lastSync)
    loadEntries()
    
    const syncInterval = setInterval(() => {
      if (isOnline) {
        syncData()
      }
    }, 30000)

    return () => clearInterval(syncInterval)
  }, [isOnline])

  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!content.trim()) {
      setMessage('请输入内容')
      return
    }

    setLoading(true)
    setMessage('正在分析...')

    try {
      const response = await api.post('/entries', {
        content: content.trim(),
        source: source.trim() || null,
        note: note.trim() || null
      })
      
      setMessage('保存成功！')
      setContent('')
      setSource('')
      setNote('')
      
      await loadEntries()
      
      setSelectedEntry(response.data)
      setSimilarEntries([])
      await syncData()
      
    } catch (error) {
      if (!isOnline) {
        const localEntries = loadLocalData()
        const newEntry = {
          id: Date.now(),
          content: content.trim(),
          source: source.trim() || null,
          note: note.trim() || null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          deleted: 0,
          device_id: deviceId,
          sync_status: 'pending',
          version: 1,
          entry_type: 'word',
          ai_analysis: '{}',
          tags: ''
        }
        localEntries.push(newEntry)
        saveLocalData(localEntries)
        setEntries([newEntry, ...entries])
        setMessage('已保存到本地，离线状态下将同步到服务器')
      } else {
        console.error('Error creating entry:', error)
        setMessage('保存失败: ' + (error.response?.data?.detail || error.message))
      }
    } finally {
      setLoading(false)
    }
  }

  const handleViewEntry = async (entry) => {
    setSelectedEntry(entry)
    setSimilarEntries([])
  }

  const handleFindSimilar = async (entryId) => {
    setLoading(true)
    try {
      const response = await api.get(`/entries/${entryId}/similar`)
      setSimilarEntries(response.data)
      setMessage(`找到 ${response.data.length} 个相似条目`)
    } catch (error) {
      console.error('Error finding similar entries:', error)
      setMessage('查找相似条目失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (entryId) => {
    if (!confirm('确定要删除这条记录吗？')) return
    
    try {
      await api.delete(`/entries/${entryId}`)
      setMessage('删除成功')
      await loadEntries()
      await syncData()
      if (selectedEntry?.id === entryId) {
        setSelectedEntry(null)
        setSimilarEntries([])
      }
    } catch (error) {
      if (!isOnline) {
        const localEntries = loadLocalData()
        const entryIndex = entries.findIndex(e => e.id === entryId)
        if (entryIndex !== -1) {
          const entry = { ...entries[entryIndex], deleted: 1, updated_at: new Date().toISOString() }
          localEntries.push(entry)
          saveLocalData(localEntries)
          setEntries(entries.filter(e => e.id !== entryId))
          setMessage('已标记删除，离线状态下将同步到服务器')
        }
        if (selectedEntry?.id === entryId) {
          setSelectedEntry(null)
          setSimilarEntries([])
        }
      } else {
        console.error('Error deleting entry:', error)
        setMessage('删除失败')
      }
    }
  }

  const renderAnalysis = (entry) => {
    try {
      const analysis = JSON.parse(entry.ai_analysis)
      
      if (entry.entry_type === 'word') {
        return (
          <div className="bg-yellow-50 border-l-4 border-yellow-500 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-yellow-800 mb-3">📚 单词分析</h3>
            <div className="space-y-2">
              <div>
                <span className="font-semibold text-gray-700">单词:</span> {analysis.word}
              </div>
              <div>
                <span className="font-semibold text-gray-700">词性:</span> {analysis.part_of_speech}
              </div>
              <div>
                <span className="font-semibold text-gray-700">释义:</span> {analysis.definition}
              </div>
              <div>
                <span className="font-semibold text-gray-700">常见搭配:</span>
                <ul className="list-disc list-inside ml-2 mt-1">
                  {analysis.collocations?.map((col, idx) => (
                    <li key={idx}>{col}</li>
                  ))}
                </ul>
              </div>
              <div>
                <span className="font-semibold text-gray-700">例句:</span> {analysis.example_sentence}
              </div>
            </div>
          </div>
        )
      } else {
        return (
          <div className="bg-yellow-50 border-l-4 border-yellow-500 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-yellow-800 mb-3">✍️ 句子分析</h3>
            <div className="space-y-2">
              <div>
                <span className="font-semibold text-gray-700">句子功能:</span> {analysis.function}
              </div>
              <div>
                <span className="font-semibold text-gray-700">句式模式:</span> {analysis.pattern}
              </div>
              <div>
                <span className="font-semibold text-gray-700">为什么是好句子:</span> {analysis.why_good}
              </div>
              <div>
                <span className="font-semibold text-gray-700">改写示例:</span>
                <ul className="list-disc list-inside ml-2 mt-1">
                  {analysis.rewrite_examples?.map((example, idx) => (
                    <li key={idx}>{example}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )
      }
    } catch (error) {
      return <div className="text-red-600">分析结果解析失败</div>
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Link to="/" className="text-xl font-bold text-indigo-600 hover:text-indigo-800">
                📖 English Study Tool
              </Link>
              <Link
                to="/"
                className="text-gray-700 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium transition"
              >
                学习
              </Link>
              <Link
                to="/charts"
                className="text-gray-700 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium transition"
              >
                图表
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <span className={`text-sm ${isOnline ? 'text-green-600' : 'text-red-600'}`}>
                {isOnline ? '🟢 在线' : '🔴 离线'}
              </span>
              <span className="text-sm text-gray-700">
                欢迎, {username}
              </span>
              <button
                onClick={onLogout}
                className="bg-red-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-600 transition"
              >
                退出
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">添加新内容</h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    英文单词或句子 *
                  </label>
                  <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="粘贴一个单词或完整的句子..."
                    rows="4"
                    disabled={loading}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition resize-none"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      来源
                    </label>
                    <input
                      type="text"
                      value={source}
                      onChange={(e) => setSource(e.target.value)}
                      placeholder="例如: X, YouTube, Report"
                      disabled={loading}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      备注
                    </label>
                    <input
                      type="text"
                      value={note}
                      onChange={(e) => setNote(e.target.value)}
                      placeholder="为什么喜欢这句话?"
                      disabled={loading}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white py-3 rounded-lg font-semibold hover:from-indigo-600 hover:to-purple-700 transition duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
                >
                  {loading ? '处理中...' : '💾 保存'}
                </button>
              </form>

              {message && (
                <div className="mt-4 p-4 bg-blue-50 border-l-4 border-blue-500 rounded-lg">
                  <p className="text-sm text-blue-700">{message}</p>
                </div>
              )}
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">
                📚 历史记录 ({entries.length})
              </h2>
              <div className="max-h-96 overflow-y-auto space-y-3">
                {entries.map((entry) => (
                  <div 
                    key={entry.id} 
                    className={`p-4 border-2 rounded-lg cursor-pointer transition hover:shadow-md ${
                      selectedEntry?.id === entry.id 
                        ? 'border-indigo-500 bg-indigo-50' 
                        : 'border-gray-200 hover:border-indigo-300'
                    }`}
                    onClick={() => handleViewEntry(entry)}
                  >
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-semibold text-indigo-600">
                        {entry.entry_type === 'word' ? '📝 单词' : '✍️ 句子'}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(entry.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="text-gray-800">{entry.content}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {selectedEntry && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex justify-between items-center mb-4 pb-4 border-b-2 border-gray-200">
                <h2 className="text-xl font-bold text-gray-800">详细信息</h2>
                <div className="flex gap-2">
                  <button 
                    onClick={() => handleFindSimilar(selectedEntry.id)}
                    className="bg-green-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-600 transition"
                    disabled={loading}
                  >
                    🔍 查找相似
                  </button>
                  <button 
                    onClick={() => handleDelete(selectedEntry.id)}
                    className="bg-red-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-600 transition"
                  >
                    🗑️ 删除
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-indigo-500">
                  <h3 className="text-lg font-semibold text-indigo-800 mb-2">原文</h3>
                  <p className="text-lg text-gray-800 mb-2">{selectedEntry.content}</p>
                  {selectedEntry.source && (
                    <p className="text-sm text-gray-600">
                      <strong>来源:</strong> {selectedEntry.source}
                    </p>
                  )}
                  {selectedEntry.note && (
                    <p className="text-sm text-gray-600">
                      <strong>备注:</strong> {selectedEntry.note}
                    </p>
                  )}
                </div>

                {renderAnalysis(selectedEntry)}

                {similarEntries.length > 0 && (
                  <div className="bg-green-50 border-l-4 border-green-500 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-green-800 mb-3">🔗 相似内容</h3>
                    <div className="space-y-2">
                      {similarEntries.map((similar) => (
                        <div 
                          key={similar.id} 
                          className="bg-white p-3 rounded-lg cursor-pointer hover:shadow-md transition"
                          onClick={() => handleViewEntry(similar)}
                        >
                          <div className="flex justify-between items-center mb-1">
                            <span className="text-xs font-semibold text-indigo-600">
                              {similar.entry_type === 'word' ? '📝 单词' : '✍️ 句子'}
                            </span>
                            <span className="text-xs text-green-600 font-semibold">
                              相似度: {(similar.similarity * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className="text-sm text-gray-800">{similar.content}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function Charts({ username, onLogout }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Link to="/" className="text-xl font-bold text-indigo-600 hover:text-indigo-800">
                📖 English Study Tool
              </Link>
              <Link
                to="/"
                className="text-gray-700 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium transition"
              >
                学习
              </Link>
              <Link
                to="/charts"
                className="text-indigo-600 bg-indigo-50 px-3 py-2 rounded-md text-sm font-medium transition"
              >
                图表
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                欢迎, {username}
              </span>
              <button
                onClick={onLogout}
                className="bg-red-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-600 transition"
              >
                退出
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-2">📊 图表页面</h2>
            <p className="text-gray-600">
              此页面正在开发中...
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const [user, setUser] = useState(null)

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY)
    const username = localStorage.getItem('username')
    if (token && username) {
      setUser(username)
    }
  }, [])

  const handleLogin = (username) => {
    setUser(username)
  }

  const handleLogout = () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem('username')
    setUser(null)
  }

  return (
    <Router>
      {user ? (
        <Routes>
          <Route
            path="/"
            element={<EnglishStudyApp username={user} onLogout={handleLogout} />}
          />
          <Route
            path="/charts"
            element={<Charts onLogout={handleLogout} username={user} />}
          />
        </Routes>
      ) : (
        <Routes>
          <Route path="*" element={<Login onLogin={handleLogin} />} />
        </Routes>
      )}
    </Router>
  )
}
