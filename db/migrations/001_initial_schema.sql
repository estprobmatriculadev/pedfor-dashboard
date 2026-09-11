-- ============================================================
-- Migration 001: Initial Schema para TiDB (MySQL 8.0 Compatible)
-- Projeto: PEDFOR Dashboard
-- ============================================================

CREATE TABLE IF NOT EXISTS unidades (
    id VARCHAR(36) PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    codigo VARCHAR(50) UNIQUE,
    uf VARCHAR(2) DEFAULT 'PR',
    ativo TINYINT(1) DEFAULT 1,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS categorias (
    id VARCHAR(36) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao VARCHAR(255),
    ativo TINYINT(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS registros_pedfor (
    id VARCHAR(36) PRIMARY KEY,
    unidade_id VARCHAR(36) NOT NULL,
    categoria_id VARCHAR(36) NOT NULL,
    data_registro DATE NOT NULL,
    responsavel VARCHAR(150),
    status VARCHAR(50) NOT NULL DEFAULT 'pendente', -- 'pendente', 'em_andamento', 'concluido', 'cancelado'
    valor DECIMAL(15,2) DEFAULT 0.00,
    qtd_itens INT DEFAULT 1,
    observacoes TEXT,
    qualidade_flag VARCHAR(50) DEFAULT 'valido', -- 'valido', 'incompleto', 'duplicado_suspeito'
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_pedfor_unidade FOREIGN KEY (unidade_id) REFERENCES unidades(id) ON DELETE RESTRICT,
    CONSTRAINT fk_pedfor_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Índices otimizados para filtros de dashboard no TiDB
CREATE INDEX idx_pedfor_data ON registros_pedfor(data_registro);
CREATE INDEX idx_pedfor_status ON registros_pedfor(status);
CREATE INDEX idx_pedfor_unidade_data ON registros_pedfor(unidade_id, data_registro);
CREATE INDEX idx_pedfor_categoria_data ON registros_pedfor(categoria_id, data_registro);

-- Tabela de Auditoria de Qualidade de Dados
CREATE TABLE IF NOT EXISTS auditoria_qualidade (
    id VARCHAR(36) PRIMARY KEY,
    data_verificacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_registros INT NOT NULL,
    registros_nulos INT DEFAULT 0,
    duplicados_detectados INT DEFAULT 0,
    datas_invalidas INT DEFAULT 0,
    score_qualidade DECIMAL(5,2) DEFAULT 100.00,
    detalhes JSON
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
