"""
EQ12 Billing and Subscription Management System
Automated usage tracking, metering, and Stripe integration
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum

import stripe

logger = logging.getLogger(__name__)


class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"
    USAGE_BASED = "usage_based"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    TRIALING = "trialing"


@dataclass
class UsageRecord:
    customer_id: str
    service_type: str  # governance_analysis, streaming_minutes, document_processing
    quantity: int
    unit_price: Decimal
    timestamp: datetime
    metadata: Optional[dict] = None


@dataclass
class BillingConfiguration:
    base_price: Decimal
    included_usage: int
    overage_rate: Decimal
    billing_cycle: BillingCycle
    features: list[str]


class EQ12BillingSystem:
    """Complete billing and subscription management system"""

    def __init__(self):
        # Initialize Stripe
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        # Pricing configurations
        self.pricing_tiers = {
            "starter": BillingConfiguration(
                base_price=Decimal("99.00"),
                included_usage=1000,
                overage_rate=Decimal("0.01"),
                billing_cycle=BillingCycle.MONTHLY,
                features=[
                    "basic_governance",
                    "standard_templates",
                    "community_support",
                ],
            ),
            "professional": BillingConfiguration(
                base_price=Decimal("499.00"),
                included_usage=10000,
                overage_rate=Decimal("0.008"),
                billing_cycle=BillingCycle.MONTHLY,
                features=[
                    "advanced_governance",
                    "custom_frameworks",
                    "priority_support",
                ],
            ),
            "enterprise": BillingConfiguration(
                base_price=Decimal("2999.00"),
                included_usage=100000,
                overage_rate=Decimal("0.005"),
                billing_cycle=BillingCycle.MONTHLY,
                features=["unlimited_governance", "white_label", "dedicated_manager"],
            ),
            "enterprise_plus": BillingConfiguration(
                base_price=Decimal("0.00"),  # Custom pricing
                included_usage=-1,  # Unlimited
                overage_rate=Decimal("0.003"),
                billing_cycle=BillingCycle.USAGE_BASED,
                features=["on_premises", "custom_training", "consulting"],
            ),
        }

        # Usage tracking
        self.usage_records = {}  # In production, use Redis or database

    async def create_customer_subscription(self, customer_data: dict) -> dict:
        """Create new customer and subscription in Stripe"""
        try:
            # Create Stripe customer
            customer = stripe.Customer.create(
                email=customer_data["email"],
                name=customer_data["company_name"],
                phone=customer_data.get("phone"),
                address=customer_data.get("address"),
                metadata={
                    "company": customer_data["company_name"],
                    "tier": customer_data["subscription_tier"],
                    "signup_source": customer_data.get("source", "api"),
                },
            )

            # Create subscription based on tier
            tier = customer_data["subscription_tier"]
            config = self.pricing_tiers[tier]

            if config.billing_cycle == BillingCycle.USAGE_BASED:
                # Usage-based billing - create metered subscription
                subscription = await self._create_usage_based_subscription(customer.id, tier)
            else:
                # Fixed pricing subscription
                subscription = await self._create_fixed_subscription(customer.id, tier, config)

            return {
                "customer_id": customer.id,
                "subscription_id": subscription.id,
                "status": "created",
                "tier": tier,
                "billing_cycle": config.billing_cycle.value,
                "next_billing_date": datetime.fromtimestamp(
                    subscription.current_period_end
                ).isoformat(),
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating subscription: {e}")
            raise Exception(f"Billing system error: {e}")

    async def _create_fixed_subscription(
        self, customer_id: str, tier: str, config: BillingConfiguration
    ):
        """Create fixed-price subscription"""

        # Create or get price object
        price = await self._get_or_create_price(tier, config)

        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price.id}],
            payment_behavior="default_incomplete",
            payment_settings={
                "save_default_payment_method": "on_subscription",
                "payment_method_types": ["card"],
            },
            expand=["latest_invoice.payment_intent"],
            metadata={
                "tier": tier,
                "included_usage": str(config.included_usage),
                "overage_rate": str(config.overage_rate),
            },
        )

        return subscription

    async def _create_usage_based_subscription(self, customer_id: str, tier: str):
        """Create usage-based metered subscription"""

        # Create metered price for governance calls
        governance_price = stripe.Price.create(
            unit_amount=300,  # $3.00 per 1000 calls
            currency="usd",
            recurring={
                "interval": "month",
                "usage_type": "metered",
                "aggregate_usage": "sum",
            },
            product_data={
                "name": f"EQ12 AI Governance Calls - {tier.title()}",
                "unit_label": "governance_call",
            },
            metadata={"service": "governance_analysis", "tier": tier},
        )

        # Create metered price for streaming minutes
        streaming_price = stripe.Price.create(
            unit_amount=5,  # $0.05 per minute
            currency="usd",
            recurring={
                "interval": "month",
                "usage_type": "metered",
                "aggregate_usage": "sum",
            },
            product_data={
                "name": f"EQ12 Streaming Minutes - {tier.title()}",
                "unit_label": "streaming_minute",
            },
            metadata={"service": "streaming_minutes", "tier": tier},
        )

        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": governance_price.id}, {"price": streaming_price.id}],
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            metadata={"tier": tier, "billing_type": "usage_based"},
        )

        return subscription

    async def _get_or_create_price(self, tier: str, config: BillingConfiguration):
        """Get existing price or create new one"""

        # Try to find existing price
        prices = stripe.Price.list(product_data={"metadata": {"tier": tier}}, active=True)

        if prices.data:
            return prices.data[0]

        # Create new price
        price = stripe.Price.create(
            unit_amount=int(config.base_price * 100),  # Convert to cents
            currency="usd",
            recurring={"interval": config.billing_cycle.value},
            product_data={
                "name": f"EQ12 AI Governance - {tier.title()}",
                "description": f"Monthly subscription for {tier} tier",
                "metadata": {
                    "tier": tier,
                    "included_usage": str(config.included_usage),
                },
            },
        )

        return price

    async def record_usage(self, usage_record: UsageRecord) -> dict:
        """Record usage for billing purposes"""

        # Store usage record (in production, use database)
        key = f"{usage_record.customer_id}:{usage_record.service_type}:{usage_record.timestamp.strftime('%Y-%m')}"

        if key not in self.usage_records:
            self.usage_records[key] = []

        self.usage_records[key].append(usage_record)

        # Report to Stripe for metered billing
        await self._report_usage_to_stripe(usage_record)

        return {
            "status": "recorded",
            "usage_id": f"usage_{usage_record.customer_id}_{int(usage_record.timestamp.timestamp())}",
            "quantity": usage_record.quantity,
            "unit_price": float(usage_record.unit_price),
            "total_cost": float(usage_record.quantity * usage_record.unit_price),
        }

    async def _report_usage_to_stripe(self, usage_record: UsageRecord):
        """Report usage to Stripe for metered billing"""
        try:
            # Get customer's subscription
            subscriptions = stripe.Subscription.list(
                customer=usage_record.customer_id, status="active"
            )

            if not subscriptions.data:
                logger.warning(
                    f"No active subscription found for customer {usage_record.customer_id}"
                )
                return

            subscription = subscriptions.data[0]

            # Find the appropriate subscription item
            for item in subscription.items.data:
                price_metadata = stripe.Price.retrieve(item.price.id).metadata
                if price_metadata.get("service") == usage_record.service_type:
                    # Create usage record in Stripe
                    stripe.SubscriptionItem.create_usage_record(
                        item.id,
                        quantity=usage_record.quantity,
                        timestamp=int(usage_record.timestamp.timestamp()),
                        action="increment",
                    )
                    break

        except stripe.error.StripeError as e:
            logger.error(f"Failed to report usage to Stripe: {e}")

    async def calculate_monthly_bill(self, customer_id: str, month: datetime) -> dict:
        """Calculate customer's monthly bill with usage charges"""

        # Get base subscription cost
        subscriptions = stripe.Subscription.list(customer=customer_id, status="active")

        if not subscriptions.data:
            return {"error": "No active subscription"}

        subscription = subscriptions.data[0]
        tier = subscription.metadata.get("tier", "starter")
        config = self.pricing_tiers[tier]

        base_cost = config.base_price

        # Calculate usage costs
        month_key = f"{customer_id}:{month.strftime('%Y-%m')}"
        usage_cost = Decimal("0.00")
        usage_details = {}

        # Get usage for all service types
        for service_type in [
            "governance_analysis",
            "streaming_minutes",
            "document_processing",
        ]:
            service_key = f"{month_key}:{service_type}"
            if service_key in self.usage_records:
                total_usage = sum(record.quantity for record in self.usage_records[service_key])

                # Calculate overage if applicable
                if config.included_usage > 0 and total_usage > config.included_usage:
                    overage = total_usage - config.included_usage
                    overage_cost = overage * config.overage_rate
                    usage_cost += overage_cost

                    usage_details[service_type] = {
                        "total_usage": total_usage,
                        "included": config.included_usage,
                        "overage": overage,
                        "overage_cost": float(overage_cost),
                    }
                else:
                    usage_details[service_type] = {
                        "total_usage": total_usage,
                        "included": config.included_usage,
                        "overage": 0,
                        "overage_cost": 0.0,
                    }

        total_cost = base_cost + usage_cost

        return {
            "customer_id": customer_id,
            "billing_period": month.strftime("%Y-%m"),
            "tier": tier,
            "base_cost": float(base_cost),
            "usage_cost": float(usage_cost),
            "total_cost": float(total_cost),
            "usage_details": usage_details,
            "next_billing_date": datetime.fromtimestamp(
                subscription.current_period_end
            ).isoformat(),
        }

    async def upgrade_subscription(self, customer_id: str, new_tier: str) -> dict:
        """Upgrade customer subscription to higher tier"""

        try:
            # Get current subscription
            subscriptions = stripe.Subscription.list(customer=customer_id, status="active")

            if not subscriptions.data:
                raise Exception("No active subscription found")

            subscription = subscriptions.data[0]
            current_tier = subscription.metadata.get("tier")

            # Validate upgrade path
            tier_hierarchy = [
                "starter",
                "professional",
                "enterprise",
                "enterprise_plus",
            ]
            if tier_hierarchy.index(new_tier) <= tier_hierarchy.index(current_tier):
                raise Exception("Can only upgrade to higher tiers")

            new_config = self.pricing_tiers[new_tier]

            # Create new price for the new tier
            new_price = await self._get_or_create_price(new_tier, new_config)

            # Update subscription
            updated_subscription = stripe.Subscription.modify(
                subscription.id,
                items=[{"id": subscription.items.data[0].id, "price": new_price.id}],
                proration_behavior="create_prorations",
                metadata={
                    "tier": new_tier,
                    "previous_tier": current_tier,
                    "upgrade_date": datetime.utcnow().isoformat(),
                },
            )

            return {
                "status": "upgraded",
                "previous_tier": current_tier,
                "new_tier": new_tier,
                "effective_date": datetime.utcnow().isoformat(),
                "next_billing_date": datetime.fromtimestamp(
                    updated_subscription.current_period_end
                ).isoformat(),
            }

        except stripe.error.StripeError as e:
            logger.error(f"Failed to upgrade subscription: {e}")
            raise Exception(f"Upgrade failed: {e}")

    async def handle_failed_payment(self, subscription_id: str) -> dict:
        """Handle failed payment scenarios"""

        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            customer = stripe.Customer.retrieve(subscription.customer)

            # Send notification email (integrate with email service)
            await self._send_payment_failure_notification(customer.email, subscription)

            # Apply grace period for enterprise customers
            tier = subscription.metadata.get("tier", "starter")
            if tier in ["enterprise", "enterprise_plus"]:
                # Enterprise gets 7-day grace period
                grace_period_end = datetime.utcnow() + timedelta(days=7)

                # Update subscription metadata
                stripe.Subscription.modify(
                    subscription_id,
                    metadata={
                        **subscription.metadata,
                        "grace_period_end": grace_period_end.isoformat(),
                        "payment_failed_date": datetime.utcnow().isoformat(),
                    },
                )

                return {
                    "status": "grace_period_applied",
                    "grace_period_end": grace_period_end.isoformat(),
                    "action_required": "update_payment_method",
                }
            # Standard customers get 3-day grace period
            grace_period_end = datetime.utcnow() + timedelta(days=3)

            return {
                "status": "payment_retry_scheduled",
                "grace_period_end": grace_period_end.isoformat(),
                "action_required": "update_payment_method",
            }

        except stripe.error.StripeError as e:
            logger.error(f"Failed to handle payment failure: {e}")
            raise Exception(f"Payment handling failed: {e}")

    async def _send_payment_failure_notification(self, email: str, subscription):
        """Send payment failure notification email"""
        # Integration point for email service (SendGrid, AWS SES, etc.)
        logger.info(f"Payment failure notification sent to {email}")

        # In production, implement actual email sending
        pass

    async def generate_usage_report(
        self, customer_id: str, start_date: datetime, end_date: datetime
    ) -> dict:
        """Generate detailed usage report for customer"""

        report_data = {
            "customer_id": customer_id,
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "services": {},
            "total_usage": 0,
            "total_cost": Decimal("0.00"),
        }

        # Aggregate usage by service type
        for service_type in [
            "governance_analysis",
            "streaming_minutes",
            "document_processing",
        ]:
            service_usage = []
            service_total = 0
            service_cost = Decimal("0.00")

            # Find usage records for the period
            for key, records in self.usage_records.items():
                if customer_id in key and service_type in key:
                    for record in records:
                        if start_date <= record.timestamp <= end_date:
                            service_usage.append(
                                {
                                    "timestamp": record.timestamp.isoformat(),
                                    "quantity": record.quantity,
                                    "unit_price": float(record.unit_price),
                                    "cost": float(record.quantity * record.unit_price),
                                    "metadata": record.metadata,
                                }
                            )
                            service_total += record.quantity
                            service_cost += record.quantity * record.unit_price

            report_data["services"][service_type] = {
                "total_usage": service_total,
                "total_cost": float(service_cost),
                "usage_records": service_usage,
            }

            report_data["total_usage"] += service_total
            report_data["total_cost"] += service_cost

        report_data["total_cost"] = float(report_data["total_cost"])

        return report_data

    async def apply_discount(
        self,
        customer_id: str,
        discount_type: str,
        value: float,
        duration_months: Optional[int] = None,
    ) -> dict:
        """Apply discount to customer subscription"""

        try:
            # Create Stripe coupon
            if discount_type == "percentage":
                coupon = stripe.Coupon.create(
                    percent_off=value,
                    duration="repeating" if duration_months else "forever",
                    duration_in_months=duration_months,
                    name=f"EQ12 {value}% Discount",
                )
            else:  # amount_off
                coupon = stripe.Coupon.create(
                    amount_off=int(value * 100),  # Convert to cents
                    currency="usd",
                    duration="repeating" if duration_months else "forever",
                    duration_in_months=duration_months,
                    name=f"EQ12 ${value} Discount",
                )

            # Apply to customer
            stripe.Customer.retrieve(customer_id)
            stripe.Customer.modify(customer_id, coupon=coupon.id)

            return {
                "status": "discount_applied",
                "coupon_id": coupon.id,
                "discount_type": discount_type,
                "discount_value": value,
                "duration_months": duration_months,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Failed to apply discount: {e}")
            raise Exception(f"Discount application failed: {e}")


# Usage examples and testing
async def main():
    """Example usage of the billing system"""

    EQ12BillingSystem()

    # Example: Create new customer subscription

    print("Creating enterprise subscription...")
    # subscription_result = await billing_system.create_customer_subscription(customer_data)
    # print(f"Subscription created: {subscription_result}")

    # Example: Record usage
    UsageRecord(
        customer_id="cust_example123",
        service_type="governance_analysis",
        quantity=150,
        unit_price=Decimal("0.01"),
        timestamp=datetime.utcnow(),
        metadata={"api_version": "v1", "endpoint": "/governance/analyze"},
    )

    print("Recording usage...")
    # usage_result = await billing_system.record_usage(usage_record)
    # print(f"Usage recorded: {usage_result}")

    # Example: Calculate monthly bill
    print("Calculating monthly bill...")
    # bill = await billing_system.calculate_monthly_bill("cust_example123", datetime.utcnow())
    # print(f"Monthly bill: {bill}")


if __name__ == "__main__":
    asyncio.run(main())
