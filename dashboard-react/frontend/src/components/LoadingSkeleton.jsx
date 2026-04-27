const LoadingSkeleton = () => {
  return (
    <div className="loading-skeleton">
      <div className="kpi-grid">
        <div className="skeleton-item" />
        <div className="skeleton-item" />
        <div className="skeleton-item" />
      </div>
      <div className="charts-grid">
        <div className="skeleton-item" style={{ height: '300px' }} />
        <div className="skeleton-item" style={{ height: '300px' }} />
        <div className="skeleton-item chart-full" style={{ height: '400px' }} />
      </div>
    </div>
  )
}

export default LoadingSkeleton
