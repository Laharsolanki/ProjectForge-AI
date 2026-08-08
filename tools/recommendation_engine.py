"""
ProjectForge AI — Curated Stacks & Recommendation Tool

Provides a structured list of supported stacks, architecture patterns, and recommendations for students.
"""

from __future__ import annotations
from typing import Optional

CURATED_STACKS = {
    "frontend": [
        {
            "name": "Svelte / SvelteKit",
            "category": "Frontend",
            "paradigm": "Compiler-driven reactive component framework",
            "why_it_teaches": "Teaches compiler-based reactivity, minimal boilerplate, and high performance without virtual DOM overhead.",
            "why_preferred_over_familiar": "Unlike React's virtual DOM or heavy standard setups, Svelte compiles components down to tiny, framework-less JS, teaching a completely different paradigm of reactive UI development.",
            "what_to_learn_first": "Basic Svelte reactivity (reactive declarations $:), component props, and SvelteKit's file-based routing system."
        },
        {
            "name": "Astro",
            "category": "Frontend",
            "paradigm": "Zero-JS Islands Architecture & Content-Driven Multi-Page Apps",
            "why_it_teaches": "Teaches static site generation (SSG), partial hydration, and 'Islands Architecture' for ultra-fast load times.",
            "why_preferred_over_familiar": "Unlike single-page apps (SPAs) that load heavy JS bundles, Astro is zero-JS by default and teaches how to only hydrate interactive islands, improving real-world performance concepts.",
            "what_to_learn_first": "Astro page structure, routing, and importing interactive components from other frameworks as island components."
        },
        {
            "name": "React / Next.js",
            "category": "Frontend",
            "paradigm": "Declarative Component UI & Hybrid Server-Client Rendering",
            "why_it_teaches": "Teaches client-side state management, virtual DOM reconciliation, hooks, and React Server Components (RSC).",
            "why_preferred_over_familiar": "Unlike traditional HTML/JS or templating engines, React forces developers to think in declarative UI states, reusable components, and server-client boundaries.",
            "what_to_learn_first": "Essential React hooks (useState, useEffect), Next.js App Router folders, and Server Actions."
        }
    ],
    "backend": [
        {
            "name": "Go (Gin or Fiber)",
            "category": "Backend",
            "paradigm": "Statically-typed compiled language with lightweight concurrency",
            "why_it_teaches": "Teaches statically-typed languages, concurrency using goroutines and channels, and high-performance minimal runtime backends.",
            "why_preferred_over_familiar": "Unlike Python or Node.js which rely on dynamic typing and single-threaded event loops, Go introduces explicit concurrency, type safety, and compiling to a single deployment binary.",
            "what_to_learn_first": "Go basic syntax, pointers vs values, structs, goroutines/channels, and building a basic router using Gin/Fiber."
        },
        {
            "name": "FastAPI (Python)",
            "category": "Backend",
            "paradigm": "Asynchronous typed REST API framework with OpenAPI schema validation",
            "why_it_teaches": "Teaches modern asynchronous Python programming, type annotations, automatic data serialization/validation with Pydantic, and OpenAPI standards.",
            "why_preferred_over_familiar": "Unlike Django or Flask, FastAPI leverages Python's modern type hinting to automatically generate API documentation, validate incoming schemas, and handle requests asynchronously.",
            "what_to_learn_first": "Python async/await model, Pydantic model declarations, path and query parameter types, and Dependency Injection basics."
        },
        {
            "name": "Rust (Axum or Actix-web)",
            "category": "Backend",
            "paradigm": "Systems programming with compile-time memory safety & zero-cost abstractions",
            "why_it_teaches": "Teaches memory safety without a garbage collector, compiler ownership and borrowing mechanics, and thread-safe systems programming.",
            "why_preferred_over_familiar": "Unlike standard garbage-collected backend languages, Rust enforces absolute correctness at compile time, teaching developers deep concepts of resource management and concurrency safety.",
            "what_to_learn_first": "Rust ownership system, borrowing/lifetimes, standard Error Handling using Result/Option, and routing with Axum."
        }
    ],
    "database": [
        {
            "name": "PostgreSQL",
            "category": "Database",
            "paradigm": "Relational ACID database with rich indexing and relational schema constraints",
            "why_it_teaches": "Teaches relational database design (relational algebra, ACID transactions), complex SQL queries, index optimization, and data integrity constraints.",
            "why_preferred_over_familiar": "Unlike SQLite (which has loose typing and is file-based) or NoSQL databases, PostgreSQL is a fully featured production-ready system teaching indexes, constraints, and migrations.",
            "what_to_learn_first": "SQL basic syntax, establishing foreign key relations, writing joins (INNER/LEFT JOIN), and managing migrations."
        },
        {
            "name": "MongoDB",
            "category": "Database",
            "paradigm": "Document-oriented schema-flexible NoSQL store with aggregation pipelines",
            "why_it_teaches": "Teaches document-oriented schema design, flexible hierarchical JSON document models, dynamic indexing, and aggregate pipelines.",
            "why_preferred_over_familiar": "Unlike rigid relational databases, MongoDB teaches how to structure and query nested, unstructured, or highly dynamic document hierarchies.",
            "what_to_learn_first": "CRUD operations in MongoDB shell, embedding vs referencing documents, indexing strategies, and basic aggregation queries."
        },
        {
            "name": "Supabase or Firebase",
            "category": "Database",
            "paradigm": "Backend-as-a-Service (BaaS) with Row Level Security and Real-Time Sockets",
            "why_it_teaches": "Teaches Backend-as-a-Service (BaaS) architectural patterns, real-time database socket subscriptions, and Row Level Security (RLS) data policies.",
            "why_preferred_over_familiar": "Unlike classical databases accessed through a custom API server, BaaS teaches client-direct database access and serverless authorization paradigms.",
            "what_to_learn_first": "Setting up real-time table listeners, writing Row Level Security (RLS) policies, and integrating the client SDK."
        }
    ]
}

ARCHITECTURE_PATTERNS = {
    "decoupled_spa_api": {
        "name": "Decoupled Single-Page App (SPA) + REST API",
        "description": "Frontend (e.g. Svelte/React) built and served separately from the Backend API service (e.g. Go/FastAPI/Rust).",
        "best_for": "Clean separation of concerns, independent scaling, and learning modern frontend/backend API contracts.",
        "tradeoffs": "Requires handling CORS, token-based authentication (JWT), and managing two separate runtime environments."
    },
    "fullstack_framework": {
        "name": "Fullstack Integrated Framework (e.g. SvelteKit / Next.js)",
        "description": "Single unified codebase handling client-side components and server-side endpoints/actions.",
        "best_for": "Fast developer velocity, type-sharing between client and server, and simplified deployments.",
        "tradeoffs": "Ties backend tightly to JavaScript/TypeScript ecosystem; less educational if the goal is to learn a dedicated backend language like Go or Rust."
    },
    "baas_serverless": {
        "name": "Frontend + Backend-as-a-Service (BaaS, e.g. Supabase / Firebase)",
        "description": "Client application communicating directly with a managed database and auth provider using Row Level Security (RLS).",
        "best_for": "Rapid MVPs, real-time sync, and learning security rule design without maintaining backend server infrastructure.",
        "tradeoffs": "Business logic is managed via client rules, database functions, or edge functions rather than a centralized API server."
    }
}


def get_supported_technologies() -> dict:
    """
    Get the curated database of supported technologies for recommendations.

    Returns:
        A dictionary containing the lists of curated frontend, backend, and database technologies.
    """
    return CURATED_STACKS


def get_architecture_patterns() -> dict:
    """
    Get standard architectural patterns suitable for student projects and MVPs.

    Returns:
        A dictionary of architecture patterns with descriptions, use cases, and trade-offs.
    """
    return ARCHITECTURE_PATTERNS


def filter_recommendations_for_student(
    learning_focus: list[str],
    familiar_technologies: list[str],
    preferred_language: Optional[str] = None,
) -> dict:
    """
    Helper function to filter and recommend candidate technologies tailored to teach new skills.

    Args:
        learning_focus: Categories the student wants to learn ('Frontend', 'Backend', 'Database').
        familiar_technologies: List of technology names the student is already comfortable with.
        preferred_language: Optional programming language preference.

    Returns:
        A dictionary mapping each learning focus area to candidate recommendation options.
    """
    familiar_lower = {t.lower().strip() for t in familiar_technologies}
    recommendations = {}

    for focus in learning_focus:
        cat_key = focus.lower().strip()
        if cat_key not in CURATED_STACKS:
            continue

        options = CURATED_STACKS[cat_key]
        unfamiliar_options = []

        for opt in options:
            name_lower = opt["name"].lower()
            # If the student's familiar list doesn't mention this tool
            is_familiar = any(fam in name_lower or name_lower in fam for fam in familiar_lower if fam)
            if not is_familiar:
                unfamiliar_options.append(opt)

        # If user has no unfamiliar options in this category, return all options sorted by modern learning value
        if not unfamiliar_options:
            unfamiliar_options = options

        recommendations[cat_key] = unfamiliar_options

    return recommendations
