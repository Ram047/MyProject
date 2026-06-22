-- 1. Total companies
SELECT COUNT(*) AS total_companies
FROM companies;

-- 2. Top 10 companies by ROE
SELECT id, company_name, roe_percentage
FROM companies
ORDER BY roe_percentage DESC
LIMIT 10;

-- 3. Companies with highest ROCE
SELECT id, company_name, roce_percentage
FROM companies
ORDER BY roce_percentage DESC
LIMIT 10;

-- 4. Total stock price records
SELECT COUNT(*) AS stock_records
FROM stock_prices;

-- 5. Average closing price by company
SELECT company_id,
AVG(close_price) AS avg_close_price
FROM stock_prices
GROUP BY company_id
ORDER BY avg_close_price DESC;

-- 6. Companies by sector
SELECT broad_sector,
COUNT(*) AS total
FROM sectors
GROUP BY broad_sector;

-- 7. Companies with highest market cap
SELECT company_id,
market_cap_crore
FROM market_cap
ORDER BY market_cap_crore DESC
LIMIT 10;

-- 8. Balance sheet record count
SELECT company_id,
COUNT(*) AS years
FROM balancesheet
GROUP BY company_id
ORDER BY years DESC;

-- 9. Companies with less than 5 years of data
SELECT company_id,
COUNT(*) AS years
FROM balancesheet
GROUP BY company_id
HAVING COUNT(*) < 5;

-- 10. Total documents available
SELECT COUNT(*)
FROM documents;