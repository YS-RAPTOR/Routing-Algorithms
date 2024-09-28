import axios from "axios";
import { CreateNodeArray, Node, Relationship } from "./types";
import { create } from "zustand";

// Stores for all the state
// 5 stores: nodes, unique_relationships, parcels, agents, routes, highlighted color/None
type Parcel = {
    id: number;
    location: number;
};
type Agent = {
    id: number;
    max_capacity: number;
    max_dist: number;
};
type Store = {
    nodes: Node[];
    relationships: Relationship[];
    updateNodesAndRelationships: (
        nodes: Node[],
        relationships: Relationship[],
    ) => void;
    highlight_color: string | null;
    updateHighlightColor: (color: string | null) => void;

    isLoading: boolean;
    routes: Map<number, number[]> | null;
    updateRoutes: (routes: Map<number, number[]> | null) => void;
    updateIsLoading: (isLoading: boolean) => void;

    parcels: Parcel[];
    updateParcels: (parcels: Parcel[]) => void;

    agents: Agent[];
    updateAgents: (agents: Agent[]) => void;

    isPicking: boolean;
    updateIsPicking: (isPicking: boolean) => void;
};

export const useStore = create<Store>((set) => ({
    nodes: [],
    relationships: [],
    updateNodesAndRelationships: (
        nodes: Node[],
        relationships: Relationship[],
    ) => {
        set({ nodes, relationships });
    },

    highlight_color: null,
    updateHighlightColor: (highlight_color: string | null) => {
        set({ highlight_color });
    },

    isLoading: false,
    routes: null,
    updateRoutes: (routes: Map<number, number[]> | null) => {
        set({ routes });
    },
    updateIsLoading: (isLoading: boolean) => {
        set({ isLoading });
    },

    parcels: [] as Parcel[],
    updateParcels: (parcels: Parcel[]) => {
        set({ parcels });
    },

    agents: [] as Agent[],
    updateAgents: (agents: Agent[]) => {
        set({ agents });
    },

    isPicking: false,
    updateIsPicking: (isPicking: boolean) => {
        set({ isPicking });
    },
}));

// Create axios instance
export const axiosInstance = axios.create({
    baseURL: "http://localhost:8000",
});

export const getParcels = async () => {
    return axiosInstance.get("/parcels").then((response) => {
        useStore.getState().updateParcels(response.data);
        return response.data;
    });
};

export const rerollParcels = async (parcel_options: {
    seed?: number;
    min_parcels?: number;
    max_parcels?: number;
}) => {
    return axiosInstance.post("/parcels", parcel_options).then((response) => {
        useStore.getState().updateParcels(response.data);
        return response.data;
    });
};

export const updateParcels = async (parcels: Parcel[]) => {
    useStore.getState().updateParcels(parcels);
    return axiosInstance.put("/parcels", parcels).then((response) => {
        useStore.getState().updateParcels(response.data);
        return response.data;
    });
};

export const getAgents = async () => {
    return axiosInstance.get("/agents").then((response) => {
        useStore.getState().updateAgents(response.data);
        return response.data;
    });
};

export const rerollAgents = async (agent_options: {
    seed?: number;
    min_agents?: number;
    max_agents?: number;
    min_capacity?: number;
    max_capacity?: number;
    min_dist?: number;
    max_dist?: number;
}) => {
    return axiosInstance.post("/agents", agent_options).then((response) => {
        useStore.getState().updateAgents(response.data);
        return response.data;
    });
};

export const updateAgents = async (agents: Agent[]) => {
    useStore.getState().updateAgents(agents);
    return axiosInstance.put("/agents", agents).then((response) => {
        useStore.getState().updateAgents(response.data);
        return response.data;
    });
};

export const getMap = async () => {
    axiosInstance.get("/map").then((response) => {
        const { nodeArray, relationships } = CreateNodeArray(
            response.data["no_of_nodes"],
            response.data["nodes"],
        );
        useStore
            .getState()
            .updateNodesAndRelationships(nodeArray, relationships);
    });
};

export const createMap = async (map_options: {
    seed?: number;
    root_splits?: number;
    turn_around_chance?: number;
    split_chance?: number;
    max_split?: number;
    min_split?: number;
    min_dist?: number;
    max_dist?: number;
    angle_range?: number;
    min_depth?: number;
    max_depth?: number;
    merge_distance?: number;
    return_angle_range?: number;
}) => {
    axiosInstance.post("/map", map_options).then((response) => {
        const { nodeArray, relationships } = CreateNodeArray(
            response.data["no_of_nodes"],
            response.data["nodes"],
        );
        useStore
            .getState()
            .updateNodesAndRelationships(nodeArray, relationships);
    });
};

export const simulate = async () => {
    return axiosInstance
        .get("/simulate")
        .then((response) => {
            console.log(response.data);
            useStore.getState().updateRoutes(response.data);
        })
        .catch((error) => {
            console.error(error);
        });
};
