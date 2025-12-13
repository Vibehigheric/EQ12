#!/usr/bin/env python3
"""
Loganberry Inventory Management System
Core inventory logic for Crystal Beach product tracking
Part of EQ12 Project 3 - Beverage E-Commerce

Features:
- Product catalog management
- Real-time inventory tracking
- Automatic reorder alerts
- Sales logging and analytics
- Integration with Windows Data Sentinel
"""

import sqlite3
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LoganberryInventory')


class LoganberryInventory:
    """
    Main inventory management class for loganberry products
    """
    
    def __init__(self, db_path='C:\\EQ12\\data\\loganberry_inventory.db'):
        self.db_path = db_path
        self.init_database()
        logger.info(f"Loganberry Inventory initialized: {db_path}")
    
    def init_database(self):
        """Create database schema if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                sku TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                cost_price REAL NOT NULL,
                retail_price REAL NOT NULL,
                quantity INTEGER DEFAULT 0,
                reorder_threshold INTEGER DEFAULT 10,
                supplier TEXT,
                size TEXT,
                unit TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Sales table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                sale_price REAL NOT NULL,
                cost_price REAL,
                sale_date TEXT NOT NULL,
                channel TEXT,
                customer_type TEXT,
                notes TEXT,
                FOREIGN KEY (sku) REFERENCES products(sku)
            )
        ''')
        
        # Purchase orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                po_number TEXT UNIQUE,
                sku TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                cost_price REAL NOT NULL,
                supplier TEXT,
                order_date TEXT NOT NULL,
                expected_date TEXT,
                received_date TEXT,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (sku) REFERENCES products(sku)
            )
        ''')
        
        # Indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sales_sku ON sales(sku)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_po_status ON purchase_orders(status)')
        
        conn.commit()
        conn.close()
        logger.info("Database schema initialized")
    
    def add_product(
        self, 
        sku: str, 
        name: str, 
        cost_price: float, 
        retail_price: float,
        quantity: int = 0,
        category: str = 'loganberry',
        reorder_threshold: int = 10,
        supplier: str = 'Buffalo in a Box',
        size: str = '',
        unit: str = 'bottle'
    ) -> bool:
        """
        Add new product to inventory or update if exists
        
        Args:
            sku: Stock keeping unit (unique identifier)
            name: Product name
            cost_price: What you pay
            retail_price: What you charge
            quantity: Initial stock
            category: Product category
            reorder_threshold: Alert when stock drops below this
            supplier: Where to buy from
            size: Product size (e.g., "1L", "20oz")
            unit: Unit type (bottle, can, case)
        
        Returns:
            True if successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            now = datetime.now(timezone.utc).isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO products 
                (sku, name, category, cost_price, retail_price, quantity, 
                 reorder_threshold, supplier, size, unit, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                        COALESCE((SELECT created_at FROM products WHERE sku = ?), ?),
                        ?)
            ''', (sku, name, category, cost_price, retail_price, quantity,
                  reorder_threshold, supplier, size, unit, sku, now, now))
            
            conn.commit()
            logger.info(f"Product added/updated: {sku} - {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding product {sku}: {e}")
            return False
        finally:
            conn.close()
    
    def record_sale(
        self, 
        sku: str, 
        quantity: int, 
        sale_price: float,
        channel: str = 'retail',
        customer_type: str = 'individual',
        notes: str = ''
    ) -> bool:
        """
        Record a sale and update inventory
        
        Args:
            sku: Product SKU
            quantity: Units sold
            sale_price: Price per unit sold
            channel: retail, wholesale, farmers_market, online
            customer_type: individual, store, restaurant
            notes: Additional notes
        
        Returns:
            True if successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check current stock
            cursor.execute('SELECT quantity, cost_price FROM products WHERE sku = ?', (sku,))
            result = cursor.fetchone()
            
            if not result:
                logger.error(f"Product not found: {sku}")
                return False
            
            current_qty, cost_price = result
            
            if current_qty < quantity:
                logger.warning(f"Insufficient stock for {sku}: have {current_qty}, need {quantity}")
                return False
            
            # Record sale
            now = datetime.now(timezone.utc).isoformat()
            cursor.execute('''
                INSERT INTO sales (sku, quantity, sale_price, cost_price, sale_date, channel, customer_type, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (sku, quantity, sale_price, cost_price, now, channel, customer_type, notes))
            
            # Update inventory
            new_qty = current_qty - quantity
            cursor.execute('UPDATE products SET quantity = ?, updated_at = ? WHERE sku = ?', 
                         (new_qty, now, sku))
            
            conn.commit()
            logger.info(f"Sale recorded: {quantity}x {sku} @ ${sale_price} via {channel}. New stock: {new_qty}")
            
            # Check if reorder needed
            self._check_reorder_alert(sku, new_qty)
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording sale: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def _check_reorder_alert(self, sku: str, current_qty: int):
        """Check if product needs reordering and log alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, reorder_threshold FROM products WHERE sku = ?', (sku,))
        result = cursor.fetchone()
        
        if result:
            name, threshold = result
            if current_qty <= threshold:
                logger.warning(f"⚠️ LOW STOCK ALERT: {name} ({sku}) - Only {current_qty} left! (Threshold: {threshold})")
        
        conn.close()
    
    def check_reorder_needed(self) -> List[Dict]:
        """
        Get list of products that need reordering
        
        Returns:
            List of products below reorder threshold
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sku, name, quantity, reorder_threshold, cost_price, supplier
            FROM products
            WHERE quantity <= reorder_threshold
            ORDER BY quantity ASC
        ''')
        
        reorder_list = []
        for row in cursor.fetchall():
            reorder_list.append({
                'sku': row[0],
                'name': row[1],
                'current_qty': row[2],
                'threshold': row[3],
                'cost_price': row[4],
                'supplier': row[5],
                'suggested_order': row[3] * 2  # Order 2x threshold
            })
        
        conn.close()
        return reorder_list
    
    def get_inventory_summary(self) -> Dict:
        """
        Get overall inventory statistics
        
        Returns:
            Dict with total value, item count, low stock count
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total inventory value (at cost)
        cursor.execute('SELECT SUM(quantity * cost_price) FROM products')
        total_value_cost = cursor.fetchone()[0] or 0.0
        
        # Total inventory value (at retail)
        cursor.execute('SELECT SUM(quantity * retail_price) FROM products')
        total_value_retail = cursor.fetchone()[0] or 0.0
        
        # Total items
        cursor.execute('SELECT COUNT(*) FROM products')
        total_products = cursor.fetchone()[0]
        
        # Total units in stock
        cursor.execute('SELECT SUM(quantity) FROM products')
        total_units = cursor.fetchone()[0] or 0
        
        # Low stock items
        cursor.execute('SELECT COUNT(*) FROM products WHERE quantity <= reorder_threshold')
        low_stock_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_value_cost': total_value_cost,
            'total_value_retail': total_value_retail,
            'potential_profit': total_value_retail - total_value_cost,
            'total_products': total_products,
            'total_units': total_units,
            'low_stock_count': low_stock_count
        }
    
    def get_sales_summary(self, days: int = 30) -> Dict:
        """
        Get sales statistics for recent period
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dict with revenue, profit, units sold
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        from datetime import timedelta
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        # Total revenue
        cursor.execute('''
            SELECT SUM(quantity * sale_price) 
            FROM sales 
            WHERE sale_date >= ?
        ''', (cutoff_date,))
        total_revenue = cursor.fetchone()[0] or 0.0
        
        # Total cost
        cursor.execute('''
            SELECT SUM(quantity * cost_price) 
            FROM sales 
            WHERE sale_date >= ?
        ''', (cutoff_date,))
        total_cost = cursor.fetchone()[0] or 0.0
        
        # Total units sold
        cursor.execute('''
            SELECT SUM(quantity) 
            FROM sales 
            WHERE sale_date >= ?
        ''', (cutoff_date,))
        total_units = cursor.fetchone()[0] or 0
        
        # Number of transactions
        cursor.execute('''
            SELECT COUNT(*) 
            FROM sales 
            WHERE sale_date >= ?
        ''', (cutoff_date,))
        transaction_count = cursor.fetchone()[0]
        
        conn.close()
        
        profit = total_revenue - total_cost
        margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            'period_days': days,
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'profit': profit,
            'profit_margin_pct': margin,
            'units_sold': total_units,
            'transactions': transaction_count,
            'avg_transaction': total_revenue / transaction_count if transaction_count > 0 else 0
        }
    
    def get_best_sellers(self, limit: int = 10) -> List[Dict]:
        """Get top-selling products"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.sku, p.name, SUM(s.quantity) as total_sold, 
                   SUM(s.quantity * s.sale_price) as revenue
            FROM sales s
            JOIN products p ON s.sku = p.sku
            GROUP BY p.sku
            ORDER BY total_sold DESC
            LIMIT ?
        ''', (limit,))
        
        best_sellers = []
        for row in cursor.fetchall():
            best_sellers.append({
                'sku': row[0],
                'name': row[1],
                'units_sold': row[2],
                'revenue': row[3]
            })
        
        conn.close()
        return best_sellers


def main():
    """Demo usage"""
    inventory = LoganberryInventory()
    
    # Add sample products (Crystal Beach loganberry from your pricing data)
    inventory.add_product(
        sku='CB-1L-SYRUP',
        name='Crystal Beach Loganberry Syrup 1L',
        cost_price=16.99,
        retail_price=35.00,  # Mixed and resold
        quantity=20,
        category='syrup',
        size='1L',
        unit='bottle',
        reorder_threshold=5
    )
    
    inventory.add_product(
        sku='CB-12PACK-CAN',
        name='Crystal Beach Loganberry 12-Pack Cans',
        cost_price=25.95,
        retail_price=45.00,
        quantity=15,
        category='cans',
        size='12x12oz',
        unit='case',
        reorder_threshold=3
    )
    
    inventory.add_product(
        sku='CB-20OZ-BTL',
        name='Crystal Beach Original Loganberry 20oz',
        cost_price=2.99,
        retail_price=5.99,
        quantity=15,
        category='bottle',
        size='20oz',
        unit='bottle',
        reorder_threshold=10
    )
    
    # Simulate some sales
    inventory.record_sale('CB-20OZ-BTL', 3, 5.99, channel='retail')
    inventory.record_sale('CB-12PACK-CAN', 2, 45.00, channel='wholesale', customer_type='store')
    
    # Get summaries
    inv_summary = inventory.get_inventory_summary()
    print("\n=== INVENTORY SUMMARY ===")
    print(f"Total Products: {inv_summary['total_products']}")
    print(f"Total Units: {inv_summary['total_units']}")
    print(f"Inventory Value (Cost): ${inv_summary['total_value_cost']:.2f}")
    print(f"Inventory Value (Retail): ${inv_summary['total_value_retail']:.2f}")
    print(f"Potential Profit: ${inv_summary['potential_profit']:.2f}")
    print(f"Low Stock Items: {inv_summary['low_stock_count']}")
    
    sales_summary = inventory.get_sales_summary(days=7)
    print("\n=== SALES SUMMARY (Last 7 Days) ===")
    print(f"Revenue: ${sales_summary['total_revenue']:.2f}")
    print(f"Cost: ${sales_summary['total_cost']:.2f}")
    print(f"Profit: ${sales_summary['profit']:.2f}")
    print(f"Margin: {sales_summary['profit_margin_pct']:.1f}%")
    print(f"Units Sold: {sales_summary['units_sold']}")
    
    # Check reorders
    reorder_list = inventory.check_reorder_needed()
    if reorder_list:
        print("\n=== REORDER NEEDED ===")
        for item in reorder_list:
            print(f"{item['name']}: {item['current_qty']} in stock (suggest ordering {item['suggested_order']})")


if __name__ == '__main__':
    main()
