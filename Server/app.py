from typing import List
from fastapi import FastAPI, HTTPException
from common import DeliveryAgentInfo, Parcel, create_agents, create_parcels
from node import Node, NodeOptions

user_parcels: List[Parcel] = []
user_agents: List[DeliveryAgentInfo] = []
root_node: None | Node = None
no_of_nodes: int | None = None

app = FastAPI()


def serialize(node: Node):
    all_nodes = list(node.get_all_nodes(set()))
    for node in all_nodes:
        node.neighbours = [n.id for n in node.neighbours]  # type: ignore
    return all_nodes


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
        raise HTTPException(400, detail="Initialize Map First")

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


@app.get("/simulate")
def simulate():
    import test_algos.GA

    global user_agents, user_parcels, root_node

    if root_node is None:
        raise HTTPException(400, detail="Initialize Map First")
    elif len(user_agents) == 0:
        raise HTTPException(400, detail="Initialize User Agents First")
    elif len(user_parcels) == 0:
        raise HTTPException(400, detail="Initialize User Parcels First")
    else:
        return test_algos.GA.model(root_node, user_parcels, user_agents)


# TODO: Main Sidebar
# Map button
# Parcels button
# Agents Button
# Run Button
