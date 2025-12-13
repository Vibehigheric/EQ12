#!/usr/bin/env python3
"""
 EQ12 eBay  USPS Flat-Rate Automation Toolkit
Complete automation for eBay selling with USPS Flat-Rate optimization

Created: November 7, 2025
Author: EQ12 Commerce Automation Team
Purpose: Lean, profitable, semi-automatic eBay  USPS workflow
Classification: COMMERCIAL - EQ12 COMMERCE STACK
"""

import json
import csv
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib
import requests
from dataclasses import dataclass, asdict
import argparse


@dataclass
class EBayItem:
    """eBay listing item with shipping optimization"""
    sku: str
    title: str
    category: str
    cost: float
    sale_price: float
    weight_oz: float
    dimensions: Dict[str, float]  # length, width, height in inches
    fits_flat_rate: str  # small, medium, large, envelope, padded, none
    preferred_box: str
    shipping_charged: float
    ebay_fee_percent: float = 0.129  # Current eBay final value fee
    paypal_fee_percent: float = 0.029  # PayPal/payment processing
    fixed_fee: float = 0.30


@dataclass
class ShippingOption:
    """USPS shipping option with cost calculation"""
    service_name: str
    package_type: str
    cost: float
    delivery_days: str
    tracking: bool
    insurance_included: float


@dataclass
class ProfitAnalysis:
    """Profit analysis for eBay item"""
    gross_revenue: float
    ebay_fees: float
    payment_fees: float
    item_cost: float
    shipping_cost: float
    box_cost: float
    net_profit: float
    profit_margin: float


class EBayShippingOptimizer:
    """
     eBay shipping optimization and profit calculation engine
    """
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.data_path = self.workspace_path / "data" / "ebay_automation"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = self._setup_logging()
        
        # USPS Flat-Rate pricing (2025 rates)
        self.flat_rate_prices = {
            "envelope": 8.95,
            "padded_envelope": 10.20,
            "small_box": 10.20,
            "medium_box": 17.10,
            "large_box": 23.75,
            "legal_envelope": 8.95
        }
        
        # Box dimensions (length x width x height in inches)
        self.box_dimensions = {
            "envelope": {"max_length": 12.5, "max_width": 9.5, "max_height": 0.75},
            "padded_envelope": {"max_length": 14.125, "max_width": 11.5, "max_height": 2.0},
            "small_box": {"max_length": 8.625, "max_width": 5.375, "max_height": 1.625},
            "medium_box": {"max_length": 14, "max_width": 12, "max_height": 3.5},
            "large_box": {"max_length": 23.6875, "max_width": 11.75, "max_height": 3.0}
        }
        
        # Box costs (packaging materials)
        self.box_costs = {
            "envelope": 0.05,
            "padded_envelope": 0.15,
            "small_box": 0.08,
            "medium_box": 0.12,
            "large_box": 0.18,
            "custom_packaging": 0.25
        }
    
    def _setup_logging(self):
        """Setup logging for shipping optimization"""
        log_file = self.data_path / f"ebay_shipping_optimizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - [EBAY_OPTIMIZER] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger(__name__)
    
    def calculate_optimal_flat_rate(self, item: EBayItem) -> Dict[str, Any]:
        """
         Calculate optimal flat-rate shipping for item
        """
        dims = item.dimensions
        weight_oz = item.weight_oz
        
        # Check which flat-rate boxes the item fits in
        fitting_boxes = []
        
        for box_type, box_dims in self.box_dimensions.items():
            if (dims["length"] <= box_dims["max_length"] and 
                dims["width"] <= box_dims["max_width"] and 
                dims["height"] <= box_dims["max_height"]):
                
                fitting_boxes.append({
                    "box_type": box_type,
                    "shipping_cost": self.flat_rate_prices[box_type],
                    "box_cost": self.box_costs[box_type],
                    "total_shipping_cost": self.flat_rate_prices[box_type] + self.box_costs[box_type]
                })
        
        if not fitting_boxes:
            # Item doesn't fit in any flat-rate box
            return {
                "recommendation": "priority_regular",
                "estimated_cost": self._estimate_priority_regular_cost(weight_oz),
                "reason": "Item too large for flat-rate packaging"
            }
        
        # Find the cheapest option
        optimal_box = min(fitting_boxes, key=lambda x: x["total_shipping_cost"])
        
        return {
            "recommendation": optimal_box["box_type"],
            "shipping_cost": optimal_box["shipping_cost"],
            "box_cost": optimal_box["box_cost"],
            "total_cost": optimal_box["total_shipping_cost"],
            "fitting_boxes": fitting_boxes,
            "savings_vs_largest": max(fitting_boxes, key=lambda x: x["total_shipping_cost"])["total_shipping_cost"] - optimal_box["total_shipping_cost"]
        }
    
    def _estimate_priority_regular_cost(self, weight_oz: float) -> float:
        """Estimate Priority Mail regular cost (zone 1-3 average)"""
        weight_lb = weight_oz / 16.0
        
        if weight_lb <= 1:
            return 7.50
        elif weight_lb <= 2:
            return 8.25
        elif weight_lb <= 3:
            return 9.85
        elif weight_lb <= 5:
            return 12.60
        else:
            return 15.00 + (weight_lb - 5) * 1.50
    
    def calculate_profit_analysis(self, item: EBayItem) -> ProfitAnalysis:
        """
         Calculate comprehensive profit analysis
        """
        # Get optimal shipping
        shipping_opt = self.calculate_optimal_flat_rate(item)
        shipping_cost = shipping_opt.get("shipping_cost", item.shipping_charged)
        box_cost = shipping_opt.get("box_cost", 0.25)
        
        # Calculate fees
        gross_revenue = item.sale_price + item.shipping_charged
        ebay_fees = item.sale_price * item.ebay_fee_percent + item.fixed_fee
        payment_fees = gross_revenue * item.paypal_fee_percent
        
        # Calculate net profit
        total_costs = item.cost + shipping_cost + box_cost + ebay_fees + payment_fees
        net_profit = gross_revenue - total_costs
        profit_margin = (net_profit / gross_revenue) * 100 if gross_revenue > 0 else 0
        
        return ProfitAnalysis(
            gross_revenue=gross_revenue,
            ebay_fees=ebay_fees,
            payment_fees=payment_fees,
            item_cost=item.cost,
            shipping_cost=shipping_cost,
            box_cost=box_cost,
            net_profit=net_profit,
            profit_margin=profit_margin
        )
    
    def generate_label_csv_data(self, items: List[EBayItem], orders: List[Dict]) -> List[Dict]:
        """
         Generate CSV data for bulk label creation (EasyPost/Pirate Ship)
        """
        csv_data = []
        
        for order in orders:
            # Find matching item
            item = next((item for item in items if item.sku == order.get("sku")), None)
            if not item:
                continue
            
            # Get shipping optimization
            shipping_opt = self.calculate_optimal_flat_rate(item)
            
            csv_row = {
                "order_id": order.get("order_id"),
                "to_name": order.get("buyer_name"),
                "address1": order.get("address1"),
                "city": order.get("city"),
                "state": order.get("state"),
                "zip": order.get("zip_code"),
                "country": order.get("country", "US"),
                "weight_oz": item.weight_oz,
                "box_type": shipping_opt.get("recommendation", "medium_box"),
                "insurance_value": min(item.sale_price, 100),  # Insurance up to $100
                "service_type": "USPS_PRIORITY",
                "package_type": "FLAT_RATE_BOX"
            }
            
            csv_data.append(csv_row)
        
        return csv_data
    
    def save_label_csv(self, csv_data: List[Dict], filename: str = None) -> str:
        """Save label data as CSV for bulk upload"""
        if not filename:
            filename = f"labels_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        csv_path = self.data_path / filename
        
        if csv_data:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
        
        self.logger.info(f" Label CSV saved: {csv_path} ({len(csv_data)} orders)")
        return str(csv_path)
    
    def analyze_inventory_profitability(self, items: List[EBayItem]) -> Dict[str, Any]:
        """
         Analyze inventory for profitability and shipping optimization
        """
        analysis = {
            "total_items": len(items),
            "profitable_items": 0,
            "marginal_items": 0,
            "unprofitable_items": 0,
            "avg_profit_margin": 0,
            "shipping_optimization": {
                "flat_rate_recommended": 0,
                "priority_regular_recommended": 0,
                "potential_savings": 0
            },
            "item_analysis": []
        }
        
        total_profit_margin = 0
        
        for item in items:
            profit_analysis = self.calculate_profit_analysis(item)
            shipping_opt = self.calculate_optimal_flat_rate(item)
            
            # Categorize profitability
            if profit_analysis.profit_margin >= 25:
                analysis["profitable_items"] += 1
                category = "PROFITABLE"
            elif profit_analysis.profit_margin >= 10:
                analysis["marginal_items"] += 1
                category = "MARGINAL"
            else:
                analysis["unprofitable_items"] += 1
                category = "UNPROFITABLE"
            
            # Track shipping recommendations
            if shipping_opt.get("recommendation") != "priority_regular":
                analysis["shipping_optimization"]["flat_rate_recommended"] += 1
                analysis["shipping_optimization"]["potential_savings"] += shipping_opt.get("savings_vs_largest", 0)
            else:
                analysis["shipping_optimization"]["priority_regular_recommended"] += 1
            
            total_profit_margin += profit_analysis.profit_margin
            
            analysis["item_analysis"].append({
                "sku": item.sku,
                "title": item.title[:50],
                "category": category,
                "profit_margin": round(profit_analysis.profit_margin, 2),
                "net_profit": round(profit_analysis.net_profit, 2),
                "recommended_shipping": shipping_opt.get("recommendation"),
                "shipping_cost": shipping_opt.get("shipping_cost", 0),
                "box_type": shipping_opt.get("recommendation")
            })
        
        analysis["avg_profit_margin"] = total_profit_margin / len(items) if items else 0
        
        return analysis
    
    def generate_google_sheets_template(self) -> Dict[str, Any]:
        """
         Generate Google Sheets template for eBay automation
        """
        template = {
            "sheet_name": "EQ12_eBay_Automation",
            "headers": [
                "SKU", "Title", "Category", "Cost", "Sale_Price", "Weight_Oz",
                "Length", "Width", "Height", "Fits_Flat_Rate", "Preferred_Box",
                "Shipping_Charged", "eBay_Fee_Percent", "PayPal_Fee_Percent",
                "Gross_Revenue", "Total_Fees", "Net_Profit", "Profit_Margin",
                "Recommended_Box", "Shipping_Cost", "Box_Cost", "Last_Updated"
            ],
            "formulas": {
                "Gross_Revenue": "=E2+L2",  # Sale_Price + Shipping_Charged
                "Total_Fees": "=E2*M2+N2*O2+0.30",  # Sale_Price*eBay_Fee + Revenue*PayPal_Fee + Fixed_Fee
                "Net_Profit": "=O2-P2-D2-T2-U2",  # Gross_Revenue - Total_Fees - Cost - Shipping_Cost - Box_Cost
                "Profit_Margin": "=Q2/O2*100"  # Net_Profit/Gross_Revenue*100
            },
            "sample_data": [
                {
                    "SKU": "TECH001",
                    "Title": "Vintage Camera Lens 50mm",
                    "Category": "Photography",
                    "Cost": 15.00,
                    "Sale_Price": 45.00,
                    "Weight_Oz": 12,
                    "Length": 4,
                    "Width": 4,
                    "Height": 3,
                    "Fits_Flat_Rate": "small_box",
                    "Preferred_Box": "small_box",
                    "Shipping_Charged": 10.20,
                    "eBay_Fee_Percent": 0.129,
                    "PayPal_Fee_Percent": 0.029
                }
            ]
        }
        
        return template


class EBayPirateShipIntegration:
    """
     Pirate Ship API integration for bulk label creation
    """
    
    def __init__(self, api_token: str = None):
        self.api_token = api_token or os.getenv("PIRATE_SHIP_API_TOKEN")
        self.base_url = "https://api.pirateship.com/v1"
        self.session = requests.Session()
        
        if self.api_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            })
    
    def create_bulk_labels(self, csv_data: List[Dict]) -> Dict[str, Any]:
        """Create bulk shipping labels via Pirate Ship API"""
        if not self.api_token:
            return {"error": "No Pirate Ship API token configured"}
        
        results = {
            "total_labels": len(csv_data),
            "successful_labels": [],
            "failed_labels": [],
            "total_cost": 0
        }
        
        for order in csv_data:
            try:
                # Create shipment
                shipment_data = {
                    "to": {
                        "name": order["to_name"],
                        "address1": order["address1"],
                        "city": order["city"],
                        "state": order["state"],
                        "zip": order["zip"],
                        "country": order.get("country", "US")
                    },
                    "package": {
                        "weight": {"value": order["weight_oz"], "unit": "ounce"},
                        "type": order.get("package_type", "FLAT_RATE_BOX")
                    },
                    "service": order.get("service_type", "USPS_PRIORITY"),
                    "reference": order["order_id"]
                }
                
                # Mock API call (replace with actual API call)
                response = self._mock_api_call(shipment_data)
                
                if response.get("success"):
                    results["successful_labels"].append({
                        "order_id": order["order_id"],
                        "tracking_number": response["tracking_number"],
                        "label_url": response["label_url"],
                        "cost": response["cost"]
                    })
                    results["total_cost"] += response["cost"]
                else:
                    results["failed_labels"].append({
                        "order_id": order["order_id"],
                        "error": response.get("error", "Unknown error")
                    })
                    
            except Exception as e:
                results["failed_labels"].append({
                    "order_id": order.get("order_id", "unknown"),
                    "error": str(e)
                })
        
        return results
    
    def _mock_api_call(self, shipment_data: Dict) -> Dict[str, Any]:
        """Mock API call for testing (replace with actual API integration)"""
        import random
        
        # Simulate API response
        if random.random() > 0.1:  # 90% success rate
            return {
                "success": True,
                "tracking_number": f"9400100000000000{random.randint(100000, 999999)}",
                "label_url": f"https://pirateship.com/labels/{random.randint(1000000, 9999999)}.pdf",
                "cost": round(random.uniform(8.50, 25.00), 2)
            }
        else:
            return {
                "success": False,
                "error": "Address validation failed"
            }


def create_google_apps_script():
    """
     Generate Google Apps Script for Google Sheets integration
    """
    apps_script = '''
// Google Apps Script for EQ12 eBay Automation
// Paste this into Google Apps Script (script.google.com)

function buildLabelCSV() {
  const ss = SpreadsheetApp.getActive();
  const sheet = ss.getSheetByName("Orders");
  
  if (!sheet) {
    Browser.msgBox("Error", "Orders sheet not found. Please create an Orders sheet first.", Browser.Buttons.OK);
    return;
  }
  
  const rows = sheet.getDataRange().getValues();
  const headers = rows.shift();
  
  // Build CSV data
  const csvData = [];
  csvData.push(["order_id","to_name","address1","city","state","zip","country","weight_oz","box_type","insurance_value"]);
  
  rows.forEach(row => {
    if (row[0]) { // If order ID exists
      const orderData = [
        row[0] || "",  // Order ID
        row[1] || "",  // Name
        row[2] || "",  // Address1
        row[3] || "",  // City
        row[4] || "",  // State
        row[5] || "",  // Zip
        row[6] || "US", // Country
        row[7] || 16,  // Weight (oz)
        row[8] || "medium_box", // Box type
        row[9] || 50   // Insurance value
      ];
      csvData.push(orderData);
    }
  });
  
  // Convert to CSV string
  const csvString = csvData.map(row => 
    row.map(cell => `"${(cell||"").toString().replace(/"/g,'""')}"`).join(",")
  ).join("\\n");
  
  // Create file in Google Drive
  const fileName = `EQ12_Labels_${new Date().getTime()}.csv`;
  const blob = Utilities.newBlob(csvString, 'text/csv', fileName);
  const file = DriveApp.createFile(blob);
  
  Browser.msgBox("Success", `CSV created: ${fileName}\\nFile ID: ${file.getId()}\\nShare this file with your shipping provider.`, Browser.Buttons.OK);
  
  // Log the file URL
  console.log(`CSV file created: ${file.getUrl()}`);
  
  return file.getUrl();
}

function calculateProfitMargins() {
  const ss = SpreadsheetApp.getActive();
  const sheet = ss.getSheetByName("EQ12_eBay_Automation");
  
  if (!sheet) {
    Browser.msgBox("Error", "EQ12_eBay_Automation sheet not found.", Browser.Buttons.OK);
    return;
  }
  
  const range = sheet.getDataRange();
  const values = range.getValues();
  
  // Update profit calculations for each row (starting from row 2)
  for (let i = 1; i < values.length; i++) {
    const row = i + 1;
    
    // Set formulas if they don't exist
    if (!sheet.getRange(`O${row}`).getFormula()) {
      sheet.getRange(`O${row}`).setFormula(`=E${row}+L${row}`); // Gross Revenue
    }
    if (!sheet.getRange(`P${row}`).getFormula()) {
      sheet.getRange(`P${row}`).setFormula(`=E${row}*M${row}+O${row}*N${row}+0.30`); // Total Fees
    }
    if (!sheet.getRange(`Q${row}`).getFormula()) {
      sheet.getRange(`Q${row}`).setFormula(`=O${row}-P${row}-D${row}-T${row}-U${row}`); // Net Profit
    }
    if (!sheet.getRange(`R${row}`).getFormula()) {
      sheet.getRange(`R${row}`).setFormula(`=IF(O${row}>0,Q${row}/O${row}*100,0)`); // Profit Margin %
    }
  }
  
  Browser.msgBox("Success", "Profit margin formulas updated for all rows!", Browser.Buttons.OK);
}

function createMenus() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('EQ12 eBay Tools')
    .addItem('Generate Label CSV', 'buildLabelCSV')
    .addItem('Calculate Profit Margins', 'calculateProfitMargins')
    .addSeparator()
    .addItem('Setup Instructions', 'showSetupInstructions')
    .addToUi();
}

function showSetupInstructions() {
  const instructions = `
EQ12 eBay Automation Setup:

1. Create an "Orders" sheet with columns:
   - Order ID, Name, Address1, City, State, Zip, Country, Weight (oz), Box Type, Insurance Value

2. Use the "EQ12_eBay_Automation" sheet for inventory management

3. Use "Generate Label CSV" to create shipping files

4. Upload CSV to Pirate Ship or EasyPost for bulk label creation

Need help? Contact EQ12 Support.
  `;
  
  Browser.msgBox("Setup Instructions", instructions, Browser.Buttons.OK);
}

function onOpen() {
  createMenus();
}
'''
    
    return apps_script


def main():
    """Main entry point for eBay automation toolkit"""
    parser = argparse.ArgumentParser(description=" EQ12 eBay  USPS Automation Toolkit")
    parser.add_argument("--action", choices=["analyze", "generate-csv", "profit-calc", "setup"], 
                       default="analyze", help="Action to perform")
    parser.add_argument("--workspace", default="C:\\EQ12", help="EQ12 workspace path")
    parser.add_argument("--sample-data", action="store_true", help="Generate sample data for testing")
    
    args = parser.parse_args()
    
    print("" + "="*70)
    print(" EQ12 eBay  USPS FLAT-RATE AUTOMATION TOOLKIT")
    print("" + "="*70)
    
    optimizer = EBayShippingOptimizer(args.workspace)
    
    if args.action == "setup":
        # Generate setup files
        template = optimizer.generate_google_sheets_template()
        apps_script = create_google_apps_script()
        
        # Save files
        template_file = optimizer.data_path / "google_sheets_template.json"
        script_file = optimizer.data_path / "google_apps_script.js"
        
        with open(template_file, 'w') as f:
            json.dump(template, f, indent=2)
        
        with open(script_file, 'w') as f:
            f.write(apps_script)
        
        print(f" Setup files created:")
        print(f"    Google Sheets Template: {template_file}")
        print(f"    Google Apps Script: {script_file}")
        print(f"    Data Directory: {optimizer.data_path}")
        
    elif args.action == "analyze" or args.sample_data:
        # Create sample data for testing
        sample_items = [
            EBayItem(
                sku="TECH001", title="Vintage Camera Lens 50mm", category="Photography",
                cost=15.00, sale_price=45.00, weight_oz=12,
                dimensions={"length": 4, "width": 4, "height": 3},
                fits_flat_rate="small_box", preferred_box="small_box", shipping_charged=10.20
            ),
            EBayItem(
                sku="ELEC002", title="Bluetooth Wireless Headphones", category="Electronics",
                cost=8.50, sale_price=29.99, weight_oz=8,
                dimensions={"length": 6, "width": 5, "height": 2},
                fits_flat_rate="small_box", preferred_box="small_box", shipping_charged=10.20
            ),
            EBayItem(
                sku="BOOK003", title="Programming Python 4th Edition", category="Books",
                cost=12.00, sale_price=28.00, weight_oz=32,
                dimensions={"length": 9, "width": 7, "height": 2},
                fits_flat_rate="medium_box", preferred_box="medium_box", shipping_charged=17.10
            )
        ]
        
        # Analyze profitability
        analysis = optimizer.analyze_inventory_profitability(sample_items)
        
        print(f"\n INVENTORY ANALYSIS")
        print(f"    Total Items: {analysis['total_items']}")
        print(f"    Profitable Items: {analysis['profitable_items']} (25% margin)")
        print(f"     Marginal Items: {analysis['marginal_items']} (10-25% margin)")
        print(f"    Unprofitable Items: {analysis['unprofitable_items']} (<10% margin)")
        print(f"    Average Profit Margin: {analysis['avg_profit_margin']:.1f}%")
        
        print(f"\n SHIPPING OPTIMIZATION")
        print(f"    Flat-Rate Recommended: {analysis['shipping_optimization']['flat_rate_recommended']}")
        print(f"    Priority Regular Recommended: {analysis['shipping_optimization']['priority_regular_recommended']}")
        print(f"    Potential Savings: ${analysis['shipping_optimization']['potential_savings']:.2f}")
        
        # Save analysis
        analysis_file = optimizer.data_path / f"inventory_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        print(f"\n Analysis saved: {analysis_file}")
    
    print(f"\n Next Steps:")
    print(f"   1. Use --action setup to create Google Sheets templates")
    print(f"   2. Import your eBay sold items CSV")
    print(f"   3. Use --action generate-csv to create shipping labels")
    print(f"   4. Upload to Pirate Ship or EasyPost for bulk processing")
    print("" + "="*70)


if __name__ == "__main__":
    main()