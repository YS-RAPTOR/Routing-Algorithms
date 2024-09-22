import axios from "axios";
import { CreateNodeArray } from "./types";

// Create axios instance
export const axiosInstance = axios.create({
    baseURL: "http://localhost:8000",
});

export const getParcels = async () => {
    return axiosInstance.get("/parcels").then((response) => {
        return response.data;
    });
};

export const rerollParcels = async (parcel_options: {
    seed?: number;
    min_parcels?: number;
    max_parcels?: number;
}) => {
    return axiosInstance.post("/parcels", parcel_options).then((response) => {
        return response.data;
    });
};

export const updateParcels = async (
    parcels: [{ id: number; location: number }],
) => {
    return axiosInstance.put("/parcels", parcels).then((response) => {
        return response.data;
    });
};

export const getAgents = async () => {
    return axiosInstance.get("/agents").then((response) => {
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
        return response.data;
    });
};

export const updateAgents = async (
    agents: [id: number, max_capacity: number, max_dist: number],
) => {
    return axiosInstance.put("/agents", agents).then((response) => {
        return response.data;
    });
};

export const getMap = async () => {
    return axiosInstance.get("/map").then((response) => {
        return CreateNodeArray(
            response.data["no_of_nodes"],
            response.data["nodes"],
        );
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
    return axiosInstance.post("/map", map_options).then((response) => {
        console.log(
            CreateNodeArray(
                response.data["no_of_nodes"],
                response.data["nodes"],
            ),
        );
        return CreateNodeArray(
            response.data["no_of_nodes"],
            response.data["nodes"],
        );
    });
};

export const simulate = async (simulate: boolean) => {
    if (simulate) {
        return axiosInstance.get("/simulate").then((response) => {
            return response.data;
        });
    } else {
        return Promise.resolve();
    }
};
