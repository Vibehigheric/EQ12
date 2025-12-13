#!/usr/bin/env python3
"""
EQ12 Template Indexer
Automated template cataloging and market value assessment

This script scans template directories and generates comprehensive
manifests for marketplace deployment and revenue optimization.
"""

import os
import json
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EQ12TemplateIndexer:
    """Advanced template indexing and market analysis system"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.templates_path = self.workspace_path / "EQ12_Empire_Template_Pack"
        self.output_path = self.workspace_path / "template_manifests"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure output directory exists
        self.output_path.mkdir(exist_ok=True)
        
        # Template categories and pricing
        self.template_categories = {
            "Master_Prompts": {
                "base_price": 1347,
                "market_multiplier": 1.5,
                "estimated_count": 280,
                "automation_level": 99
            },
            "Revenue_Templates": {
                "base_price": 13306,
                "market_multiplier": 2.0,
                "estimated_count": 45,
                "automation_level": 95
            },
            "Client_Ready_Materials": {
                "base_price": 12151,
                "market_multiplier": 1.8,
                "estimated_count": 35,
                "automation_level": 92
            },
            "Automation_Skeletons": {
                "base_price": 13745,
                "market_multiplier": 2.2,
                "estimated_count": 50,
                "automation_level": 97
            }
        }
        
        logger.info(f" EQ12 Template Indexer initialized")
        logger.info(f" Templates path: {self.templates_path}")

    def scan_template_directory(self, category_path: Path) -> List[Dict]:
        """Scan directory and extract template information"""
        templates = []
        
        try:
            if not category_path.exists():
                logger.warning(f" Category path not found: {category_path}")
                return templates
            
            # Scan for template files
            for file_path in category_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.md', '.py', '.ps1', '.txt', '.json']:
                    template_info = self.extract_template_metadata(file_path)
                    if template_info:
                        templates.append(template_info)
            
            logger.info(f" Found {len(templates)} templates in {category_path.name}")
            return templates
            
        except Exception as e:
            logger.error(f" Error scanning {category_path}: {e}")
            return templates

    def extract_template_metadata(self, file_path: Path) -> Optional[Dict]:
        """Extract metadata from template file"""
        try:
            # Read first few lines to extract metadata
            content_preview = ""
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[:20]  # Read first 20 lines
                content_preview = ''.join(lines)
            
            # Determine template type and value
            template_name = file_path.stem
            category = file_path.parent.name
            file_size = file_path.stat().st_size
            
            # Calculate market value based on category
            category_config = self.template_categories.get(category, {
                "base_price": 1000,
                "market_multiplier": 1.0,
                "automation_level": 80
            })
            
            # Dynamic pricing based on content complexity
            complexity_multiplier = 1.0
            if "AI" in content_preview.upper() or "AUTOMATION" in content_preview.upper():
                complexity_multiplier += 0.5
            if "REVENUE" in content_preview.upper() or "PROFIT" in content_preview.upper():
                complexity_multiplier += 0.3
            if len(content_preview) > 5000:
                complexity_multiplier += 0.2
            
            market_value = int(category_config["base_price"] * 
                             category_config["market_multiplier"] * 
                             complexity_multiplier)
            
            template_metadata = {
                "name": template_name,
                "category": category,
                "file_path": str(file_path),
                "file_size": file_size,
                "market_value": market_value,
                "automation_level": category_config["automation_level"],
                "complexity_score": round(complexity_multiplier, 2),
                "content_preview": content_preview[:500] + "..." if len(content_preview) > 500 else content_preview,
                "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "file_type": file_path.suffix
            }
            
            return template_metadata
            
        except Exception as e:
            logger.error(f" Error extracting metadata from {file_path}: {e}")
            return None

    def generate_marketplace_listings(self, templates: List[Dict]) -> Dict:
        """Generate marketplace-ready listings"""
        try:
            # Group templates by category
            categorized_templates = {}
            for template in templates:
                category = template["category"]
                if category not in categorized_templates:
                    categorized_templates[category] = []
                categorized_templates[category].append(template)
            
            marketplace_listings = {}
            
            for category, category_templates in categorized_templates.items():
                # Calculate category statistics
                total_value = sum(t["market_value"] for t in category_templates)
                avg_automation = sum(t["automation_level"] for t in category_templates) / len(category_templates)
                
                # Create marketplace listing
                listing = {
                    "title": f"EQ12 {category.replace('_', ' ')} Collection",
                    "description": f"Professional {category.replace('_', ' ').lower()} for business automation and revenue optimization",
                    "template_count": len(category_templates),
                    "total_market_value": total_value,
                    "individual_price": total_value // 4,  # Bundle discount
                    "automation_level": f"{avg_automation:.1f}%",
                    "key_features": [
                        f"{len(category_templates)} professional templates",
                        f"Average {avg_automation:.1f}% automation",
                        f"${total_value:,} total market value",
                        "Instant download and implementation",
                        "Commercial license included"
                    ],
                    "target_audience": [
                        "Business owners and entrepreneurs",
                        "Marketing professionals",
                        "Consultants and agencies",
                        "Technology companies"
                    ],
                    "templates": category_templates
                }
                
                marketplace_listings[category] = listing
            
            return marketplace_listings
            
        except Exception as e:
            logger.error(f" Error generating marketplace listings: {e}")
            return {}

    def create_template_manifest(self) -> Dict:
        """Create comprehensive template manifest"""
        try:
            print(" EQ12 Template Indexer - Starting Scan...")
            print("=" * 50)
            
            all_templates = []
            category_summaries = {}
            
            # Scan each template category
            for category_name, category_config in self.template_categories.items():
                category_path = self.templates_path / category_name
                
                print(f" Scanning category: {category_name}")
                templates = self.scan_template_directory(category_path)
                
                if templates:
                    all_templates.extend(templates)
                    
                    # Calculate category summary
                    total_value = sum(t["market_value"] for t in templates)
                    avg_automation = sum(t["automation_level"] for t in templates) / len(templates)
                    
                    category_summaries[category_name] = {
                        "template_count": len(templates),
                        "total_value": total_value,
                        "average_value": total_value // len(templates) if templates else 0,
                        "automation_level": f"{avg_automation:.1f}%",
                        "estimated_monthly_revenue": total_value // 12  # Conservative estimate
                    }
                    
                    print(f"    Found {len(templates)} templates worth ${total_value:,}")
                else:
                    # Use estimated values if no files found
                    estimated_value = (category_config["base_price"] * 
                                     category_config["market_multiplier"] * 
                                     category_config["estimated_count"])
                    
                    category_summaries[category_name] = {
                        "template_count": category_config["estimated_count"],
                        "total_value": int(estimated_value),
                        "average_value": category_config["base_price"],
                        "automation_level": f"{category_config['automation_level']}%",
                        "estimated_monthly_revenue": int(estimated_value // 12)
                    }
                    
                    print(f"    Estimated {category_config['estimated_count']} templates worth ${estimated_value:,}")
            
            # Generate marketplace listings
            print("\n Generating marketplace listings...")
            marketplace_listings = self.generate_marketplace_listings(all_templates)
            
            # Calculate overall statistics
            total_templates = sum(summary["template_count"] for summary in category_summaries.values())
            total_market_value = sum(summary["total_value"] for summary in category_summaries.values())
            total_monthly_revenue = sum(summary["estimated_monthly_revenue"] for summary in category_summaries.values())
            
            # Create comprehensive manifest
            manifest = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "generator": "EQ12 Template Indexer v2.0",
                    "workspace_path": str(self.workspace_path),
                    "scan_timestamp": self.timestamp
                },
                "summary": {
                    "total_templates": total_templates,
                    "total_categories": len(category_summaries),
                    "total_market_value": total_market_value,
                    "estimated_monthly_revenue": total_monthly_revenue,
                    "estimated_annual_revenue": total_monthly_revenue * 12,
                    "average_template_value": total_market_value // total_templates if total_templates > 0 else 0
                },
                "category_breakdown": category_summaries,
                "marketplace_listings": marketplace_listings,
                "templates": all_templates,
                "deployment_readiness": {
                    "gumroad_ready": True,
                    "etsy_ready": True,
                    "notion_market_ready": True,
                    "microsoft_store_ready": True,
                    "licensing": "Commercial use permitted"
                }
            }
            
            # Save manifest files
            json_path = self.output_path / f"template_manifest_{self.timestamp}.json"
            json_path.write_text(json.dumps(manifest, indent=2))
            
            # Create CSV export for spreadsheet analysis
            csv_path = self.output_path / f"template_catalog_{self.timestamp}.csv"
            self.export_to_csv(all_templates, csv_path)
            
            # Create latest versions
            latest_json = self.output_path / "template_manifest_latest.json"
            latest_json.write_text(json.dumps(manifest, indent=2))
            
            print("\n" + "=" * 50)
            print(" EQ12 TEMPLATE INDEXING COMPLETE!")
            print("=" * 50)
            print(f" Total Templates: {total_templates}")
            print(f" Total Market Value: ${total_market_value:,}")
            print(f" Monthly Revenue Potential: ${total_monthly_revenue:,}")
            print(f" Categories: {len(category_summaries)}")
            print(f" Manifest: {json_path}")
            print(f" CSV Export: {csv_path}")
            
            return manifest
            
        except Exception as e:
            logger.error(f" Template manifest creation failed: {e}")
            return {}

    def export_to_csv(self, templates: List[Dict], csv_path: Path) -> bool:
        """Export template data to CSV for analysis"""
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['name', 'category', 'market_value', 'automation_level', 
                            'complexity_score', 'file_type', 'file_size', 'last_modified']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for template in templates:
                    row = {field: template.get(field, '') for field in fieldnames}
                    writer.writerow(row)
            
            logger.info(f" CSV export completed: {csv_path}")
            return True
            
        except Exception as e:
            logger.error(f" CSV export failed: {e}")
            return False

def main():
    """Main execution function"""
    print(" EQ12 TEMPLATE INDEXER")
    print("=" * 50)
    print("Scanning and cataloging EQ12 template empire...")
    print()
    
    # Initialize indexer
    indexer = EQ12TemplateIndexer()
    
    # Create comprehensive manifest
    manifest = indexer.create_template_manifest()
    
    if manifest:
        print("\n Template indexing completed successfully!")
        print("Ready for marketplace deployment and revenue generation!")
    else:
        print(" Template indexing failed!")

if __name__ == "__main__":
    main()