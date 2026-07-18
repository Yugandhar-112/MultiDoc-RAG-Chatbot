import { useRef, useState } from 'react'

const ACCEPTED = '.pdf,.txt,.docx'

export default function UploadPanel({ documents, onUpload, isUploading, error }) {
  const inputRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)

  function handleFiles(fileList) {
    const files = Array.from(fileList)
    if (files.length > 0) onUpload(files)
  }

  return (
    <aside className="panel">
      <div className="panel-header">
        <span className="panel-eyebrow">Index</span>
        <h1 className="panel-title">Docs Chat</h1>
        <p className="panel-subtitle">
          Upload sources, then ask questions grounded in exactly what they say.
        </p>
      </div>

      <div
        className={`dropzone ${isDragging ? 'dropzone-active' : ''}`}
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setIsDragging(false)
          handleFiles(e.dataTransfer.files)
        }}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click()
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED}
          multiple
          hidden
          onChange={(e) => {
            handleFiles(e.target.files)
            e.target.value = ''
          }}
        />
        <div className="dropzone-icon">＋</div>
        <div className="dropzone-text">
          {isUploading ? 'Reading documents…' : 'Drop PDF, DOCX, or TXT files'}
        </div>
        <div className="dropzone-hint">or click to browse</div>
      </div>

      {error && <div className="upload-error">{error}</div>}

      <div className="document-list">
        <span className="panel-eyebrow" style={{ marginTop: 4 }}>
          {documents.length === 0 ? 'No sources yet' : `${documents.length} source${documents.length === 1 ? '' : 's'}`}
        </span>
        {documents.map((doc) => (
          <div className="document-card" key={doc.doc_id}>
            <div className="document-card-name">{doc.filename}</div>
            <div className="document-card-meta">
              {doc.num_chunks} chunk{doc.num_chunks === 1 ? '' : 's'}
              {doc.num_pages ? ` · ${doc.num_pages} page${doc.num_pages === 1 ? '' : 's'}` : ''}
            </div>
          </div>
        ))}
      </div>
    </aside>
  )
}
