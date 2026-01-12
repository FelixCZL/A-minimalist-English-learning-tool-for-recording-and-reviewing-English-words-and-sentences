import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

function App() {
  const [content, setContent] = useState('')
  const [source, setSource] = useState('')
  const [note, setNote] = useState('')
  const [entries, setEntries] = useState([])
  const [selectedEntry, setSelectedEntry] = useState(null)
  const [similarEntries, setSimilarEntries] = useState([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  // 加载所有条目
  const loadEntries = async () => {
    try {
      const response = await axios.get(`${API_BASE}/entries`)
      setEntries(response.data)
    } catch (error) {
      console.error('Error loading entries:', error)
      setMessage('加载条目失败')
    }
  }

  useEffect(() => {
    loadEntries()
  }, [])

  // 保存新条目
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!content.trim()) {
      setMessage('请输入内容')
      return
    }

    setLoading(true)
    setMessage('正在分析...')

    try {
      const response = await axios.post(`${API_BASE}/entries`, {
        content: content.trim(),
        source: source.trim() || null,
        note: note.trim() || null
      })
      
      setMessage('保存成功！')
      setContent('')
      setSource('')
      setNote('')
      
      // 重新加载列表
      await loadEntries()
      
      // 显示新添加的条目
      setSelectedEntry(response.data)
      setSimilarEntries([])
      
    } catch (error) {
      console.error('Error creating entry:', error)
      setMessage('保存失败: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  // 查看条目详情
  const handleViewEntry = async (entry) => {
    setSelectedEntry(entry)
    setSimilarEntries([])
  }

  // 查找相似条目
  const handleFindSimilar = async (entryId) => {
    setLoading(true)
    try {
      const response = await axios.get(`${API_BASE}/entries/${entryId}/similar`)
      setSimilarEntries(response.data)
      setMessage(`找到 ${response.data.length} 个相似条目`)
    } catch (error) {
      console.error('Error finding similar entries:', error)
      setMessage('查找相似条目失败')
    } finally {
      setLoading(false)
    }
  }

  // 删除条目
  const handleDelete = async (entryId) => {
    if (!confirm('确定要删除这条记录吗？')) return
    
    try {
      await axios.delete(`${API_BASE}/entries/${entryId}`)
      setMessage('删除成功')
      await loadEntries()
      if (selectedEntry?.id === entryId) {
        setSelectedEntry(null)
        setSimilarEntries([])
      }
    } catch (error) {
      console.error('Error deleting entry:', error)
      setMessage('删除失败')
    }
  }

  // 渲染 AI 分析结果
  const renderAnalysis = (entry) => {
    try {
      const analysis = JSON.parse(entry.ai_analysis)
      
      if (entry.entry_type === 'word') {
        return (
          <div className="analysis">
            <h3>📚 单词分析</h3>
            <div className="analysis-item">
              <strong>单词:</strong> {analysis.word}
            </div>
            <div className="analysis-item">
              <strong>词性:</strong> {analysis.part_of_speech}
            </div>
            <div className="analysis-item">
              <strong>释义:</strong> {analysis.definition}
            </div>
            <div className="analysis-item">
              <strong>常见搭配:</strong>
              <ul>
                {analysis.collocations?.map((col, idx) => (
                  <li key={idx}>{col}</li>
                ))}
              </ul>
            </div>
            <div className="analysis-item">
              <strong>例句:</strong> {analysis.example_sentence}
            </div>
          </div>
        )
      } else {
        return (
          <div className="analysis">
            <h3>✍️ 句子分析</h3>
            <div className="analysis-item">
              <strong>句子功能:</strong> {analysis.function}
            </div>
            <div className="analysis-item">
              <strong>句式模式:</strong> {analysis.pattern}
            </div>
            <div className="analysis-item">
              <strong>为什么是好句子:</strong> {analysis.why_good}
            </div>
            <div className="analysis-item">
              <strong>改写示例:</strong>
              <ul>
                {analysis.rewrite_examples?.map((example, idx) => (
                  <li key={idx}>{example}</li>
                ))}
              </ul>
            </div>
          </div>
        )
      }
    } catch (error) {
      return <div className="analysis">分析结果解析失败</div>
    }
  }

  return (
    <div className="app">
      <header>
        <h1>📖 English Study Tool</h1>
        <p>记录和复习英语单词与句子</p>
      </header>

      <div className="container">
        {/* 输入区域 */}
        <div className="input-section">
          <h2>添加新内容</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>英文单词或句子 *</label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="粘贴一个单词或完整的句子..."
                rows="4"
                disabled={loading}
              />
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label>来源</label>
                <input
                  type="text"
                  value={source}
                  onChange={(e) => setSource(e.target.value)}
                  placeholder="例如: X, YouTube, Report"
                  disabled={loading}
                />
              </div>
              
              <div className="form-group">
                <label>备注</label>
                <input
                  type="text"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  placeholder="为什么喜欢这句话?"
                  disabled={loading}
                />
              </div>
            </div>

            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? '处理中...' : '💾 保存'}
            </button>
          </form>

          {message && <div className="message">{message}</div>}
        </div>

        {/* 历史记录区域 */}
        <div className="history-section">
          <h2>📚 历史记录 ({entries.length})</h2>
          <div className="entries-list">
            {entries.map((entry) => (
              <div 
                key={entry.id} 
                className={`entry-card ${selectedEntry?.id === entry.id ? 'selected' : ''}`}
                onClick={() => handleViewEntry(entry)}
              >
                <div className="entry-header">
                  <span className="entry-type">{entry.entry_type === 'word' ? '📝 单词' : '✍️ 句子'}</span>
                  <span className="entry-date">{new Date(entry.created_at).toLocaleDateString()}</span>
                </div>
                <div className="entry-content">{entry.content}</div>
                {entry.tags && (
                  <div className="entry-tags">
                    {entry.tags.split(',').map((tag, idx) => (
                      <span key={idx} className="tag">{tag}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* 详情区域 */}
        {selectedEntry && (
          <div className="detail-section">
            <div className="detail-header">
              <h2>详细信息</h2>
              <div className="detail-actions">
                <button 
                  onClick={() => handleFindSimilar(selectedEntry.id)}
                  className="btn-secondary"
                  disabled={loading}
                >
                  🔍 查找相似
                </button>
                <button 
                  onClick={() => handleDelete(selectedEntry.id)}
                  className="btn-danger"
                >
                  🗑️ 删除
                </button>
              </div>
            </div>

            <div className="detail-content">
              <div className="detail-original">
                <h3>原文</h3>
                <p className="original-text">{selectedEntry.content}</p>
                {selectedEntry.source && (
                  <p className="meta"><strong>来源:</strong> {selectedEntry.source}</p>
                )}
                {selectedEntry.note && (
                  <p className="meta"><strong>备注:</strong> {selectedEntry.note}</p>
                )}
              </div>

              {renderAnalysis(selectedEntry)}

              {/* 相似条目 */}
              {similarEntries.length > 0 && (
                <div className="similar-section">
                  <h3>🔗 相似内容</h3>
                  {similarEntries.map((similar) => (
                    <div 
                      key={similar.id} 
                      className="similar-card"
                      onClick={() => handleViewEntry(similar)}
                    >
                      <div className="similar-header">
                        <span className="entry-type">
                          {similar.entry_type === 'word' ? '📝 单词' : '✍️ 句子'}
                        </span>
                        <span className="similarity-score">
                          相似度: {(similar.similarity * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="similar-content">{similar.content}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
