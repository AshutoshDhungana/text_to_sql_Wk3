"""Database connection and schema introspection module."""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/classicmodels")


def get_connection():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)


SCHEMA = {
    "products": [
        "productCode", "productName", "productLine", "productScale",
        "productVendor", "productDescription", "quantityInStock",
        "buyPrice", "MSRP",
    ],
    "productlines": ["productLine", "textDescription", "htmlDescription", "image"],
    "offices": [
        "officeCode", "city", "phone", "addressLine1", "addressLine2",
        "state", "country", "postalCode", "territory",
    ],
    "employees": [
        "employeeNumber", "lastName", "firstName", "extension",
        "email", "officeCode", "reportsTo", "jobTitle",
    ],
    "customers": [
        "customerNumber", "customerName", "contactLastName",
        "contactFirstName", "phone", "addressLine1", "addressLine2",
        "city", "state", "postalCode", "country",
        "salesRepEmployeeNumber", "creditLimit",
    ],
    "payments": ["customerNumber", "checkNumber", "paymentDate", "amount"],
    "orders": [
        "orderNumber", "orderDate", "requiredDate", "shippedDate",
        "status", "comments", "customerNumber",
    ],
    "orderdetails": [
        "orderNumber", "productCode", "quantityOrdered",
        "priceEach", "orderLineNumber",
    ],
}

PRIMARY_KEYS = {
    "products": "productCode",
    "productlines": "productLine",
    "offices": "officeCode",
    "employees": "employeeNumber",
    "customers": "customerNumber",
    "payments": ("customerNumber", "checkNumber"),
    "orders": "orderNumber",
    "orderdetails": ("orderNumber", "productCode"),
}


FK = {
    ("products", "productLine"): ("productlines", "productLine"),
    ("employees", "officeCode"): ("offices", "officeCode"),
    ("employees", "reportsTo"): ("employees", "employeeNumber"),
    ("customers", "salesRepEmployeeNumber"): ("employees", "employeeNumber"),
    ("payments", "customerNumber"): ("customers", "customerNumber"),
    ("orders", "customerNumber"): ("customers", "customerNumber"),
    ("orderdetails", "orderNumber"): ("orders", "orderNumber"),
    ("orderdetails", "productCode"): ("products", "productCode"),
}


def get_cursor():
    conn = get_connection()
    return conn.cursor(), conn
