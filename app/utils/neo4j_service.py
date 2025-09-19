from typing import Any, Dict, List
from neo4j import GraphDatabase, AsyncGraphDatabase, AsyncManagedTransaction
from app.core.config import config

# -------------------- Shared queries --------------------
CAR_NODE_QUERY = """
MERGE (u:User {id: $user_id})
MERGE (c:Car {id: $car_id})
SET c.name = $name, c.year = $year, c.category = $category
MERGE (u)-[:OWNS]->(c)
WITH c
MERGE (m:Make {id: $make_id})
MERGE (c)-[:BELONGS_TO]->(m)
"""

USER_NODE_QUERY = """
MERGE (u:User {id: $id})
SET u.username = $username,
    u.email = $email,
    u.created_at = $created_at,
    u.updated_at = $updated_at
RETURN u
"""

# ==================== ASYNC DRIVER FOR FASTAPI ====================
driver_async = AsyncGraphDatabase.driver(
    config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
)

# -------------------- Async functions --------------------
async def create_user_node_async(
    tx: AsyncManagedTransaction,
    id: int,
    username: str,
    email: str,
    created_at: str,
    updated_at: str,
) -> None:
    """Create or update a User node in Neo4j (async)."""
    await tx.run(
        USER_NODE_QUERY,
        id=id,
        username=username,
        email=email,
        created_at=created_at,
        updated_at=updated_at,
    )

async def create_car_node_async(
    tx: AsyncManagedTransaction,
    car_id: int,
    name: str,
    year: int,
    category: str,
    make_id: int,
    user_id: int,
) -> None:
    """Create or update a Car node in Neo4j (async)."""
    await tx.run(
        CAR_NODE_QUERY,
        user_id=user_id,
        car_id=car_id,
        name=name,
        year=year,
        category=category,
        make_id=make_id,
    )

async def update_car_node_async(
    tx: AsyncManagedTransaction,
    car_id: int,
    updates: Dict[str, Any],
) -> None:
    """Update Car node properties (async)."""
    if not updates:
        return

    node_updates = {k: v for k in updates if k in {"name", "year", "category"}}
    if node_updates:
        set_clauses = [f"c.{k} = ${k}" for k in node_updates.keys()]
        query = f"""
        MATCH (c:Car {{id: $car_id}})
        SET {', '.join(set_clauses)}
        """
        params = {"car_id": car_id, **node_updates}
        await tx.run(query, **params)

    if "make_id" in updates and updates["make_id"] is not None:
        query = """
        MATCH (c:Car {id: $car_id})
        OPTIONAL MATCH (c)-[r:BELONGS_TO]->(:Make)
        DELETE r
        WITH c
        MERGE (m:Make {id: $make_id})
        MERGE (c)-[:BELONGS_TO]->(m)
        """
        params = {"car_id": car_id, "make_id": updates["make_id"]}
        await tx.run(query, **params)

async def delete_car_node_async(tx: AsyncManagedTransaction, car_id: int) -> None:
    """Delete a Car node in Neo4j (async)."""
    await tx.run("MATCH (c:Car {id: $car_id}) DETACH DELETE c", car_id=car_id)

async def get_user_cars_async(tx: AsyncManagedTransaction, user_id: int) -> List[Dict[str, Any]]:
    """Fetch all cars owned by a user (async)."""
    query = """
    MATCH (u:User {id: $user_id})-[:OWNS]->(c:Car)
    RETURN c { .* } AS car
    ORDER BY c.id
    """
    result = await tx.run(query, user_id=user_id)
    records = await result.to_list()
    return [record["car"] for record in records]

# ==================== SYNC DRIVER FOR CELERY ====================
driver_sync = GraphDatabase.driver(
    config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
)

# -------------------- Sync functions --------------------
def create_user_node_sync(
    id: int,
    username: str,
    email: str,
    created_at: str,
    updated_at: str,
) -> None:
    """Create or update a User node in Neo4j (sync)."""
    with driver_sync.session() as session:
        session.write_transaction(
            lambda tx: tx.run(
                USER_NODE_QUERY,
                id=id,
                username=username,
                email=email,
                created_at=created_at,
                updated_at=updated_at,
            )
        )

def create_car_node_sync(car_id: int, name: str, year: int, category: str, make_id: int, user_id: int) -> None:
    """Create or update a Car node in Neo4j (sync)."""
    with driver_sync.session() as session:
        session.write_transaction(
            lambda tx: tx.run(
                CAR_NODE_QUERY,
                user_id=user_id,
                car_id=car_id,
                name=name,
                year=year,
                category=category,
                make_id=make_id,
            )
        )

def update_car_node_sync(car_id: int, updates: Dict[str, Any]) -> None:
    """Update Car node properties (sync)."""
    if not updates:
        return
    with driver_sync.session() as session:
        # Node updates
        node_updates = {k: v for k, v in updates.items() if k in {"name", "year", "category"}}
        if node_updates:
            set_clauses = [f"c.{k} = ${k}" for k in node_updates.keys()]
            query = f"""
            MATCH (c:Car {{id: $car_id}})
            SET {', '.join(set_clauses)}
            """
            session.write_transaction(lambda tx: tx.run(query, car_id=car_id, **node_updates))

        # Relationship updates
        if "make_id" in updates and updates["make_id"] is not None:
            query = """
            MATCH (c:Car {id: $car_id})
            OPTIONAL MATCH (c)-[r:BELONGS_TO]->(:Make)
            DELETE r
            WITH c
            MERGE (m:Make {id: $make_id})
            MERGE (c)-[:BELONGS_TO]->(m)
            """
            session.write_transaction(lambda tx: tx.run(query, car_id=car_id, make_id=updates["make_id"]))

