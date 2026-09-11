-- ============================================================
-- Migration 001: Schema Real de Matrículas PEDFOR para TiDB
-- Projeto: PEDFOR Dashboard de Matrículas
-- ============================================================

-- 1. Tabela Principal de Matrículas
CREATE TABLE IF NOT EXISTS matriculas_pedfor (
    id VARCHAR(36) PRIMARY KEY,
    cursista_id VARCHAR(255) NOT NULL,
    cursista_nome VARCHAR(255) NOT NULL,
    cursista_email VARCHAR(255) NOT NULL,
    turma_id VARCHAR(36) NOT NULL,
    turma_nome VARCHAR(150) NOT NULL,
    turma_formador VARCHAR(150) NOT NULL,
    turma_dia VARCHAR(50) NOT NULL,
    turma_horario VARCHAR(50) NOT NULL,
    vaga_id VARCHAR(36) NOT NULL,
    data_confirmacao DATETIME NOT NULL,
    status_email VARCHAR(50) DEFAULT 'pendente', -- 'enviado', 'pendente'
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Índices de alta performance para buscas e agregações
CREATE INDEX idx_matriculas_turma ON matriculas_pedfor(turma_id);
CREATE INDEX idx_matriculas_formador ON matriculas_pedfor(turma_formador);
CREATE INDEX idx_matriculas_dia ON matriculas_pedfor(turma_dia);
CREATE INDEX idx_matriculas_status_email ON matriculas_pedfor(status_email);
CREATE INDEX idx_matriculas_data_conf ON matriculas_pedfor(data_confirmacao);
