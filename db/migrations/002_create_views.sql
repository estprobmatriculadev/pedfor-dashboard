-- ============================================================
-- Migration 002: Views Agregadas de Matrícula, NRE e Frequência
-- Projeto: PEDFOR Dashboard
-- ============================================================

-- 1. View KPI Geral de Matrículas e Frequência
CREATE OR REPLACE VIEW vw_kpi_matriculas AS
SELECT 
    COUNT(*) AS total_inscritos,
    SUM(CASE WHEN situacao = 'Matriculado' THEN 1 ELSE 0 END) AS total_matriculados,
    SUM(CASE WHEN situacao = 'Remanejado' THEN 1 ELSE 0 END) AS total_remanejados,
    SUM(CASE WHEN situacao = 'Desistente' THEN 1 ELSE 0 END) AS total_desistentes,
    COUNT(DISTINCT turma_id) AS total_turmas,
    COUNT(DISTINCT turma_formador) AS total_formadores,
    COUNT(DISTINCT nre) AS total_nres,
    ROUND(AVG(frequencia_pct), 2) AS frequencia_media_pct
FROM matriculas_pedfor;

-- 2. View Agregada por Formador / Tutora
CREATE OR REPLACE VIEW vw_cursistas_por_formador AS
SELECT 
    turma_formador AS formador,
    COUNT(DISTINCT turma_id) AS qtd_turmas,
    COUNT(*) AS total_cursistas,
    SUM(CASE WHEN situacao = 'Matriculado' THEN 1 ELSE 0 END) AS matriculados,
    SUM(CASE WHEN situacao = 'Remanejado' THEN 1 ELSE 0 END) AS remanejados,
    SUM(CASE WHEN situacao = 'Desistente' THEN 1 ELSE 0 END) AS desistentes,
    ROUND(AVG(frequencia_pct), 2) AS frequencia_media_pct
FROM matriculas_pedfor
GROUP BY turma_formador
ORDER BY total_cursistas DESC;

-- 3. View Agregada por NRE
CREATE OR REPLACE VIEW vw_cursistas_por_nre AS
SELECT 
    nre,
    COUNT(*) AS total_cursistas,
    SUM(CASE WHEN situacao = 'Matriculado' THEN 1 ELSE 0 END) AS matriculados,
    SUM(CASE WHEN situacao = 'Remanejado' THEN 1 ELSE 0 END) AS remanejados,
    SUM(CASE WHEN situacao = 'Desistente' THEN 1 ELSE 0 END) AS desistentes
FROM matriculas_pedfor
GROUP BY nre
ORDER BY total_cursistas DESC;
