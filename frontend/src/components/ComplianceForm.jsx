import React, { useState } from 'react';

const ComplianceForm = () => {
  const [params, setParams] = useState({
    floorCount: 10,
    elevatorCount: 0,
    buildingHeight: 45,
    usage: 'B-2',
    hasRoofPlatform: false,
  });
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setParams(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : (type === 'number' ? Number(value) : value),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/check-compliance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        {/* 簡單起見，只列出部分輸入欄位 */}
        <div>
          <label>樓層數: <input type="number" name="floorCount" value={params.floorCount} onChange={handleChange} /></label>
        </div>
        <div>
          <label>電梯數: <input type="number" name="elevatorCount" value={params.elevatorCount} onChange={handleChange} /></label>
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? '檢核中...' : '開始檢核'}
        </button>
      </form>

      {error && <div style={{ color: 'red' }}>錯誤: {error}</div>}

      {results && (
        <div>
          <h3>檢核結果</h3>
          <h4>❌ 不符合項目 ({results.failed.length})</h4>
          {results.failed.length > 0 ? (
            <ul>
              {results.failed.map(item => (
                <li key={item.id} style={{ border: '1px solid red', margin: '8px', padding: '8px' }}>
                  <strong>{item.article} [{item.severity}]</strong>
                  <p>問題：{item.violationMsg}</p>
                  <p>建議：{item.suggestion}</p>
                </li>
              ))}
            </ul>
          ) : <p>所有檢查項目均符合要求。</p>}
        </div>
      )}
    </div>
  );
};

export default ComplianceForm;
