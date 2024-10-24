from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from Server.simulate import get_route
from common import DeliveryAgentInfo, Parcel, Route, create_agents, create_parcels
from node import Node, NodeOptions
import logging
import uvicorn
from Simulator import Simulator
import Algos.GA

user_parcels: List[Parcel] = []
user_agents: List[DeliveryAgentInfo] = []
root_node: None | Node = None
no_of_nodes: int | None = None

app = FastAPI()
logger = logging.getLogger("uvicorn")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def serialize(node: Node):
    all_nodes = node.get_all_nodes(set())
    nodes = []
    for node in all_nodes:
        n = Node(node.x, node.y, node.color, node.id)
        n.neighbours = [n.id for n in node.neighbours]  # type: ignore
        nodes.append(n)
    return nodes


# TODO: Parcel Options Sidebar
# Change Parcel Information (Id cannot be changed, Location picked from map. Id always starting from zero to num_of_agents)
# Reroll Parcel Information
# Add and Remove Parcels
# On Hover Highlight location


@app.get("/parcels")
def get_parcels():
    global user_parcels
    return user_parcels


@app.post("/parcels")
def reroll_parcels(
    seed: int = 0,
    min_parcels: int = 20,
    max_parcels: int = 50,
):
    global user_parcels, no_of_nodes
    if no_of_nodes is None:
        raise HTTPException(400, detail="Initialize Map First")

    user_parcels = create_parcels(no_of_nodes, seed, min_parcels, max_parcels)
    return user_parcels


@app.put("/parcels")
def update_parcel(parcels: List[Parcel]):
    global user_parcels
    user_parcels = [Parcel(i, parcel.location) for i, parcel in enumerate(parcels)]
    return user_parcels


# TODO: Agent Options Sidebar
# Change Agent Information (Id cannot be changed, others can. Id always starting from zero to num_of_agents)
# Reroll Agent Information
# Add and Remove Agents


@app.get("/agents")
def get_agents():
    global user_agents
    return user_agents


@app.post("/agents")
def reroll_agents(
    seed: int = 0,
    min_agents: int = 3,
    max_agents: int = 5,
    min_capacity: int = 5,
    max_capacity: int = 10,
    min_dist: float = 500,
    max_dist: float = 5000,
):
    global user_agents
    user_agents = create_agents(
        seed,
        min_agents,
        max_agents,
        min_capacity,
        max_capacity,
        min_dist,
        max_dist,
    )
    return user_agents


@app.put("/agents")
def update_agents(agents: List[DeliveryAgentInfo]):
    global user_agents
    user_agents = [
        DeliveryAgentInfo(i, agent.max_capacity, agent.max_dist)
        for i, agent in enumerate(agents)
    ]
    return user_agents


# TODO: Map Options Sidebar
# Change Map Settings and Recreate Map. Map Recreation always rerolls invalid parcels
# TODO: Render Map


@app.get("/map")
def get_map():
    global no_of_nodes, root_node
    if root_node is None or no_of_nodes is None:
        return {"no_of_nodes": 0, "nodes": None}
    return {"no_of_nodes": no_of_nodes, "nodes": serialize(root_node)}


@app.post("/map")
def create_map(
    seed: int = 0,
    root_splits: int = 20,
    turn_around_chance: float = 0.5,
    split_chance: float = 0.2,
    max_split: int = 4,
    min_split: int = 1,
    min_dist: int = 20,
    max_dist: int = 200,
    angle_range: int = 75,
    min_depth: int = 3,
    max_depth: int = 6,
    merge_distance: int = 30,
    return_angle_range: int = 60,
):
    global root_node, no_of_nodes
    root_node = Node(0, 0, (0, 0, 0), 0)
    no_of_nodes = root_node.create(
        NodeOptions(
            seed=seed,
            root_splits=root_splits,
            turn_around_chance=turn_around_chance,
            split_chance=split_chance,
            max_split=max_split,
            min_split=min_split,
            min_dist=min_dist,
            max_dist=max_dist,
            angle_range=angle_range,
            min_depth=min_depth,
            max_depth=max_depth,
            merge_distance=merge_distance,
            return_angle_range=return_angle_range,
        )
    )
    return {"no_of_nodes": no_of_nodes, "nodes": serialize(root_node)}


# TODO:
# Render Parcels in Warehouse in the sidebar (On hover highlight agent/warehouse. Removed when delivered)
# Stop button at bottom of sidebar
# Render All Agents and the parcels carried by them


def sanitize_route(ro: List[Parcel | None]):
    route = [ro[0]]

    for r in ro[1:]:
        if r is None and route[-1] is None:
            continue

        route.append(r)

    return route


def sanitize_path(ro: List[int]):
    path = [ro[0]]
    for r in ro[1:]:
        if r == path[-1]:
            continue
        path.append(r)
    return path


def get_path(ro: List[Parcel | None]):
    global root_node
    path = []
    if root_node is None:
        raise HTTPException(400, detail="Initialize Map First")
    node = root_node

    for r in ro:
        if r is None:
            continue
        p, node = get_route(node, r.location)
        p.reverse()
        path.extend(p)

    return sanitize_path(path)


@app.get("/simulate")
def simulate():
    logger.info("Simulating")

    global user_agents, user_parcels, root_node

    if root_node is None:
        raise HTTPException(400, detail="Initialize Map First")
    elif len(user_agents) == 0:
        raise HTTPException(400, detail="Initialize User Agents First")
    elif len(user_parcels) == 0:
        raise HTTPException(400, detail="Initialize User Parcels First")
    else:
        route = test_algos.GA.model(
            root_node,
            user_parcels,
            user_agents,
        )
        simulator = Simulator(root_node, user_parcels)
        allocations = [{a: r.get_allocation() for a, r in route.items()}]
        _, total_parcels, total_distance = simulator.simulate(allocations)[0]
        agent_results = simulator.get_agent_results(0)

        return {
            "summary": {
                "total_distance": total_distance,
                "total_parcels": total_parcels,
            },
            "per_agent": [
                {
                    "agent": a,
                    "route": sanitize_route(r.route),
                    "path": get_path(r.route),
                    "performance": {
                        "parcels_delivered": ar[1],
                        "distance_travelled": ar[2],
                    }
                    if ar[0]
                    else None,
                }
                for (a, r), ar in zip(route.items(), agent_results)
            ],
        }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
