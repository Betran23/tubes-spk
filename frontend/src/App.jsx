import { useEffect, useState } from "react";
import {
  calculateVikor,
  commitCsvImport,
  createAlternative,
  createCriterion,
  createScore,
  deleteAlternative,
  deleteCriterion,
  deleteScore,
  getCompromise,
  getRanking,
  getScoreMatrix,
  listAlternatives,
  listCriteria,
  listScores,
  previewCsvImport,
  updateAlternative,
  updateCriterion,
  updateScore,
} from "./api.js";

const emptyAlternative = { code: "", name: "" };
const emptyCriterion = { code: "", name: "", weight: "", type: "benefit" };
const emptyScore = { alternative_id: "", criterion_id: "", value: "" };
const pageSizeOptions = [10, 20, 50, 100];

const buildImportCriteria = (count) =>
  Array.from({ length: count }, (_, index) => ({
    code: `C${index + 1}`,
    name: "",
    weight: "",
    type: "cost",
    valueColumn: "",
  }));

function App() {
  const [alternatives, setAlternatives] = useState([]);
  const [criteria, setCriteria] = useState([]);
  const [scores, setScores] = useState([]);
  const [matrix, setMatrix] = useState([]);
  const [calculation, setCalculation] = useState(null);
  const [ranking, setRanking] = useState(null);
  const [compromise, setCompromise] = useState(null);
  const [alternativeForm, setAlternativeForm] = useState(emptyAlternative);
  const [criterionForm, setCriterionForm] = useState(emptyCriterion);
  const [scoreForm, setScoreForm] = useState(emptyScore);
  const [editingAlternativeId, setEditingAlternativeId] = useState(null);
  const [editingCriterionId, setEditingCriterionId] = useState(null);
  const [editingScoreId, setEditingScoreId] = useState(null);
  const [vValue, setVValue] = useState("0.5");
  const [vikorSearch, setVikorSearch] = useState("");
  const [csvFile, setCsvFile] = useState(null);
  const [csvPreview, setCsvPreview] = useState(null);
  const [importMode, setImportMode] = useState("replace");
  const [criterionCount, setCriterionCount] = useState(5);
  const [importAlternativeCodeColumn, setImportAlternativeCodeColumn] = useState("");
  const [importAlternativeCodeColumn2, setImportAlternativeCodeColumn2] = useState("");
  const [importAlternativeNameColumn, setImportAlternativeNameColumn] = useState("");
  const [importCriteria, setImportCriteria] = useState(buildImportCriteria(5));
  const [importResult, setImportResult] = useState(null);
  const [activeSection, setActiveSection] = useState("alternatives");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const showError = (err) => {
    setError(err.payload ? JSON.stringify(err.payload, null, 2) : err.message);
  };

  const runAction = async (action) => {
    setLoading(true);
    setError("");
    try {
      await action();
    } catch (err) {
      showError(err);
    } finally {
      setLoading(false);
    }
  };

  const loadData = async () => {
    const [alternativeData, criterionData, scoreData, matrixData] =
      await Promise.all([
        listAlternatives(),
        listCriteria(),
        listScores(),
        getScoreMatrix(),
      ]);
    setAlternatives(alternativeData);
    setCriteria(criterionData);
    setScores(scoreData);
    setMatrix(matrixData);
  };

  useEffect(() => {
    runAction(loadData);
  }, []);

  const submitAlternative = (event) => {
    event.preventDefault();
    runAction(async () => {
      if (editingAlternativeId) {
        await updateAlternative(editingAlternativeId, alternativeForm);
      } else {
        await createAlternative(alternativeForm);
      }
      setAlternativeForm(emptyAlternative);
      setEditingAlternativeId(null);
      await loadData();
    });
  };

  const submitCriterion = (event) => {
    event.preventDefault();
    runAction(async () => {
      const payload = {
        ...criterionForm,
        weight: Number(criterionForm.weight),
      };
      if (editingCriterionId) {
        await updateCriterion(editingCriterionId, payload);
      } else {
        await createCriterion(payload);
      }
      setCriterionForm(emptyCriterion);
      setEditingCriterionId(null);
      await loadData();
    });
  };

  const getNextCriterionId = (currentCriterionId) => {
    if (!criteria.length) return "";
    const currentIndex = criteria.findIndex(
      (criterion) => criterion.id === Number(currentCriterionId),
    );
    const nextIndex =
      currentIndex === -1 || currentIndex === criteria.length - 1
        ? 0
        : currentIndex + 1;
    return String(criteria[nextIndex].id);
  };

  const submitScore = (event) => {
    event.preventDefault();
    runAction(async () => {
      const payload = {
        alternative_id: Number(scoreForm.alternative_id),
        criterion_id: Number(scoreForm.criterion_id),
        value: Number(scoreForm.value),
      };
      if (editingScoreId) {
        await updateScore(editingScoreId, payload);
        setScoreForm(emptyScore);
        setEditingScoreId(null);
      } else {
        await createScore(payload);
        setScoreForm({
          alternative_id: String(payload.alternative_id),
          criterion_id: getNextCriterionId(payload.criterion_id),
          value: "",
        });
      }
      await loadData();
    });
  };

  const removeItem = (label, callback) => {
    if (!window.confirm(`Hapus ${label}?`)) return;
    runAction(async () => {
      await callback();
      await loadData();
    });
  };

  const calculate = () => {
    runAction(async () => {
      const [calculationData, rankingData, compromiseData] = await Promise.all([
        calculateVikor(vValue || "0.5"),
        getRanking(vValue || "0.5"),
        getCompromise(vValue || "0.5"),
      ]);
      setCalculation(calculationData);
      setRanking(rankingData);
      setCompromise(compromiseData);
    });
  };

  const handleCsvPreview = (file) => {
    if (!file) return;
    setCsvFile(file);
    setImportResult(null);
    runAction(async () => {
      const preview = await previewCsvImport(file);
      setCsvPreview(preview);
      setImportAlternativeCodeColumn(preview.headers[0] || "");
      setImportAlternativeCodeColumn2("");
      setImportAlternativeNameColumn(preview.headers[1] || preview.headers[0] || "");
      setImportCriteria((currentCriteria) =>
        currentCriteria.map((criterion, index) => ({
          ...criterion,
          name: criterion.name || preview.headers[index + 2] || criterion.code,
          valueColumn: criterion.valueColumn || preview.headers[index + 2] || "",
        })),
      );
    });
  };

  const changeCriterionCount = (value) => {
    const nextCount = Math.max(1, Number(value) || 1);
    setCriterionCount(nextCount);
    setImportCriteria((currentCriteria) => {
      const nextCriteria = buildImportCriteria(nextCount);
      return nextCriteria.map((criterion, index) => ({
        ...criterion,
        ...(currentCriteria[index] || {}),
      }));
    });
  };

  const updateImportCriterion = (index, key, value) => {
    setImportCriteria((currentCriteria) =>
      currentCriteria.map((criterion, criterionIndex) =>
        criterionIndex === index ? { ...criterion, [key]: value } : criterion,
      ),
    );
  };

  const commitImport = () => {
    if (!csvFile) {
      setError("Upload CSV dulu sebelum import final.");
      return;
    }
    runAction(async () => {
      const result = await commitCsvImport(csvFile, {
        mode: importMode,
        alternativeCodeColumns: [importAlternativeCodeColumn, importAlternativeCodeColumn2].filter(Boolean),
        alternativeNameColumn: importAlternativeNameColumn,
        criteria: importCriteria,
      });
      setImportResult(result);
      await loadData();
    });
  };

  const searchTerm = vikorSearch.trim().toLowerCase();
  const filteredRanking =
    ranking?.ranking.filter((item) => {
      if (!searchTerm) return true;
      return [
        item.rank,
        item.alternative_code,
        item.alternative_name,
        item.S,
        item.R,
        item.Q,
      ].some((value) => String(value).toLowerCase().includes(searchTerm));
    }) ?? [];

  return (
    <main className="app-shell">
      <section className="hero block-shadow">
        <div>
          <p className="eyebrow">SPK VIKOR DASHBOARD</p>
          <h1>VIKOR.</h1>
          <p className="hero-copy">
            SISTEM PENDUKUNG KEPUTUSAN PENILAIAN KINERJA GARDU DISTRIBUSI
            BERDASARKAN KONDISI OVERLOAD MENGGUNAKAN METODE VIKOR (STUDI KASUS:
            PLN ULP BALIKPAPAN UTARA) .
          </p>
        </div>
        <div className="hero-stamp">
          VIKOR
          <br />
          Q↓
        </div>
      </section>

      <nav className="nav-tabs" aria-label="Navigasi dashboard">
        {[
          ["alternatives", "Alternatif"],
          ["criteria", "Kriteria"],
          ["scores", "Scores"],
          ["matrix", "Matrix"],
          ["import", "Import CSV"],
          ["vikor", "VIKOR"],
        ].map(([key, label]) => (
          <button
            key={key}
            className={activeSection === key ? "active" : ""}
            onClick={() => setActiveSection(key)}
          >
            {label}
          </button>
        ))}
      </nav>

      {loading && <div className="notice">Memproses request...</div>}
      {error && <pre className="error-panel">{error}</pre>}

      {activeSection === "alternatives" && (
        <section className="grid-section">
          <form className="panel" onSubmit={submitAlternative}>
            <h2>
              {editingAlternativeId ? "Edit Alternatif" : "Tambah Alternatif"}
            </h2>
            <label>
              Kode
              <input
                value={alternativeForm.code}
                onChange={(e) =>
                  setAlternativeForm({
                    ...alternativeForm,
                    code: e.target.value,
                  })
                }
                placeholder="A1"
                required
              />
            </label>
            <label>
              Nama
              <input
                value={alternativeForm.name}
                onChange={(e) =>
                  setAlternativeForm({
                    ...alternativeForm,
                    name: e.target.value,
                  })
                }
                placeholder="Alternatif 1"
                required
              />
            </label>
            <div className="button-row">
              <button type="submit">Simpan</button>
              <button
                type="button"
                className="muted"
                onClick={() => {
                  setAlternativeForm(emptyAlternative);
                  setEditingAlternativeId(null);
                }}
              >
                Reset
              </button>
            </div>
          </form>
          <DataTable
            headers={["ID", "Kode", "Nama", "Aksi"]}
            rows={alternatives.map((item) => [
              item.id,
              item.code,
              item.name,
              <Actions
                onEdit={() => {
                  setEditingAlternativeId(item.id);
                  setAlternativeForm({ code: item.code, name: item.name });
                }}
                onDelete={() =>
                  removeItem(`alternatif ${item.code}`, () =>
                    deleteAlternative(item.id),
                  )
                }
              />,
            ])}
          />
        </section>
      )}

      {activeSection === "criteria" && (
        <section className="grid-section">
          <form className="panel" onSubmit={submitCriterion}>
            <h2>{editingCriterionId ? "Edit Kriteria" : "Tambah Kriteria"}</h2>
            <label>
              Kode
              <input
                value={criterionForm.code}
                onChange={(e) =>
                  setCriterionForm({ ...criterionForm, code: e.target.value })
                }
                placeholder="C1"
                required
              />
            </label>
            <label>
              Nama
              <input
                value={criterionForm.name}
                onChange={(e) =>
                  setCriterionForm({ ...criterionForm, name: e.target.value })
                }
                placeholder="Harga"
                required
              />
            </label>
            <label>
              Bobot
              <input
                type="number"
                step="0.01"
                value={criterionForm.weight}
                onChange={(e) =>
                  setCriterionForm({ ...criterionForm, weight: e.target.value })
                }
                placeholder="0.25 atau 25"
                required
              />
            </label>
            <label>
              Tipe
              <select
                value={criterionForm.type}
                onChange={(e) =>
                  setCriterionForm({ ...criterionForm, type: e.target.value })
                }
              >
                <option value="benefit">Benefit</option>
                <option value="cost">Cost</option>
              </select>
            </label>
            <div className="button-row">
              <button type="submit">Simpan</button>
              <button
                type="button"
                className="muted"
                onClick={() => {
                  setCriterionForm(emptyCriterion);
                  setEditingCriterionId(null);
                }}
              >
                Reset
              </button>
            </div>
          </form>
          <DataTable
            headers={["ID", "Kode", "Nama", "Bobot", "Tipe", "Aksi"]}
            rows={criteria.map((item) => [
              item.id,
              item.code,
              item.name,
              item.weight,
              item.type,
              <Actions
                onEdit={() => {
                  setEditingCriterionId(item.id);
                  setCriterionForm({
                    code: item.code,
                    name: item.name,
                    weight: item.weight,
                    type: item.type,
                  });
                }}
                onDelete={() =>
                  removeItem(`kriteria ${item.code}`, () =>
                    deleteCriterion(item.id),
                  )
                }
              />,
            ])}
          />
        </section>
      )}

      {activeSection === "scores" && (
        <section className="grid-section">
          <form className="panel" onSubmit={submitScore}>
            <h2>{editingScoreId ? "Edit Score" : "Tambah Score"}</h2>
            <label>
              Alternatif
              <select
                value={scoreForm.alternative_id}
                onChange={(e) =>
                  setScoreForm({ ...scoreForm, alternative_id: e.target.value })
                }
                required
              >
                <option value="">Pilih alternatif</option>
                {alternatives.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.code} - {item.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Kriteria
              <select
                value={scoreForm.criterion_id}
                onChange={(e) =>
                  setScoreForm({ ...scoreForm, criterion_id: e.target.value })
                }
                required
              >
                <option value="">Pilih kriteria</option>
                {criteria.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.code} - {item.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Nilai
              <input
                type="number"
                step="0.01"
                value={scoreForm.value}
                onChange={(e) =>
                  setScoreForm({ ...scoreForm, value: e.target.value })
                }
                required
              />
            </label>
            <div className="button-row">
              <button type="submit">Simpan</button>
              <button
                type="button"
                className="muted"
                onClick={() => {
                  setScoreForm(emptyScore);
                  setEditingScoreId(null);
                }}
              >
                Reset
              </button>
            </div>
          </form>
          <DataTable
            headers={["ID", "Alt ID", "Crit ID", "Nilai", "Aksi"]}
            rows={scores.map((item) => [
              item.id,
              item.alternative_id,
              item.criterion_id,
              item.value,
              <Actions
                onEdit={() => {
                  setEditingScoreId(item.id);
                  setScoreForm({
                    alternative_id: item.alternative_id,
                    criterion_id: item.criterion_id,
                    value: item.value,
                  });
                }}
                onDelete={() =>
                  removeItem(`score ${item.id}`, () => deleteScore(item.id))
                }
              />,
            ])}
          />
        </section>
      )}

      {activeSection === "matrix" && (
        <MatrixTable matrix={matrix} criteria={criteria} />
      )}

      {activeSection === "import" && (
        <section className="panel full-width import-wizard">
          <div className="calc-header">
            <div>
              <h2>Import CSV</h2>
              <p>Upload CSV, mapping kolom, validasi, lalu import setelah konfirmasi.</p>
            </div>
            <label className="v-input">
              File CSV
              <input type="file" accept=".csv" onChange={(event) => handleCsvPreview(event.target.files?.[0])} />
            </label>
          </div>

          {csvPreview && (
            <div className="import-grid">
              <div className="import-card">
                <h3>1. Ringkasan File</h3>
                <p><strong>{csvFile?.name}</strong></p>
                <p>{csvPreview.totalRows} baris data ditemukan.</p>
                <div className="pill-row">
                  {csvPreview.headers.map((header) => <span className="pill" key={header}>{header}</span>)}
                </div>
              </div>

              <div className="import-card">
                <h3>2. Mode Import</h3>
                <label>Mode
                  <select value={importMode} onChange={(event) => setImportMode(event.target.value)}>
                    <option value="replace">Replace semua data lama</option>
                    <option value="upsert">Tambah/update data</option>
                  </select>
                </label>
                <label>Jumlah kriteria
                  <input type="number" min="1" value={criterionCount} onChange={(event) => changeCriterionCount(event.target.value)} />
                </label>
              </div>

              <div className="import-card">
                <h3>3. Mapping Alternatif</h3>
                <label>Kolom kode alternatif utama
                  <ColumnSelect headers={csvPreview.headers} value={importAlternativeCodeColumn} onChange={setImportAlternativeCodeColumn} />
                </label>
                <label>Kolom kode tambahan opsional
                  <ColumnSelect headers={csvPreview.headers} value={importAlternativeCodeColumn2} onChange={setImportAlternativeCodeColumn2} allowEmptyLabel="Tidak pakai" />
                </label>
                <label>Kolom nama alternatif
                  <ColumnSelect headers={csvPreview.headers} value={importAlternativeNameColumn} onChange={setImportAlternativeNameColumn} />
                </label>
              </div>
            </div>
          )}

          {csvPreview && (
            <div className="import-card full-width">
              <h3>4. Mapping Kriteria</h3>
              <div className="criteria-mapping-grid">
                {importCriteria.map((criterion, index) => (
                  <div className="criterion-map" key={index}>
                    <h4>{criterion.code}</h4>
                    <label>Kode
                      <input value={criterion.code} onChange={(event) => updateImportCriterion(index, "code", event.target.value)} />
                    </label>
                    <label>Nama
                      <input value={criterion.name} onChange={(event) => updateImportCriterion(index, "name", event.target.value)} placeholder="Nama kriteria" />
                    </label>
                    <label>Bobot
                      <input type="number" step="0.01" value={criterion.weight} onChange={(event) => updateImportCriterion(index, "weight", event.target.value)} placeholder="0.15 atau 15" />
                    </label>
                    <label>Tipe
                      <select value={criterion.type} onChange={(event) => updateImportCriterion(index, "type", event.target.value)}>
                        <option value="cost">Cost</option>
                        <option value="benefit">Benefit</option>
                      </select>
                    </label>
                    <label>Kolom nilai
                      <ColumnSelect headers={csvPreview.headers} value={criterion.valueColumn} onChange={(value) => updateImportCriterion(index, "valueColumn", value)} />
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {csvPreview && (
            <div className="import-card full-width">
              <h3>5. Preview dan Konfirmasi</h3>
              <DataTable headers={csvPreview.headers} rows={csvPreview.sampleRows.map((row) => csvPreview.headers.map((header) => row[header]))} />
              <div className="button-row import-actions">
                <button type="button" onClick={commitImport}>Konfirmasi Import CSV</button>
                <button type="button" className="muted" onClick={() => { setCsvFile(null); setCsvPreview(null); setImportResult(null); }}>Reset Upload</button>
              </div>
            </div>
          )}

          {importResult && (
            <div className="notice">
              {importResult.message}: {importResult.alternatives} alternatif, {importResult.criteria} kriteria, {importResult.scores_created} scores baru, {importResult.scores_updated} scores update.
            </div>
          )}
        </section>
      )}

      {activeSection === "vikor" && (
        <section className="panel full-width">
          <div className="calc-header">
            <div>
              <h2>Perhitungan VIKOR</h2>
              <p>Q terbesar menjadi rank 1 dan prioritas perbaikan paling kritis.</p>
            </div>
            <label className="v-input">
              Nilai v
              <input
                type="number"
                min="0"
                max="1"
                step="0.1"
                value={vValue}
                onChange={(e) => setVValue(e.target.value)}
              />
            </label>
            <button onClick={calculate}>Hitung VIKOR</button>
          </div>
          {ranking && (
            <div className="search-box">
              <label>
                Cari hasil ranking
                <input
                  value={vikorSearch}
                  onChange={(e) => setVikorSearch(e.target.value)}
                  placeholder="Cari rank, kode, nama, S, R, atau Q"
                />
              </label>
              <span>
                {filteredRanking.length} dari {ranking.ranking.length} hasil
              </span>
            </div>
          )}
          {ranking && (
            <DataTable
              headers={["Rank", "Alternatif", "S", "R", "Q"]}
              rows={filteredRanking.map((item) => [
                item.rank,
                `${item.alternative_code} - ${item.alternative_name}`,
                format(item.S),
                format(item.R),
                format(item.Q),
              ])}
              rowClassName={(row) => getRankClass(row[0])}
            />
          )}
          {compromise && (
            <div className="result-card">
              <h3>Compromise Solution</h3>
              <div className="status-grid">
                <div className="status-chip">
                  <span>Acceptable advantage</span>
                  <strong>{String(compromise.acceptable_advantage)}</strong>
                </div>
                <div className="status-chip">
                  <span>Acceptable stability</span>
                  <strong>{String(compromise.acceptable_stability)}</strong>
                </div>
              </div>
              <DataTable
                headers={["Ranking", "ID Alternatif", "Nilai S", "Nilai R", "Nilai Q", "Status"]}
                rows={compromise.compromise_solutions.map((item) => [
                  item.rank,
                  `${item.alternative_code} - ${item.alternative_name}`,
                  format(item.S),
                  format(item.R),
                  format(item.Q),
                  getCompromiseStatus(item.rank),
                ])}
                rowClassName={(row) => getRankClass(row[0])}
              />
            </div>
          )}
          {calculation && (
            <details>
              <summary>Detail normalisasi</summary>
              <pre>{JSON.stringify(calculation.results, null, 2)}</pre>
            </details>
          )}
        </section>
      )}
    </main>
  );
}

function Actions({ onEdit, onDelete }) {
  return (
    <div className="actions">
      <button onClick={onEdit}>Edit</button>
      <button className="danger" onClick={onDelete}>
        Hapus
      </button>
    </div>
  );
}

function ColumnSelect({ headers, value, onChange, allowEmptyLabel = "Pilih kolom" }) {
  return (
    <select value={value} onChange={(event) => onChange(event.target.value)}>
      <option value="">{allowEmptyLabel}</option>
      {headers.map((header) => (
        <option key={header} value={header}>{header}</option>
      ))}
    </select>
  );
}

function DataTable({ headers, rows, rowClassName }) {
  const [pageSize, setPageSize] = useState(10);
  const [page, setPage] = useState(1);
  const totalPages = Math.max(1, Math.ceil(rows.length / pageSize));
  const safePage = Math.min(page, totalPages);
  const startIndex = (safePage - 1) * pageSize;
  const visibleRows = rows.slice(startIndex, startIndex + pageSize);
  const startItem = rows.length ? startIndex + 1 : 0;
  const endItem = Math.min(startIndex + pageSize, rows.length);

  useEffect(() => {
    setPage((currentPage) => Math.min(currentPage, totalPages));
  }, [rows.length, totalPages]);

  return (
    <div className="table-wrap panel">
      <TableControls
        pageSize={pageSize}
        setPageSize={setPageSize}
        page={safePage}
        setPage={setPage}
        totalPages={totalPages}
        startItem={startItem}
        endItem={endItem}
        totalItems={rows.length}
      />
      <table>
        <thead>
          <tr>
            {headers.map((header) => (
              <th key={header}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length ? (
            visibleRows.map((row, index) => (
              <tr key={index} className={rowClassName ? rowClassName(row, index) : undefined}>
                {row.map((cell, cellIndex) => (
                  <td key={cellIndex}>{cell}</td>
                ))}
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={headers.length}>Data masih kosong.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

function getRankClass(rank) {
  const numericRank = Number(rank);
  return numericRank >= 1 && numericRank <= 5 ? `rank-highlight rank-${numericRank}` : undefined;
}

function getCompromiseStatus(rank) {
  const numericRank = Number(rank);
  if (numericRank === 1) return "Prioritas utama";
  if (numericRank >= 2 && numericRank <= 5) return "Prioritas tinggi";
  return "Kandidat kompromi";
}

function MatrixTable({ matrix, criteria }) {
  const [pageSize, setPageSize] = useState(10);
  const [page, setPage] = useState(1);
  const totalPages = Math.max(1, Math.ceil(matrix.length / pageSize));
  const safePage = Math.min(page, totalPages);
  const startIndex = (safePage - 1) * pageSize;
  const visibleRows = matrix.slice(startIndex, startIndex + pageSize);
  const startItem = matrix.length ? startIndex + 1 : 0;
  const endItem = Math.min(startIndex + pageSize, matrix.length);

  useEffect(() => {
    setPage((currentPage) => Math.min(currentPage, totalPages));
  }, [matrix.length, totalPages]);

  return (
    <section className="panel full-width">
      <h2>Matrix Scores</h2>
      <TableControls
        pageSize={pageSize}
        setPageSize={setPageSize}
        page={safePage}
        setPage={setPage}
        totalPages={totalPages}
        startItem={startItem}
        endItem={endItem}
        totalItems={matrix.length}
      />
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Alternatif</th>
              {criteria.map((criterion) => (
                <th key={criterion.id}>{criterion.code}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {matrix.length ? (
              visibleRows.map((row) => (
                <tr key={row.alternative_id}>
                  <td>
                    {row.alternative_code} - {row.alternative_name}
                  </td>
                  {row.scores.map((score) => (
                    <td key={score.criterion_id}>{score.value ?? "-"}</td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={criteria.length + 1}>Matrix masih kosong.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function TableControls({ pageSize, setPageSize, page, setPage, totalPages, startItem, endItem, totalItems }) {
  return (
    <div className="table-controls">
      <label>
        Tampilkan
        <select
          value={pageSize}
          onChange={(event) => {
            setPageSize(Number(event.target.value));
            setPage(1);
          }}
        >
          {pageSizeOptions.map((option) => (
            <option key={option} value={option}>
              {option} baris
            </option>
          ))}
        </select>
      </label>
      <span className="table-range">
        Menampilkan {startItem}-{endItem} dari {totalItems} data
      </span>
      <div className="pager-buttons">
        <button type="button" onClick={() => setPage((currentPage) => Math.max(1, currentPage - 1))} disabled={page <= 1}>
          Prev
        </button>
        <span>
          {page} / {totalPages}
        </span>
        <button type="button" onClick={() => setPage((currentPage) => Math.min(totalPages, currentPage + 1))} disabled={page >= totalPages}>
          Next
        </button>
      </div>
    </div>
  );
}

function format(value) {
  return Number(value).toFixed(4);
}

export default App;
