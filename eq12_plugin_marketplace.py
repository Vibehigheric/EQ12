"""
EQ12 Plugin Marketplace and Partner Ecosystem
Revenue sharing platform for third-party governance modules
"""

import asyncio
import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class PluginStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"


class PluginCategory(str, Enum):
    COMPLIANCE = "compliance"
    SECURITY = "security"
    DATA_GOVERNANCE = "data_governance"
    MODEL_MONITORING = "model_monitoring"
    REPORTING = "reporting"
    INTEGRATION = "integration"
    AUTOMATION = "automation"


class RevenueModel(str, Enum):
    FREE = "free"
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    USAGE_BASED = "usage_based"
    REVENUE_SHARE = "revenue_share"


@dataclass
class PluginMetadata:
    name: str
    description: str
    version: str
    category: PluginCategory
    author: str
    author_email: str
    homepage_url: str
    documentation_url: str
    support_url: str
    tags: list[str]
    supported_frameworks: list[str]
    min_eq12_version: str
    max_eq12_version: str | None = None


@dataclass
class PluginPricing:
    model: RevenueModel
    base_price: Decimal
    recurring_period: str | None = None  # monthly, annual
    usage_tiers: list[dict[str, Any]] = field(default_factory=list)
    free_tier_limits: dict[str, Any] | None = None
    revenue_share_percentage: Decimal | None = None


@dataclass
class Plugin:
    id: str
    metadata: PluginMetadata
    pricing: PluginPricing
    status: PluginStatus
    install_count: int = 0
    rating: float = 0.0
    review_count: int = 0
    revenue_generated: Decimal = field(default_factory=lambda: Decimal("0.00"))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Technical details
    entry_point: str = ""
    dependencies: list[str] = field(default_factory=list)
    api_endpoints: list[dict[str, Any]] = field(default_factory=list)
    webhook_endpoints: list[str] = field(default_factory=list)
    required_permissions: list[str] = field(default_factory=list)


@dataclass
class Partner:
    id: str
    company_name: str
    contact_email: str
    partnership_tier: str  # bronze, silver, gold, platinum
    revenue_share_rate: Decimal
    total_revenue: Decimal = field(default_factory=lambda: Decimal("0.00"))
    plugins: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


class PluginMarketplace:
    """EQ12 Plugin Marketplace and Partner Ecosystem"""

    def __init__(self):
        self.plugins: dict[str, Plugin] = {}
        self.partners: dict[str, Partner] = {}
        self.installations: dict[str, list[str]] = {}  # customer_id -> plugin_ids
        self.reviews: dict[str, list[dict]] = {}  # plugin_id -> reviews
        self.revenue_records: list[dict] = []

        # Partnership tiers and revenue sharing
        self.partnership_tiers = {
            "bronze": {"revenue_share": Decimal("0.70"), "annual_fee": Decimal("1000")},
            "silver": {"revenue_share": Decimal("0.75"), "annual_fee": Decimal("5000")},
            "gold": {"revenue_share": Decimal("0.80"), "annual_fee": Decimal("15000")},
            "platinum": {
                "revenue_share": Decimal("0.85"),
                "annual_fee": Decimal("50000"),
            },
        }

    async def register_partner(self, partner_data: dict) -> dict:
        """Register new development partner"""

        partner_id = f"partner_{uuid.uuid4().hex[:12]}"

        partner = Partner(
            id=partner_id,
            company_name=partner_data["company_name"],
            contact_email=partner_data["contact_email"],
            partnership_tier=partner_data.get("tier", "bronze"),
            revenue_share_rate=self.partnership_tiers[partner_data.get("tier", "bronze")][
                "revenue_share"
            ],
        )

        self.partners[partner_id] = partner

        # Generate API credentials for partner
        api_key = f"eq12_partner_{hashlib.sha256(partner_id.encode()).hexdigest()[:32]}"

        return {
            "partner_id": partner_id,
            "api_key": api_key,
            "revenue_share_rate": float(partner.revenue_share_rate),
            "partnership_tier": partner.partnership_tier,
            "status": "registered",
            "onboarding_url": f"https://partners.eq12.ai/onboard/{partner_id}",
        }

    async def submit_plugin(self, partner_id: str, plugin_data: dict) -> dict:
        """Submit plugin for marketplace review"""

        if partner_id not in self.partners:
            return {"error": "Invalid partner ID"}

        plugin_id = f"plugin_{uuid.uuid4().hex[:12]}"

        # Validate plugin submission
        validation_result = await self._validate_plugin_submission(plugin_data)
        if not validation_result["is_valid"]:
            return {
                "error": "Validation failed",
                "details": validation_result["errors"],
            }

        # Create plugin metadata
        metadata = PluginMetadata(
            name=plugin_data["name"],
            description=plugin_data["description"],
            version=plugin_data["version"],
            category=PluginCategory(plugin_data["category"]),
            author=self.partners[partner_id].company_name,
            author_email=self.partners[partner_id].contact_email,
            homepage_url=plugin_data.get("homepage_url", ""),
            documentation_url=plugin_data.get("documentation_url", ""),
            support_url=plugin_data.get("support_url", ""),
            tags=plugin_data.get("tags", []),
            supported_frameworks=plugin_data.get("supported_frameworks", []),
            min_eq12_version=plugin_data["min_eq12_version"],
        )

        # Create pricing information
        pricing = PluginPricing(
            model=RevenueModel(plugin_data["pricing"]["model"]),
            base_price=Decimal(str(plugin_data["pricing"]["base_price"])),
            recurring_period=plugin_data["pricing"].get("recurring_period"),
            usage_tiers=plugin_data["pricing"].get("usage_tiers", []),
            free_tier_limits=plugin_data["pricing"].get("free_tier_limits"),
            revenue_share_percentage=self.partners[partner_id].revenue_share_rate,
        )

        # Create plugin
        plugin = Plugin(
            id=plugin_id,
            metadata=metadata,
            pricing=pricing,
            status=PluginStatus.PENDING,
            entry_point=plugin_data.get("entry_point", ""),
            dependencies=plugin_data.get("dependencies", []),
            api_endpoints=plugin_data.get("api_endpoints", []),
            webhook_endpoints=plugin_data.get("webhook_endpoints", []),
            required_permissions=plugin_data.get("required_permissions", []),
        )

        self.plugins[plugin_id] = plugin
        self.partners[partner_id].plugins.append(plugin_id)

        # Schedule automated review
        review_result = await self._automated_plugin_review(plugin)

        return {
            "plugin_id": plugin_id,
            "status": "submitted",
            "automated_review": review_result,
            "estimated_review_time": "3-5 business days",
            "review_url": f"https://partners.eq12.ai/plugins/{plugin_id}/review",
        }

    async def _validate_plugin_submission(self, plugin_data: dict) -> dict:
        """Validate plugin submission"""

        validation = {"is_valid": True, "errors": [], "warnings": []}

        # Required fields
        required_fields = ["name", "description", "version", "category", "pricing"]
        for field in required_fields:
            if field not in plugin_data:
                validation["errors"].append(f"Missing required field: {field}")
                validation["is_valid"] = False

        # Validate category
        if "category" in plugin_data:
            try:
                PluginCategory(plugin_data["category"])
            except ValueError:
                validation["errors"].append(f"Invalid category: {plugin_data['category']}")
                validation["is_valid"] = False

        # Validate pricing model
        if "pricing" in plugin_data:
            try:
                RevenueModel(plugin_data["pricing"]["model"])
            except ValueError:
                validation["errors"].append(
                    f"Invalid pricing model: {plugin_data['pricing']['model']}"
                )
                validation["is_valid"] = False

        # Security validation
        if "required_permissions" in plugin_data:
            dangerous_permissions = ["admin", "full_access", "system_modify"]
            for perm in plugin_data["required_permissions"]:
                if perm in dangerous_permissions:
                    validation["warnings"].append(f"High-risk permission requested: {perm}")

        return validation

    async def _automated_plugin_review(self, plugin: Plugin) -> dict:
        """Perform automated security and quality review"""

        review_score = 0.0
        review_items = []

        # Security checks
        if not plugin.required_permissions:
            review_score += 20
            review_items.append("✓ No dangerous permissions requested")
        else:
            dangerous_count = len(
                [
                    p
                    for p in plugin.required_permissions
                    if p in ["admin", "full_access", "system_modify"]
                ]
            )
            if dangerous_count == 0:
                review_score += 15
                review_items.append("✓ Safe permissions only")
            else:
                review_items.append("⚠ High-risk permissions need manual review")

        # Documentation quality
        if plugin.metadata.documentation_url:
            review_score += 15
            review_items.append("✓ Documentation provided")
        else:
            review_items.append("⚠ Missing documentation URL")

        # Version compliance
        if plugin.metadata.min_eq12_version:
            review_score += 10
            review_items.append("✓ EQ12 version compatibility specified")

        # Description quality
        if len(plugin.metadata.description) > 100:
            review_score += 10
            review_items.append("✓ Detailed description provided")
        else:
            review_items.append("⚠ Description could be more detailed")

        # Category appropriateness
        review_score += 10  # Assuming category is appropriate
        review_items.append("✓ Appropriate category selection")

        # Pricing reasonableness
        if plugin.pricing.model == RevenueModel.FREE:
            review_score += 15
            review_items.append("✓ Free plugin - good for ecosystem")
        elif plugin.pricing.base_price <= Decimal("100"):
            review_score += 10
            review_items.append("✓ Reasonable pricing")
        else:
            review_items.append("⚠ High pricing - ensure value justification")

        # Auto-approval threshold
        auto_approve = review_score >= 75

        if auto_approve:
            plugin.status = PluginStatus.APPROVED
            status = "auto_approved"
        else:
            status = "manual_review_required"

        return {
            "status": status,
            "score": review_score,
            "review_items": review_items,
            "auto_approved": auto_approve,
        }

    async def install_plugin(self, customer_id: str, plugin_id: str) -> dict:
        """Install plugin for customer"""

        if plugin_id not in self.plugins:
            return {"error": "Plugin not found"}

        plugin = self.plugins[plugin_id]

        if plugin.status != PluginStatus.APPROVED:
            return {"error": "Plugin not approved for installation"}

        # Check if already installed
        if customer_id in self.installations:
            if plugin_id in self.installations[customer_id]:
                return {"error": "Plugin already installed"}
        else:
            self.installations[customer_id] = []

        # Process payment if required
        if plugin.pricing.model != RevenueModel.FREE:
            payment_result = await self._process_plugin_payment(customer_id, plugin)
            if not payment_result["success"]:
                return {"error": "Payment failed", "details": payment_result}

        # Install plugin
        self.installations[customer_id].append(plugin_id)
        plugin.install_count += 1

        # Record revenue
        await self._record_plugin_revenue(customer_id, plugin_id, plugin.pricing.base_price)

        return {
            "status": "installed",
            "plugin_id": plugin_id,
            "plugin_name": plugin.metadata.name,
            "version": plugin.metadata.version,
            "installation_date": datetime.utcnow().isoformat(),
            "configuration_required": len(plugin.required_permissions) > 0,
        }

    async def _process_plugin_payment(self, customer_id: str, plugin: Plugin) -> dict:
        """Process plugin payment"""

        # In production, integrate with Stripe or payment processor
        # For now, simulate payment processing

        payment_amount = plugin.pricing.base_price

        # Simulate payment processing
        payment_success = True  # In reality, call payment processor

        if payment_success:
            return {
                "success": True,
                "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
                "amount": float(payment_amount),
                "currency": "USD",
            }
        return {"success": False, "error": "Payment processing failed"}

    async def _record_plugin_revenue(self, customer_id: str, plugin_id: str, amount: Decimal):
        """Record plugin revenue and calculate partner share"""

        plugin = self.plugins[plugin_id]
        partner_id = None

        # Find partner
        for pid, partner in self.partners.items():
            if plugin_id in partner.plugins:
                partner_id = pid
                break

        if partner_id:
            partner = self.partners[partner_id]
            partner_share = amount * partner.revenue_share_rate
            eq12_share = amount - partner_share

            # Record revenue
            revenue_record = {
                "id": f"rev_{uuid.uuid4().hex[:12]}",
                "customer_id": customer_id,
                "plugin_id": plugin_id,
                "partner_id": partner_id,
                "total_amount": float(amount),
                "partner_share": float(partner_share),
                "eq12_share": float(eq12_share),
                "revenue_share_rate": float(partner.revenue_share_rate),
                "timestamp": datetime.utcnow().isoformat(),
            }

            self.revenue_records.append(revenue_record)
            partner.total_revenue += partner_share
            plugin.revenue_generated += amount

    async def search_plugins(
        self,
        query: str | None = None,
        category: PluginCategory | None = None,
        pricing_model: RevenueModel | None = None,
        sort_by: str = "popularity",
    ) -> dict:
        """Search marketplace plugins"""

        results = []

        for plugin in self.plugins.values():
            if plugin.status != PluginStatus.APPROVED:
                continue

            # Apply filters
            if category and plugin.metadata.category != category:
                continue

            if pricing_model and plugin.pricing.model != pricing_model:
                continue

            if query:
                searchable_text = f"{plugin.metadata.name} {plugin.metadata.description} {' '.join(plugin.metadata.tags)}"
                if query.lower() not in searchable_text.lower():
                    continue

            # Add to results
            results.append(
                {
                    "id": plugin.id,
                    "name": plugin.metadata.name,
                    "description": plugin.metadata.description,
                    "category": plugin.metadata.category.value,
                    "author": plugin.metadata.author,
                    "version": plugin.metadata.version,
                    "pricing": {
                        "model": plugin.pricing.model.value,
                        "base_price": float(plugin.pricing.base_price),
                    },
                    "stats": {
                        "installs": plugin.install_count,
                        "rating": plugin.rating,
                        "reviews": plugin.review_count,
                    },
                    "tags": plugin.metadata.tags,
                }
            )

        # Sort results
        if sort_by == "popularity":
            results.sort(key=lambda x: x["stats"]["installs"], reverse=True)
        elif sort_by == "rating":
            results.sort(key=lambda x: x["stats"]["rating"], reverse=True)
        elif sort_by == "newest":
            results.sort(key=lambda x: self.plugins[x["id"]].created_at, reverse=True)
        elif sort_by == "price_low":
            results.sort(key=lambda x: x["pricing"]["base_price"])
        elif sort_by == "price_high":
            results.sort(key=lambda x: x["pricing"]["base_price"], reverse=True)

        return {
            "results": results,
            "total_count": len(results),
            "filters_applied": {
                "query": query,
                "category": category.value if category else None,
                "pricing_model": pricing_model.value if pricing_model else None,
            },
            "sort_by": sort_by,
        }

    async def get_plugin_details(self, plugin_id: str) -> dict:
        """Get detailed plugin information"""

        if plugin_id not in self.plugins:
            return {"error": "Plugin not found"}

        plugin = self.plugins[plugin_id]

        # Get recent reviews
        recent_reviews = self.reviews.get(plugin_id, [])[-5:]

        return {
            "id": plugin.id,
            "metadata": {
                "name": plugin.metadata.name,
                "description": plugin.metadata.description,
                "version": plugin.metadata.version,
                "category": plugin.metadata.category.value,
                "author": plugin.metadata.author,
                "homepage_url": plugin.metadata.homepage_url,
                "documentation_url": plugin.metadata.documentation_url,
                "support_url": plugin.metadata.support_url,
                "tags": plugin.metadata.tags,
                "supported_frameworks": plugin.metadata.supported_frameworks,
            },
            "pricing": {
                "model": plugin.pricing.model.value,
                "base_price": float(plugin.pricing.base_price),
                "recurring_period": plugin.pricing.recurring_period,
                "free_tier_limits": plugin.pricing.free_tier_limits,
            },
            "stats": {
                "installs": plugin.install_count,
                "rating": plugin.rating,
                "review_count": plugin.review_count,
                "revenue_generated": float(plugin.revenue_generated),
            },
            "technical": {
                "dependencies": plugin.dependencies,
                "required_permissions": plugin.required_permissions,
                "api_endpoints_count": len(plugin.api_endpoints),
            },
            "recent_reviews": recent_reviews,
            "created_at": plugin.created_at.isoformat(),
            "updated_at": plugin.updated_at.isoformat(),
        }

    async def generate_partner_revenue_report(
        self, partner_id: str, start_date: datetime, end_date: datetime
    ) -> dict:
        """Generate revenue report for partner"""

        if partner_id not in self.partners:
            return {"error": "Partner not found"}

        partner = self.partners[partner_id]

        # Filter revenue records for this partner and date range
        partner_revenues = [
            record
            for record in self.revenue_records
            if record["partner_id"] == partner_id
            and start_date <= datetime.fromisoformat(record["timestamp"]) <= end_date
        ]

        # Calculate metrics
        total_revenue = sum(record["partner_share"] for record in partner_revenues)
        total_transactions = len(partner_revenues)

        # Group by plugin
        plugin_breakdown = {}
        for record in partner_revenues:
            plugin_id = record["plugin_id"]
            if plugin_id not in plugin_breakdown:
                plugin_breakdown[plugin_id] = {
                    "plugin_name": self.plugins[plugin_id].metadata.name,
                    "revenue": 0.0,
                    "transactions": 0,
                }
            plugin_breakdown[plugin_id]["revenue"] += record["partner_share"]
            plugin_breakdown[plugin_id]["transactions"] += 1

        return {
            "partner_id": partner_id,
            "partner_name": partner.company_name,
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "summary": {
                "total_revenue": total_revenue,
                "total_transactions": total_transactions,
                "average_transaction": total_revenue / max(total_transactions, 1),
                "revenue_share_rate": float(partner.revenue_share_rate),
            },
            "plugin_breakdown": plugin_breakdown,
            "payment_schedule": "Monthly on the 15th",
            "next_payment_date": (end_date + timedelta(days=15)).strftime("%Y-%m-%d"),
        }

    async def featured_plugins(self) -> dict:
        """Get featured plugins for marketplace homepage"""

        # Select top plugins by different criteria
        most_popular = sorted(
            [p for p in self.plugins.values() if p.status == PluginStatus.APPROVED],
            key=lambda x: x.install_count,
            reverse=True,
        )[:3]

        highest_rated = sorted(
            [
                p
                for p in self.plugins.values()
                if p.status == PluginStatus.APPROVED and p.review_count > 0
            ],
            key=lambda x: x.rating,
            reverse=True,
        )[:3]

        newest = sorted(
            [p for p in self.plugins.values() if p.status == PluginStatus.APPROVED],
            key=lambda x: x.created_at,
            reverse=True,
        )[:3]

        def plugin_summary(plugin):
            return {
                "id": plugin.id,
                "name": plugin.metadata.name,
                "description": plugin.metadata.description[:100] + "...",
                "author": plugin.metadata.author,
                "category": plugin.metadata.category.value,
                "installs": plugin.install_count,
                "rating": plugin.rating,
                "price": float(plugin.pricing.base_price),
                "pricing_model": plugin.pricing.model.value,
            }

        return {
            "most_popular": [plugin_summary(p) for p in most_popular],
            "highest_rated": [plugin_summary(p) for p in highest_rated],
            "newest": [plugin_summary(p) for p in newest],
            "total_plugins": len(
                [p for p in self.plugins.values() if p.status == PluginStatus.APPROVED]
            ),
            "total_partners": len(self.partners),
            "marketplace_stats": {
                "total_downloads": sum(p.install_count for p in self.plugins.values()),
                "total_revenue": sum(float(p.revenue_generated) for p in self.plugins.values()),
                "active_plugins": len(
                    [p for p in self.plugins.values() if p.status == PluginStatus.APPROVED]
                ),
            },
        }


# Example usage
async def main():
    """Demonstrate plugin marketplace functionality"""

    marketplace = PluginMarketplace()

    # Register a partner
    print("Registering development partner...")
    partner_result = await marketplace.register_partner(
        {
            "company_name": "SecurityAI Solutions",
            "contact_email": "dev@securityai.com",
            "tier": "gold",
        }
    )
    print(f"Partner registered: {partner_result}")

    partner_id = partner_result["partner_id"]

    # Submit a plugin
    print("\nSubmitting plugin...")
    plugin_data = {
        "name": "Advanced PII Detector",
        "description": "AI-powered PII detection with 99.9% accuracy for GDPR compliance",
        "version": "1.2.3",
        "category": "compliance",
        "pricing": {
            "model": "subscription",
            "base_price": 299.99,
            "recurring_period": "monthly",
        },
        "min_eq12_version": "1.0.0",
        "tags": ["pii", "gdpr", "privacy", "ai"],
        "supported_frameworks": ["gdpr", "hipaa", "ccpa"],
        "required_permissions": ["data_read", "alert_create"],
        "dependencies": ["numpy>=1.21.0", "scikit-learn>=1.0.0"],
        "homepage_url": "https://securityai.com/pii-detector",
        "documentation_url": "https://docs.securityai.com/pii-detector",
        "support_url": "https://support.securityai.com",
    }

    plugin_result = await marketplace.submit_plugin(partner_id, plugin_data)
    print(f"Plugin submitted: {plugin_result}")

    plugin_id = plugin_result["plugin_id"]

    # Search plugins
    print("\nSearching plugins...")
    search_results = await marketplace.search_plugins(
        query="pii", category=PluginCategory.COMPLIANCE, sort_by="newest"
    )
    print(f"Search results: {len(search_results['results'])} plugins found")

    # Install plugin
    print("\nInstalling plugin...")
    install_result = await marketplace.install_plugin("customer_123", plugin_id)
    print(f"Installation result: {install_result}")

    # Generate partner revenue report
    print("\nGenerating revenue report...")
    revenue_report = await marketplace.generate_partner_revenue_report(
        partner_id, datetime.utcnow() - timedelta(days=30), datetime.utcnow()
    )
    print(f"Revenue report: {json.dumps(revenue_report, indent=2, default=str)}")


if __name__ == "__main__":
    asyncio.run(main())
