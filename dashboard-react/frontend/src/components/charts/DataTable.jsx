const DataTable = ({ data }) => {
  if (!data || !data.data || data.data.length === 0) {
    return <div className="no-data">Aucune donnée disponible</div>
  }
  
  return (
    <div className="data-table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Nom</th>
            <th className="mobile-hidden">Groupe</th>
            <th>Questions</th>
            <th className="mobile-hidden">Réponses</th>
          </tr>
        </thead>
        <tbody>
          {data.data.map((row, idx) => (
            <tr key={idx}>
              <td>{row.nom_complet}</td>
              <td className="mobile-hidden">{row.groupe_parlementaire}</td>
              <td><strong>{row.nombre_questions}</strong></td>
              <td className="mobile-hidden">{row.nombre_reponses}</td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {data.pages > 1 && (
        <div className="pagination">
          Page {data.page} / {data.pages}
        </div>
      )}
    </div>
  )
}

export default DataTable
