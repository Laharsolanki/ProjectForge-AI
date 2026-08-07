"""
ProjectForge AI — Curated Stacks & Recommendation Tool

Provides a structured list of supported stacks and recommendations for students.
"""

from __future__ import annotations

CURATED_STACKS = {
    "frontend": [
        {
            "name": "Svelte / SvelteKit",
            "why_it_teaches": "Teaches compiler-based reactivity, minimal boilerplate, and high performance without virtual DOM overhead.",
            "why_preferred_over_familiar": "Unlike React's virtual DOM or heavy standard setups, Svelte compiles components down to tiny, framework-less JS, teaching a completely different paradigm of reactive UI development.",
            "what_to_learn_first": "Basic Svelte reactivity (reactive declarations $:), component props, and SvelteKit's file-based routing system."
        },
        {
            "name": "Astro",
            "why_it_teaches": "Teaches static site generation (SSG), partial hydration, and 'Islands Architecture' for ultra-fast load times.",
            "why_preferred_over_familiar": "Unlike single-page apps (SPAs) that load heavy JS bundles, Astro is zero-JS by default and teaches how to only hydrate interactive islands, improving real-world performance concepts.",
            "what_to_learn_first": "Astro page structure, routing, and importing interactive components from other frameworks as island components."
        },
        {
            "name": "React / Next.js",
            "why_it_teaches": "Teaches client-side state management, virtual DOM reconciliation, hooks, and React Server Components (RSC).",
            "why_preferred_over_familiar": "Unlike traditional HTML/JS or templating engines, React forces developers to think in declarative UI states, reusable components, and server-client boundaries.",
            "what_to_learn_first": "Essential React hooks (useState, useEffect), Next.js App Router folders, and Server Actions."
        }
    ],
    "backend": [
        {
            "name": "Go (Gin or Fiber)",
            "why_it_teaches": "Teaches statically-typed languages, concurrency using goroutines and channels, and high-performance minimal runtime backends.",
            "why_preferred_over_familiar": "Unlike Python or Node.js which rely on dynamic typing and single-threaded event loops, Go introduces explicit concurrency, type safety, and compiling to a single deployment binary.",
            "what_to_learn_first": "Go basic syntax, pointers vs values, structs, goroutines/channels, and building a basic router using Gin/Fiber."
        },
        {
            "name": "FastAPI (Python)",
            "why_it_teaches": "Teaches modern asynchronous Python programming, type annotations, automatic data serialization/validation with Pydantic, and OpenAPI standards.",
            "why_preferred_over_familiar": "Unlike Django or Flask, FastAPI leverages Python's modern type hinting to automatically generate API documentation, validate incoming schemas, and handle requests asynchronously.",
            "what_to_learn_first": "Python async/await model, Pydantic model declarations, path and query parameter types, and Dependency Injection basics."
        },
        {
            "name": "Rust (Axum or Actix-web)",
            "why_it_teaches": "Teaches memory safety without a garbage collector, compiler ownership and borrowing mechanics, and thread-safe systems programming.",
            "why_preferred_over_familiar": "Unlike standard garbage-collected backend languages, Rust enforces absolute correctness at compile time, teaching developers deep concepts of resource management and concurrency safety.",
            "what_to_learn_first": "Rust ownership system, borrowing/lifetimes, standard Error Handling using Result/Option, and routing with Axum."
        }
    ],
    "database": [
        {
            "name": "PostgreSQL",
            "why_it_teaches": "Teaches relational database design (relational algebra, ACID transactions), complex SQL queries, index optimization, and data integrity constraints.",
            "why_preferred_over_familiar": "Unlike SQLite (which has loose typing and is file-based) or NoSQL databases, PostgreSQL is a fully featured production-ready system teaching indexes, constraints, and migrations.",
            "what_to_learn_first": "SQL basic syntax, establishing foreign key relations, writing joins (INNER/LEFT JOIN), and managing migrations."
        },
        {
            "name": "MongoDB",
            "why_it_teaches": "Teaches document-oriented schema design, flexible hierarchical JSON document models, dynamic indexing, and aggregate pipelines.",
            "why_preferred_over_familiar": "Unlike rigid relational databases, MongoDB teaches how to structure and query nested, unstructured, or highly dynamic document hierarchies.",
            "what_to_learn_first": "CRUD operations in MongoDB shell, embedding vs referencing documents, indexing strategies, and basic aggregation queries."
        },
        {
            "name": "Supabase or Firebase",
            "why_it_teaches": "Teaches Backend-as-a-Service (BaaS) architectural patterns, real-time database socket subscriptions, and Row Level Security (RLS) data policies.",
            "why_preferred_over_familiar": "Unlike classical databases accessed through a custom API server, BaaS teaches client-direct database access and serverless authorization paradigms.",
            "what_to_learn_first": "Setting up real-time table listeners, writing Row Level Security (RLS) policies, and integrating the client SDK."
        }
    ]
}


def get_supported_technologies() -> dict:
    """
    Get the curated database of supported technologies for recommendations.

    Returns:
        A dictionary containing the lists of curated frontend, backend, and database technologies.
    """
    return CURATED_STACKS
