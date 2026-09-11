-- ============================================================
-- Migration 001: Schema Consolidado de Matrículas PEDFOR (TiDB)
-- Projeto: PEDFOR Dashboard de Matrículas e Frequência
-- ============================================================

CREATE TABLE IF NOT EXISTS matriculas_pedfor (
    id VARCHAR(36) PRIMARY KEY,
    cgm VARCHAR(50),
    cursista_nome VARCHAR(255) NOT NULL,
    cursista_email VARCHAR(255) NOT NULL,
    nre VARCHAR(100) DEFAULT 'NRE CURITIBA',
    turma_id VARCHAR(36) NOT NULL,
    turma_nome VARCHAR(150) NOT NULL,
    turma_formador VARCHAR(150) NOT NULL,
    tutora VARCHAR(150) NOT NULL,
    turma_dia VARCHAR(50) NOT NULL,
    turma_horario VARCHAR(50) NOT NULL,
    periodo_turno VARCHAR(50) NOT NULL, -- 'Manhã', 'Tarde', 'Noite'
    situacao VARCHAR(50) NOT NULL DEFAULT 'Matriculado', -- 'Matriculado', 'Remanejado', 'Desistente'
    frequencia_pct DECIMAL(5,2) DEFAULT 100.00,
    status_email VARCHAR(50) DEFAULT 'enviado',
    data_confirmacao DATETIME,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Índices de alta performance
CREATE INDEX idx_matriculas_turma ON matriculas_pedfor(turma_id);
CREATE INDEX idx_matriculas_formador ON matriculas_pedfor(turma_formador);
CREATE INDEX idx_matriculas_nre ON matriculas_pedfor(nre);
CREATE INDEX idx_matriculas_situacao ON matriculas_pedfor(situacao);
CREATE INDEX idx_matriculas_dia ON matriculas_pedfor(turma_dia);
CREATE INDEX idx_matriculas_turno ON matriculas_pedfor(periodo_turno);
