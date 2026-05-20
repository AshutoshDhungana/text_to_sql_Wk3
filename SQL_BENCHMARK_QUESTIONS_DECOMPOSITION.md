# SQL Benchmark Questions - Structured Decomposition

---

## Question 1: List all products
- **Intent:** List all rows
- **Tables:** products
- **Columns:** *
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 2: Get all customers
- **Intent:** List all rows
- **Tables:** customers
- **Columns:** *
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 3: Show all orders
- **Intent:** List all rows
- **Tables:** orders
- **Columns:** *
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 4: List all employees
- **Intent:** List all rows
- **Tables:** employees
- **Columns:** *
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 5: Get all offices
- **Intent:** List all rows
- **Tables:** offices
- **Columns:** *
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 6: Show all product lines
- **Intent:** List all rows
- **Tables:** productlines
- **Columns:** *
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 7: List all payments
- **Intent:** List all rows
- **Tables:** payments
- **Columns:** *
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 8: Get product names and prices
- **Intent:** List specific columns
- **Tables:** products
- **Columns:** productName, buyPrice
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 9: Get customer names and cities
- **Intent:** List specific columns
- **Tables:** customers
- **Columns:** customerName, city
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 10: List employee first and last names
- **Intent:** List specific columns
- **Tables:** employees
- **Columns:** firstName, lastName
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 11: Get all order dates
- **Intent:** List specific columns
- **Tables:** orders
- **Columns:** orderDate
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 12: Show product vendor list
- **Intent:** List specific columns
- **Tables:** products
- **Columns:** productVendor
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 13: Get all product codes
- **Intent:** List specific columns
- **Tables:** products
- **Columns:** productCode
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 14: List all countries from offices
- **Intent:** List specific columns
- **Tables:** offices
- **Columns:** country
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 15: Show all order statuses
- **Intent:** List specific columns
- **Tables:** orders
- **Columns:** status
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 16: Get all payment amounts
- **Intent:** List specific columns
- **Tables:** payments
- **Columns:** amount
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 17: List all job titles
- **Intent:** List specific columns
- **Tables:** employees
- **Columns:** jobTitle
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 18: Get customer phone numbers
- **Intent:** List specific columns
- **Tables:** customers
- **Columns:** phone
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 19: Show product MSRP values
- **Intent:** List specific columns
- **Tables:** products
- **Columns:** MSRP
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 20: List order numbers
- **Intent:** List specific columns
- **Tables:** orders
- **Columns:** orderNumber
- **Filters:** None
- **Joins:** None
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 21: Get orders with customer names
- **Intent:** Join and list columns from multiple tables
- **Tables:** orders, customers
- **Columns:** orders.*, customers.customerName
- **Filters:** None
- **Joins:** orders.customerNumber = customers.customerNumber
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 22: Get employees with office city
- **Intent:** Join and list columns from multiple tables
- **Tables:** employees, offices
- **Columns:** employees.*, offices.city
- **Filters:** None
- **Joins:** employees.officeCode = offices.officeCode
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 23: Get payments with customer names
- **Intent:** Join and list columns from multiple tables
- **Tables:** payments, customers
- **Columns:** payments.*, customers.customerName
- **Filters:** None
- **Joins:** payments.customerNumber = customers.customerNumber
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 24: Get order details with product names
- **Intent:** Join and list columns from multiple tables
- **Tables:** orderdetails, products
- **Columns:** orderdetails.*, products.productName
- **Filters:** None
- **Joins:** orderdetails.productCode = products.productCode
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 25: Get products with product line description
- **Intent:** Join and list columns from multiple tables
- **Tables:** products, productlines
- **Columns:** products.*, productlines.textDescription
- **Filters:** None
- **Joins:** products.productLine = productlines.productLine
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 26: Get customers with sales rep names
- **Intent:** Join and list columns from multiple tables
- **Tables:** customers, employees
- **Columns:** customers.*, employees.firstName, employees.lastName
- **Filters:** None
- **Joins:** customers.salesRepEmployeeNumber = employees.employeeNumber
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 27: Get orders with customer city
- **Intent:** Join and list columns from multiple tables
- **Tables:** orders, customers
- **Columns:** orders.*, customers.city
- **Filters:** None
- **Joins:** orders.customerNumber = customers.customerNumber
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 28: Get employees and their manager
- **Intent:** Self-join to show hierarchical relationship
- **Tables:** employees (alias e1), employees (alias e2)
- **Columns:** e1.*, e2.firstName AS managerFirstName, e2.lastName AS managerLastName
- **Filters:** None
- **Joins:** e1.reportsTo = e2.employeeNumber
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 29: Get orderdetails with product vendor
- **Intent:** Join and list columns from multiple tables
- **Tables:** orderdetails, products
- **Columns:** orderdetails.*, products.productVendor
- **Filters:** None
- **Joins:** orderdetails.productCode = products.productCode
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 30: Get payments with customer country
- **Intent:** Join and list columns from multiple tables
- **Tables:** payments, customers
- **Columns:** payments.*, customers.country
- **Filters:** None
- **Joins:** payments.customerNumber = customers.customerNumber
- **Aggregation:** None
- **Sort/Limit:** None

---

## Question 31: Count customers per country
- **Intent:** Aggregate and count
- **Tables:** customers
- **Columns:** country, COUNT(*)
- **Filters:** None
- **Joins:** None
- **Aggregation:** GROUP BY country
- **Sort/Limit:** None

---

## Question 32: Total payments per customer
- **Intent:** Aggregate and sum
- **Tables:** payments
- **Columns:** customerNumber, SUM(amount)
- **Filters:** None
- **Joins:** None
- **Aggregation:** GROUP BY customerNumber
- **Sort/Limit:** None

---

## Question 33: Number of orders per status
- **Intent:** Aggregate and count
- **Tables:** orders
- **Columns:** status, COUNT(*)
- **Filters:** None
- **Joins:** None
- **Aggregation:** GROUP BY status
- **Sort/Limit:** None

---

## Question 34: Products per product line
- **Intent:** Aggregate and count
- **Tables:** products
- **Columns:** productLine, COUNT(*)
- **Filters:** None
- **Joins:** None
- **Aggregation:** GROUP BY productLine
- **Sort/Limit:** None

---

## Question 35: Employees per office
- **Intent:** Aggregate and count
- **Tables:** employees
- **Columns:** officeCode, COUNT(*)
- **Filters:** None
- **Joins:** None
- **Aggregation:** GROUP BY officeCode
- **Sort/Limit:** None

---

## Question 36: Total stock per product vendor
- **Intent:** Aggregate and sum
- **Tables:** products
- **Columns:** productVendor, SUM(quantityInStock)
- **Filters:** None
- **Joins:** None
- **Aggregation:** GROUP BY productVendor
- **Sort/Limit:** None

---

## Question 37: Average buy price per product line
- **Intent:** Aggregate and average
- **Tables:** products
- **Columns:** productLine, AVG(buyPrice)
- **Filters:** None
- **Joins:** None
- **Aggregation:** GROUP BY productLine
- **Sort/Limit:** None

---

## Question 38: Orders per customer
- **Intent:** Aggregate and count
- **Tables:** orders
- **Columns:** customerNumber, COUNT(*)
- **Filters:** None
- **Joins:** None
- **Aggregation:** GROUP BY customerNumber
- **Sort/Limit:** None

---

## Question 39: Max MSRP per product line
- **Intent:** Aggregate and find maximum
- **Tables:** products
- **Columns:** productLine, MAX(MSRP)
- **Filters:** None
- **Joins:** None
- **Aggregation:** GROUP BY productLine
- **Sort/Limit:** None

---

## Question 40: Min buy price per vendor
- **Intent:** Aggregate and find minimum
- **Tables:** products
- **Columns:** productVendor, MIN(buyPrice)
- **Filters:** None
- **Joins:** None
- **Aggregation:** GROUP BY productVendor
- **Sort/Limit:** None

---

## Question 41: Total number of customers
- **Intent:** Simple aggregate count
- **Tables:** customers
- **Columns:** COUNT(*)
- **Filters:** None
- **Joins:** None
- **Aggregation:** COUNT(*)
- **Sort/Limit:** None

---

## Question 42: Total number of products
- **Intent:** Simple aggregate count
- **Tables:** products
- **Columns:** COUNT(*)
- **Filters:** None
- **Joins:** None
- **Aggregation:** COUNT(*)
- **Sort/Limit:** None

---

## Question 43: Total revenue from payments
- **Intent:** Simple aggregate sum
- **Tables:** payments
- **Columns:** SUM(amount)
- **Filters:** None
- **Joins:** None
- **Aggregation:** SUM(amount)
- **Sort/Limit:** None

---

## Question 44: Average product price
- **Intent:** Simple aggregate average
- **Tables:** products
- **Columns:** AVG(buyPrice)
- **Filters:** None
- **Joins:** None
- **Aggregation:** AVG(buyPrice)
- **Sort/Limit:** None

---

## Question 45: Max payment amount
- **Intent:** Simple aggregate maximum
- **Tables:** payments
- **Columns:** MAX(amount)
- **Filters:** None
- **Joins:** None
- **Aggregation:** MAX(amount)
- **Sort/Limit:** None

---

## Question 46: Min payment amount
- **Intent:** Simple aggregate minimum
- **Tables:** payments
- **Columns:** MIN(amount)
- **Filters:** None
- **Joins:** None
- **Aggregation:** MIN(amount)
- **Sort/Limit:** None

---

## Question 47: Count total orders
- **Intent:** Simple aggregate count
- **Tables:** orders
- **Columns:** COUNT(*)
- **Filters:** None
- **Joins:** None
- **Aggregation:** COUNT(*)
- **Sort/Limit:** None

---

## Question 48: Total quantity in stock
- **Intent:** Simple aggregate sum
- **Tables:** products
- **Columns:** SUM(quantityInStock)
- **Filters:** None
- **Joins:** None
- **Aggregation:** SUM(quantityInStock)
- **Sort/Limit:** None

---

## Question 49: Average MSRP
- **Intent:** Simple aggregate average
- **Tables:** products
- **Columns:** AVG(MSRP)
- **Filters:** None
- **Joins:** None
- **Aggregation:** AVG(MSRP)
- **Sort/Limit:** None

---

## Question 50: Number of employees
- **Intent:** Simple aggregate count
- **Tables:** employees
- **Columns:** COUNT(*)
- **Filters:** None
- **Joins:** None
- **Aggregation:** COUNT(*)
- **Sort/Limit:** None