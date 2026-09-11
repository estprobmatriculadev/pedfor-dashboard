-- ============================================================
-- Migration 002: Views Agregadas de Indicadores para TiDB
-- Projeto: PEDFOR Dashboard
-- ============================================================

-- 1. View Resumo dos Principais KPIs
CREATE OR REPLACE VIEW vw_kpi_resumo AS
SELECT 
    COUNT(*) AS total_registros,
    SUM(CASE WHEN status = 'concluido' THEN 1 ELSE 0 END) AS total_concluidos,
    SUM(CASE WHEN status = 'em_andamento' THEN 1 ELSE 0 END) AS total_em_andamento,
    SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END) AS total_pendentes,
    SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END) AS total_cancelados,
    COALESCE(SUM(valor), 0.00) AS valor_total,
    COALESCE(AVG(valor), 0.00) AS valor_medio,
    ROUND(
        (SUM(CASE WHEN status = 'concluido' THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(*), 0),
        2
    ) AS taxa_conclusao_pct
FROM registros_pedfor;

-- 2. View Agregada Temporal (Por Mês) para Gráficos de Tendência
CREATE OR REPLACE VIEW vw_series_temporais AS
SELECT 
    DATE_FORMAT(data_registro, '%Y-%m') AS mes_ano,
    COUNT(*) AS total_pedidos,
    SUM(CASE WHEN status = 'concluido' THEN 1 ELSE 0 END) AS concluidos,
    SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END) AS pendentes,
    COALESCE(SUM(valor), 0.00) AS montante_financeiro
FROM registros_pedfor
GROUP BY DATE_FORMAT(data_registro, '%Y-%m')
ORDER BY mes_ano ASC;

-- 3. View Ranking de Desempenho por Unidade
CREATE OR REPLACE VIEW vw_ranking_unidades AS
SELECT 
    u.id AS unidade_id,
    u.nome AS unidade_nome,
    u.uf,
    COUNT(r.id) AS total_atendimentos,
    SUM(CASE WHEN r.status = 'concluido' THEN 1 ELSE 0 END) AS concluidos,
    COALESCE(SUM(r.valor), 0.00) AS valor_total,
    ROUND(
        (SUM(CASE WHEN r.status = 'concluido' THEN 1 ELSE 0 END) * 100.0) / NULLIF(COUNT(r.id), 0),
        2
    ) AS taxa_eficiencia_pct
FROM unidades u
LEFT JOIN registros_pedfor r ON u.id = r.unidade_id
GROUP BY u.id, u.nome, u.uf
ORDER BY total_atendimentos DESC;
