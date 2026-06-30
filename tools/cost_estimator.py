"""
ProjectForge AI — Cloud Cost Estimator Tool

Heuristic-based cost estimation for common cloud services.
Covers AWS, GCP, and Azure with ballpark monthly estimates.
"""

from __future__ import annotations

# ─── Pricing Tables (approximate monthly USD, as of 2025-2026) ────────────────
# These are ballpark estimates for common configurations.
# Real costs vary by region, commitment, and usage patterns.

PRICING = {
    "compute": {
        "aws": {
            "small": {"name": "EC2 t3.small", "monthly": 15},
            "medium": {"name": "EC2 t3.medium", "monthly": 30},
            "large": {"name": "EC2 m5.large", "monthly": 70},
            "xlarge": {"name": "EC2 m5.xlarge", "monthly": 140},
        },
        "gcp": {
            "small": {"name": "e2-small", "monthly": 12},
            "medium": {"name": "e2-medium", "monthly": 25},
            "large": {"name": "n2-standard-2", "monthly": 65},
            "xlarge": {"name": "n2-standard-4", "monthly": 130},
        },
        "azure": {
            "small": {"name": "B1ms", "monthly": 14},
            "medium": {"name": "B2s", "monthly": 30},
            "large": {"name": "D2s_v5", "monthly": 70},
            "xlarge": {"name": "D4s_v5", "monthly": 140},
        },
    },
    "database": {
        "aws": {
            "small": {"name": "RDS db.t3.small (PostgreSQL)", "monthly": 25},
            "medium": {"name": "RDS db.t3.medium (PostgreSQL)", "monthly": 50},
            "large": {"name": "RDS db.m5.large (PostgreSQL)", "monthly": 140},
            "managed_nosql": {"name": "DynamoDB (25 WCU/RCU)", "monthly": 25},
        },
        "gcp": {
            "small": {"name": "Cloud SQL db-f1-micro", "monthly": 10},
            "medium": {"name": "Cloud SQL db-g1-small", "monthly": 35},
            "large": {"name": "Cloud SQL db-n1-standard-2", "monthly": 120},
            "managed_nosql": {"name": "Firestore (1M reads/day)", "monthly": 20},
        },
        "azure": {
            "small": {"name": "Azure DB Basic", "monthly": 15},
            "medium": {"name": "Azure DB Standard S1", "monthly": 30},
            "large": {"name": "Azure DB Standard S3", "monthly": 100},
            "managed_nosql": {"name": "Cosmos DB (400 RU/s)", "monthly": 25},
        },
    },
    "storage": {
        "aws": {"name": "S3", "per_gb": 0.023},
        "gcp": {"name": "Cloud Storage", "per_gb": 0.020},
        "azure": {"name": "Blob Storage", "per_gb": 0.018},
    },
    "cdn": {
        "aws": {"name": "CloudFront", "monthly": 15},
        "gcp": {"name": "Cloud CDN", "monthly": 12},
        "azure": {"name": "Azure CDN", "monthly": 15},
    },
    "monitoring": {
        "aws": {"name": "CloudWatch", "monthly": 10},
        "gcp": {"name": "Cloud Monitoring", "monthly": 0},
        "azure": {"name": "Azure Monitor", "monthly": 10},
    },
    "container_orchestration": {
        "aws": {"name": "ECS Fargate (2 tasks)", "monthly": 40},
        "gcp": {"name": "Cloud Run (2 instances)", "monthly": 30},
        "azure": {"name": "Container Apps (2 instances)", "monthly": 35},
    },
    "serverless": {
        "aws": {"name": "Lambda (1M requests)", "monthly": 5},
        "gcp": {"name": "Cloud Functions (1M requests)", "monthly": 4},
        "azure": {"name": "Azure Functions (1M requests)", "monthly": 5},
    },
    "cache": {
        "aws": {"name": "ElastiCache t3.small (Redis)", "monthly": 25},
        "gcp": {"name": "Memorystore (1GB Redis)", "monthly": 35},
        "azure": {"name": "Azure Cache Basic C0", "monthly": 16},
    },
    "message_queue": {
        "aws": {"name": "SQS (1M messages)", "monthly": 1},
        "gcp": {"name": "Pub/Sub (1M messages)", "monthly": 1},
        "azure": {"name": "Service Bus Basic", "monthly": 5},
    },
    "auth": {
        "aws": {"name": "Cognito (1K MAU)", "monthly": 0},
        "gcp": {"name": "Firebase Auth (10K MAU)", "monthly": 0},
        "azure": {"name": "Azure AD B2C (50K MAU)", "monthly": 0},
    },
}

# Scale multipliers based on expected user count
SCALE_MULTIPLIERS = {
    "tiny": 1.0,       # < 100 users
    "small": 1.0,      # 100-1K users
    "medium": 2.0,     # 1K-10K users
    "large": 5.0,      # 10K-100K users
    "massive": 15.0,   # 100K+ users
}


def estimate_cloud_costs(
    services: str,
    scale: str,
    provider: str = "aws",
) -> dict:
    """
    Estimate monthly cloud infrastructure costs based on services needed and scale.

    Args:
        services: Comma-separated list of services needed.
            Options: compute, database, storage, cdn, monitoring,
            container_orchestration, serverless, cache, message_queue, auth.
            Example: "compute,database,cache,monitoring"
        scale: Expected scale of the application.
            Options: tiny (<100 users), small (100-1K), medium (1K-10K),
            large (10K-100K), massive (100K+).
        provider: Cloud provider preference. Options: aws, gcp, azure.
            Defaults to 'aws'.

    Returns:
        A dictionary with itemized costs, total monthly and annual estimates,
        assumptions, and optimization tips.
    """
    provider = provider.lower()
    if provider not in ("aws", "gcp", "azure"):
        provider = "aws"

    scale = scale.lower()
    multiplier = SCALE_MULTIPLIERS.get(scale, 1.0)

    # Determine compute/db size based on scale
    if scale in ("tiny", "small"):
        size = "small"
    elif scale == "medium":
        size = "medium"
    elif scale == "large":
        size = "large"
    else:
        size = "xlarge"

    service_list = [s.strip().lower() for s in services.split(",")]
    line_items = []
    total = 0.0

    for service_name in service_list:
        if service_name not in PRICING:
            continue

        service_pricing = PRICING[service_name]

        if service_name == "storage":
            # Estimate storage based on scale
            storage_gb = {"tiny": 10, "small": 50, "medium": 200, "large": 1000, "massive": 5000}
            gb = storage_gb.get(scale, 50)
            provider_data = service_pricing.get(provider, service_pricing.get("aws"))
            cost = gb * provider_data["per_gb"]
            line_items.append({
                "service": provider_data["name"],
                "description": f"{gb} GB storage",
                "monthly_cost_usd": round(cost, 2),
            })
            total += cost
        elif isinstance(service_pricing.get(provider, {}), dict) and "monthly" in service_pricing.get(provider, {}):
            # Flat-rate services (cdn, monitoring, serverless, etc.)
            provider_data = service_pricing[provider]
            cost = provider_data["monthly"] * multiplier
            line_items.append({
                "service": provider_data["name"],
                "description": f"{service_name.replace('_', ' ').title()}",
                "monthly_cost_usd": round(cost, 2),
            })
            total += cost
        elif provider in service_pricing:
            # Sized services (compute, database, cache)
            provider_data = service_pricing[provider]
            if isinstance(provider_data, dict):
                if size in provider_data:
                    entry = provider_data[size]
                    cost = entry["monthly"] * multiplier
                    line_items.append({
                        "service": entry["name"],
                        "description": f"{service_name.replace('_', ' ').title()} ({size})",
                        "monthly_cost_usd": round(cost, 2),
                    })
                    total += cost

    # Optimization tips
    optimization_tips = []
    if scale in ("tiny", "small"):
        optimization_tips.append(
            "At this scale, consider a Platform-as-a-Service (Railway, Render, Fly.io) "
            "instead of raw cloud — often cheaper and simpler."
        )
    if "cache" in service_list:
        optimization_tips.append(
            "Evaluate if application-level caching (e.g., in-memory LRU) "
            "is sufficient before paying for managed Redis."
        )
    if multiplier >= 5.0:
        optimization_tips.append(
            "At this scale, investigate reserved instances or committed-use "
            "discounts — can save 30-60% on compute and database."
        )
    if "serverless" in service_list and "compute" in service_list:
        optimization_tips.append(
            "You're using both serverless and dedicated compute. "
            "Consider consolidating to reduce operational overhead."
        )

    assumptions = [
        f"Pricing is approximate and based on {provider.upper()} public pricing (2025-2026)",
        f"Scale assumption: {scale} ({SCALE_MULTIPLIERS[scale]}x base capacity)",
        "Does not include data transfer/egress costs (can add 10-30%)",
        "Does not include CI/CD pipeline costs",
        "Reserved/committed pricing not applied (on-demand rates)",
    ]

    return {
        "provider": provider.upper(),
        "scale": scale,
        "line_items": line_items,
        "total_monthly_usd": round(total, 2),
        "total_annual_usd": round(total * 12, 2),
        "assumptions": assumptions,
        "optimization_tips": optimization_tips,
    }
