DROP TABLE IF EXISTS cat_reg;

CREATE TABLE cat_reg AS
SELECT
    category,
    ROUND(SUM(CASE WHEN region = 'East' THEN total_price ELSE 0 END))::INT AS east,
    ROUND(SUM(CASE WHEN region = 'West' THEN total_price ELSE 0 END))::INT AS west,
    ROUND(SUM(total_price))::INT                                           AS grand_total
FROM food_sales
GROUP BY category
ORDER BY category;

ALTER TABLE cat_reg ADD PRIMARY KEY (category);