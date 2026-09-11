-- ============================================================
-- Migration 002: Views Agregadas de Indicadores de Matrícula
-- Projeto: PEDFOR Dashboard de Matrículas
-- ============================================================

-- 1. View Resumo dos KPIs Principais de Matrícula
CREATE OR REPLACE VIEW vw_kpi_matriculas AS
SELECT 
    COUNT(*) AS total_matriculas,
    COUNT(DISTINCT cursista_email) AS total_cursistas_unicos,
    COUNT(DISTINCT turma_id) AS total_turmas,
    COUNT(DISTINCT turma_formador) AS total_formadores,
    SUM(CASE WHEN status_email = 'enviado' THEN 1 ELSE 0 END) AS emails_enviados,
    SUM(CASE WHEN status_email = 'pendente' THEN 1 ELSE 0 END) AS emails_pendentes,
    ROUND(
        (SUM(CASE WHEN status_email = 'enviado' THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(*), 0),
        2
    ) AS taxa_envio_email_pct
FROM matriculas_pedfor;

-- 2. View Agregada por Turma e Formador
CREATE OR REPLACE VIEW vw_matriculas_por_turma AS
SELECT 
    turma_id,
    turma_nome,
    turma_formador,
    turma_dia,
    turma_horario,
    COUNT(*) AS total_cursistas,
    SUM(CASE WHEN status_email = 'enviado' THEN 1 ELSE 0 END) AS emails_enviados,
    ROUND(
        (SUM(CASE WHEN status_email = 'enviado' THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(*), 0),
        2
    ) AS taxa_confirmacao_pct
FROM matriculas_pedfor
GROUP BY turma_id, turma_nome, turma_formador, turma_dia, turma_horario
ORDER BY total_cursistas DESC;

-- 3. View Agregada por Formador (Ranking de Ocupação)
CREATE OR REPLACE VIEW vw_ranking_formadores AS
SELECT 
    turma_formador AS formador,
    COUNT(DISTINCT turma_id) AS qtd_turmas,
    COUNT(*) AS total_cursistas_atendidos,
    SUM(CASE WHEN status_email = 'enviado' THEN 1 ELSE 0 END) AS confirmados
FROM matriculas_pedfor
GROUP BY turma_formador
ORDER BY total_cursistas_atendidos DESC;

-- 4. View Agregada por Dia da Semana e Horário
CREATE OR REPLACE VIEW vw_distribuicao_dia_horario AS
SELECT 
    turma_dia AS dia_semana,
    turma_horario AS horario,
    COUNT(*) AS total_matriculas
FROM matriculas_pedfor
GROUP BY turma_dia, turma_horario
ORDER BY total_matriculas DESC;
