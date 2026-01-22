import { useEffect, useRef } from 'react'
import { createChart } from 'lightweight-charts'

function Charts({ username, onLogout }) {
  const chartContainerRef = useRef()

  useEffect(() => {
    if (!chartContainerRef.current) return

    console.log('Creating chart in container:', chartContainerRef.current)
    console.log('Container width:', chartContainerRef.current?.clientWidth)
    console.log('Container height:', chartContainerRef.current?.clientHeight)

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: 'transparent' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#e0e0e0' },
        horzLines: { color: '#e0e0e0' },
      },
      width: chartContainerRef.current.clientWidth || 800,
      height: 400,
    })

    console.log('Chart created successfully')

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    })

    const data = [
      { time: '2018-12-22', open: 75.16, high: 82.84, low: 36.16, close: 45.72 },
      { time: '2018-12-23', open: 45.12, high: 53.90, low: 45.12, close: 48.09 },
      { time: '2018-12-24', open: 60.71, high: 60.71, low: 53.39, close: 59.29 },
      { time: '2018-12-25', open: 68.26, high: 68.26, low: 59.04, close: 60.50 },
      { time: '2018-12-26', open: 67.71, high: 105.85, low: 66.67, close: 91.04 },
      { time: '2018-12-27', open: 91.04, high: 121.40, low: 82.70, close: 111.40 },
      { time: '2018-12-28', open: 111.51, high: 142.83, low: 103.34, close: 131.25 },
      { time: '2018-12-29', open: 131.33, high: 151.17, low: 77.68, close: 96.43 },
      { time: '2018-12-30', open: 106.33, high: 110.20, low: 90.39, close: 98.10 },
      { time: '2018-12-31', open: 109.87, high: 114.69, low: 85.66, close: 111.26 },
    ]

    candlestickSeries.setData(data)
    console.log('Data set successfully')

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth || 800 })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [])

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">📊 K线图表</h2>
        <p className="text-gray-600">
          基于 TradingView Lightweight Charts 的金融图表示例
        </p>
      </div>

       <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
         <div 
           ref={chartContainerRef} 
           style={{ 
             minHeight: '400px', 
             width: '100%' 
           }} 
         />
       </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h3 className="font-semibold text-blue-800 mb-2">ℹ️ 功能说明</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• 交互式图表：支持鼠标滚轮缩放</li>
          <li>• 拖拽浏览：按住鼠标拖动查看历史数据</li>
          <li>• 悬停详情：鼠标悬停显示详细信息</li>
          <li>• 响应式设计：自适应屏幕尺寸</li>
        </ul>
      </div>

      <div className="mt-6 p-4 bg-amber-50 rounded-lg border border-amber-200">
        <p className="text-sm text-amber-700">
          <span className="font-semibold">注意：</span>
          此图表使用 TradingView Lightweight Charts 库渲染，数据为示例数据。
        </p>
      </div>
    </div>
  )
}

export default Charts
