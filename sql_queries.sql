-- SQL Queries for Classic Models Database
-- Generated for PostgreSQL (identifiers use double quotes)

-- ============================================================
-- Queries 1-20: Basic SELECTs
-- ============================================================

-- Q1: List all products
SELECT * FROM "products";

-- Q2: Get all customers
SELECT * FROM "customers";

-- Q3: Show all orders
SELECT * FROM "orders";

-- Q4: List all employees
SELECT * FROM "employees";

-- Q5: Get all offices
SELECT * FROM "offices";

-- Q6: Show all product lines
SELECT * FROM "productlines";

-- Q7: List all payments
SELECT * FROM "payments";

-- Q8: Get product names and prices
SELECT "productName", "buyPrice" FROM "products";

-- Q9: Get customer names and cities
SELECT "customerName", "city" FROM "customers";

-- Q10: List employee first and last names
SELECT "firstName", "lastName" FROM "employees";

-- Q11: Get all order dates
SELECT "orderDate" FROM "orders";

-- Q12: Show product vendor list
SELECT "productVendor" FROM "products";

-- Q13: Get all product codes
SELECT "productCode" FROM "products";

-- Q14: List all countries from offices
SELECT "country" FROM "offices";

-- Q15: Show all order statuses
SELECT "status" FROM "orders";

-- Q16: Get all payment amounts
SELECT "amount" FROM "payments";

-- Q17: List all job titles
SELECT "jobTitle" FROM "employees";

-- Q18: Get customer phone numbers
SELECT "phone" FROM "customers";

-- Q19: Show product MSRP values
SELECT "MSRP" FROM "products";

-- Q20: List order numbers
SELECT "orderNumber" FROM "orders";

-- ============================================================
-- Queries 21-30: JOINs
-- ============================================================

-- Q21: Get orders with customer names
SELECT o.*, c."customerName"
FROM "orders" o
JOIN "customers" c ON o."customerNumber" = c."customerNumber";

-- Q22: Get employees with office city
SELECT e.*, o."city" AS "officeCity"
FROM "employees" e
JOIN "offices" o ON e."officeCode" = o."officeCode";

-- Q23: Get payments with customer names
SELECT p.*, c."customerName"
FROM "payments" p
JOIN "customers" c ON p."customerNumber" = c."customerNumber";

-- Q24: Get order details with product names
SELECT od.*, p."productName"
FROM "orderdetails" od
JOIN "products" p ON od."productCode" = p."productCode";

-- Q25: Get products with product line description
SELECT p.*, pl."textDescription"
FROM "products" p
JOIN "productlines" pl ON p."productLine" = pl."productLine";

-- Q26: Get customers with sales rep names
SELECT c.*, CONCAT(e."firstName", ' ', e."lastName") AS "salesRepName"
FROM "customers" c
LEFT JOIN "employees" e ON c."salesRepEmployeeNumber" = e."employeeNumber";

-- Q27: Get orders with customer city
SELECT o.*, c."city" AS "customerCity"
FROM "orders" o
JOIN "customers" c ON o."customerNumber" = c."customerNumber";

-- Q28: Get employees and their manager
SELECT e.*, CONCAT(m."firstName", ' ', m."lastName") AS "managerName"
FROM "employees" e
LEFT JOIN "employees" m ON e."reportsTo" = m."employeeNumber";

-- Q29: Get orderdetails with product vendor
SELECT od.*, p."productVendor"
FROM "orderdetails" od
JOIN "products" p ON od."productCode" = p."productCode";

-- Q30: Get payments with customer country
SELECT p.*, c."country" AS "customerCountry"
FROM "payments" p
JOIN "customers" c ON p."customerNumber" = c."customerNumber";

-- ============================================================
-- Queries 31-40: GROUP BY with Aggregates
-- ============================================================

-- Q31: Count customers per country
SELECT "country", COUNT(*) AS "customerCount"
FROM "customers"
GROUP BY "country";

-- Q32: Total payments per customer
SELECT "customerNumber", SUM("amount") AS "totalPayments"
FROM "payments"
GROUP BY "customerNumber";

-- Q33: Number of orders per status
SELECT "status", COUNT(*) AS "orderCount"
FROM "orders"
GROUP BY "status";

-- Q34: Products per product line
SELECT "productLine", COUNT(*) AS "productCount"
FROM "products"
GROUP BY "productLine";

-- Q35: Employees per office
SELECT "officeCode", COUNT(*) AS "employeeCount"
FROM "employees"
GROUP BY "officeCode";

-- Q36: Total stock per product vendor
SELECT "productVendor", SUM("quantityInStock") AS "totalStock"
FROM "products"
GROUP BY "productVendor";

-- Q37: Average buy price per product line
SELECT "productLine", AVG("buyPrice") AS "avgBuyPrice"
FROM "products"
GROUP BY "productLine";

-- Q38: Orders per customer
SELECT "customerNumber", COUNT(*) AS "orderCount"
FROM "orders"
GROUP BY "customerNumber";

-- Q39: Max MSRP per product line
SELECT "productLine", MAX("MSRP") AS "maxMSRP"
FROM "products"
GROUP BY "productLine";

-- Q40: Min buy price per vendor
SELECT "productVendor", MIN("buyPrice") AS "minBuyPrice"
FROM "products"
GROUP BY "productVendor";

-- ============================================================
-- Queries 41-50: Scalar Aggregates
-- ============================================================

-- Q41: Total number of customers
SELECT COUNT(*) AS "totalCustomers" FROM "customers";

-- Q42: Total number of products
SELECT COUNT(*) AS "totalProducts" FROM "products";

-- Q43: Total revenue from payments
SELECT SUM("amount") AS "totalRevenue" FROM "payments";

-- Q44: Average product price
SELECT AVG("buyPrice") AS "avgProductPrice" FROM "products";

-- Q45: Max payment amount
SELECT MAX("amount") AS "maxPayment" FROM "payments";

-- Q46: Min payment amount
SELECT MIN("amount") AS "minPayment" FROM "payments";

-- Q47: Count total orders
SELECT COUNT(*) AS "totalOrders" FROM "orders";

-- Q48: Total quantity in stock
SELECT SUM("quantityInStock") AS "totalStock" FROM "products";

-- Q49: Average MSRP
SELECT AVG("MSRP") AS "avgMSRP" FROM "products";

-- Q50: Number of employees
SELECT COUNT(*) AS "totalEmployees" FROM "employees";
