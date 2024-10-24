import { Canvas as FiberCanvas, useFrame } from "@react-three/fiber";
import {
    Plane,
    Circle,
    CameraControls,
    OrthographicCamera,
    Text,
} from "@react-three/drei";
import { Button } from "@/components/ui/button";
import { useStore } from "./lib/api";
import { Node, Relationship } from "./lib/types";
import { useRef } from "react";

import * as api from "./lib/api";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "./components/ui/card";

import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { ScrollArea } from "./components/ui/scroll-area";
import {
    PiArrowsVerticalFill,
    PiGpsFixDuotone,
    PiPlayDuotone,
    PiStopDuotone,
} from "react-icons/pi";
import { Separator } from "./components/ui/separator";

const ButtonGroup = (props: {
    simulating: boolean;
    setSimulating: (value: boolean) => void;
    loading: number;
    setLoading: (value: number) => void;
    camControls: React.MutableRefObject<CameraControls>;
}) => {
    const isPicking = useStore((state) => state.isPicking);
    const updateIsPicking = useStore((state) => state.updateIsPicking);
    const updateIsLoading = useStore((state) => state.updateIsLoading);
    const updateCalcResults = useStore((state) => state.updateCalcResults);

    return (
        <div className="flex fill-slate-900 flex-col gap-3 absolute right-3 bottom-3 z-10">
            <Button
                size="icon"
                onClick={() => {
                    api.createMap({});
                    api.rerollParcels({});
                    api.rerollAgents({});
                }}
            ></Button>
            <Button
                size="icon"
                onClick={() => {
                    updateIsPicking(!isPicking);
                }}
            >
                P
            </Button>
            <Button
                variant={props.simulating ? "destructive" : "secondary"}
                size="icon"
                onClick={() => {
                    if (!props.simulating) {
                        updateIsLoading(true);

                        var percent = 0;
                        const timer = setInterval(() => {
                            percent += Math.floor(Math.random() * 5 + 1);
                            props.setLoading(percent);
                            if (percent >= 85) {
                                clearInterval(timer);
                                percent = 0;
                            }
                        }, 1300);

                        api.simulate()
                            .then(() => {
                                updateIsLoading(false);
                                clearInterval(timer);
                                percent = 0;
                                props.setLoading(0);
                            })
                            .catch(() => {
                                updateIsLoading(false);
                                props.setSimulating(false);
                                clearInterval(timer);
                                percent = 0;
                                props.setLoading(0);
                            });
                    }
                    props.setSimulating(!props.simulating);
                }}
            >
                {props.simulating ? <PiStopDuotone /> : <PiPlayDuotone />}
            </Button>
            <Button
                variant="secondary"
                size="icon"
                onClick={() => {
                    props.camControls.current.reset();
                }}
            >
                <PiGpsFixDuotone />
            </Button>
        </div>
    );
};

export const SimulatorSidebar = () => {
    const calcResults = useStore((state) => state.calcResults);
    const summary = useStore((state) => state.summary);
    if (calcResults === null || summary === null) {
        return <div></div>;
    }

    return (
        <ScrollArea className="w-full h-full">
            <div className="h-full w-full flex gap-2 flex-col p-2 ">
                <h1 className="font-black text-lg">Summary:</h1>
                <div className="text-sm text-muted-foreground -mt-2">
                    <p>
                        Total Distance Travelled:{" "}
                        {summary.total_distance.toFixed(0)}
                    </p>
                    <p>Total Parcels Delivered: {summary.total_parcels}</p>
                </div>

                <Separator></Separator>
                <h1 className="font-black text-lg">Calculated Routes:</h1>
                {calcResults.map((res) => (
                    <AgentInfo
                        key={res.agent.id}
                        agent={res.agent}
                        color={res.color}
                        route={res.route}
                        path={res.path}
                        performance={res.performance}
                    />
                ))}
            </div>
        </ScrollArea>
    );
};

const WarehouseInfo = () => {
    const highlights = useStore((state) => state.highlights);

    const getPickups = () => {
        if (highlights === null) {
            return [];
        }

        const agent_id = highlights?.agent_id;
        const calcResults = useStore.getState().calcResults;
        if (calcResults === null) {
            return [];
        }
        const current_highlight = calcResults.find(
            (route) => route.agent.id === agent_id,
        );

        if (current_highlight === undefined) {
            return [];
        }
        const route = current_highlight.route;

        const pickups: string[] = ["Warehouse Pickup Order"];

        let warehouse_times = 0;
        for (let i = 0; i < route.length; i++) {
            if (route[i] === null) {
                pickups.push("");
                warehouse_times++;
                continue;
            }
            pickups[warehouse_times] += "📦" + route[i]!.id;
        }
        return pickups;
    };

    return (
        <div className="z-10 absolute top-3 right-3 flex items-end flex-col">
            {getPickups().map((pickups, index) => {
                return (
                    <div
                        key={index}
                        className={`flex w-fit gap-2 rounded-full font-bold px-2 bg-slate-100`}
                    >
                        {pickups}
                    </div>
                );
            })}
        </div>
    );
};

const AgentInfo = (props: api.CalcResults) => {
    const updateHighlight = useStore((state) => state.updateHighlights);

    const nodesToHighlight = new Set<number>(props.path);
    const relationshipsToHighlight = (() => {
        const relationships: Relationship[] = [];
        for (let i = 0; i < props.path.length - 1; i++) {
            const relationship = new Relationship(
                props.path[i],
                props.path[i + 1],
            );
            if (relationship.arrayHas(relationships)) {
                continue;
            }
            relationships.push(relationship);
        }
        return relationships;
    })();

    return (
        <Card
            onPointerEnter={() =>
                updateHighlight({
                    relationship: relationshipsToHighlight,
                    nodes: nodesToHighlight,
                    agent_id: props.agent.id,
                })
            }
            onPointerLeave={() => updateHighlight(null)}
        >
            <CardHeader className="p-3 pb-0 ">
                <CardTitle>Agent {props.agent.id}</CardTitle>
                <CardDescription>
                    <p>Max Capacity: {props.agent.max_capacity}</p>
                    <p>Max Distance: {props.agent.max_dist.toFixed(0)}m</p>
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div>
                    {props.performance ? (
                        <>
                            <p className="text-sm ">
                                Distance Travelled:{" "}
                                {props.performance.distance_travelled.toFixed(
                                    0,
                                )}
                                m
                            </p>
                            <p className="text-sm ">
                                Parcels Delivered:{" "}
                                {props.performance.parcels_delivered}
                            </p>
                        </>
                    ) : (
                        <p className="text-red-500 font-bold">
                            Agent is not valid
                        </p>
                    )}
                </div>
                <Collapsible>
                    <CollapsibleTrigger className="font-bold w-full justify-between items-center flex">
                        <span>Routes</span>
                        <PiArrowsVerticalFill />
                    </CollapsibleTrigger>
                    <CollapsibleContent className="relative flex flex-col items-center gap-2">
                        {props.route.map((parcel, index) => (
                            <div
                                key={index}
                                className="flex flex-col items-center"
                            >
                                {index !== 0 ? (
                                    <div className="bg-slate-900 w-2 h-6 -m-2"></div>
                                ) : (
                                    <div className=" w-2 h-8 -m-2"></div>
                                )}
                                <div>
                                    {parcel === null ? (
                                        <div className="bg-green-500 rounded-full items-center flex flex-col p-3">
                                            <span className="font-bold">0</span>
                                            <span className="text-center">
                                                Pick up parcels from warehouse
                                            </span>
                                        </div>
                                    ) : (
                                        <div className="bg-red-500 rounded-full items-center flex flex-col p-3">
                                            <span className="font-bold">
                                                {parcel.location}
                                            </span>
                                            <span className="text-center">
                                                Drop off Parcel {parcel.id}
                                            </span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </CollapsibleContent>
                </Collapsible>
            </CardContent>
        </Card>
    );
};

export const Canvas = (props: {
    simulating: boolean;
    setSimulating: (value: boolean) => void;
    loading: number;
    setLoading: (value: number) => void;
}) => {
    // OnClick event handler for the circles
    // Way to highlight circles, lines from outside the canvas

    const nodes = useStore((state) => state.nodes);
    const relationships = useStore((state) => state.relationships);
    const camControls = useRef<CameraControls>(null!);
    const enabled = nodes.length > 0 && relationships.length > 0;
    const calcResults = useStore((state) => state.calcResults);

    return (
        <div className="w-full h-full relative">
            <ButtonGroup
                simulating={props.simulating}
                setSimulating={props.setSimulating}
                loading={props.loading}
                setLoading={props.setLoading}
                camControls={camControls}
            />
            <WarehouseInfo />
            <FiberCanvas
                onPointerEnter={(e) => {
                    if (enabled) {
                        if (e.buttons === 1) {
                            e.currentTarget.className = "cursor-grabbing";
                        } else {
                            e.currentTarget.className = "cursor-grab";
                        }
                    } else {
                        e.currentTarget.className = "cursor-default";
                    }
                }}
                onPointerUp={(e) => {
                    if (enabled) {
                        e.currentTarget.className = "cursor-grab";
                    } else {
                        e.currentTarget.className = "cursor-default";
                    }
                }}
                onPointerDown={(e) => {
                    if (enabled) {
                        e.currentTarget.className = "cursor-grabbing";
                    } else {
                        e.currentTarget.className = "cursor-default";
                    }
                }}
            >
                <OrthographicCamera position={[0, 0, 10]} makeDefault />
                <CameraControls
                    enabled={enabled}
                    ref={camControls}
                    dollySpeed={5}
                    dollyToCursor={true}
                    maxZoom={50}
                    minZoom={0.5}
                    mouseButtons={{
                        left: 2,
                        middle: 0,
                        right: 0,
                        wheel: 16,
                    }}
                    touches={{
                        one: 64,
                        two: 8192,
                        three: 0,
                    }}
                />
                {nodes.map((node) => (
                    <NodeView
                        key={node.id}
                        node={node}
                        num_of_nodes={nodes.length}
                    />
                ))}
                {relationships.map((relationship, index) => (
                    <RelationshipView
                        key={index}
                        relationship={relationship}
                        nodes={nodes}
                        relationship_index={index}
                        num_of_relationships={relationships.length}
                    />
                ))}
                {(calcResults ?? []).map((res) => (
                    <RouteView
                        key={res.agent.id}
                        route={res.route}
                        nodes={nodes}
                        agent_id={res.agent.id}
                    />
                ))}
            </FiberCanvas>
        </div>
    );
};

const RouteView = (props: {
    route: (api.Parcel | null)[];
    nodes: Node[];
    agent_id: number;
}) => {
    const locations = (() => {
        const map = new Map<number, string>();

        for (let i = 0; i < props.route.length; i++) {
            const parcel = props.route[i];
            if (parcel === null) {
                continue;
            }
            if (!map.has(parcel.location)) {
                map.set(parcel.location, "");
            }
            map.set(
                parcel.location,
                map.get(parcel.location) + "📦" + parcel.id,
            );
        }
        return [...map.entries()];
    })();

    const refs = locations.map(() => useRef<any>(null!));

    useFrame(() => {
        if (useStore.getState().highlights !== null) {
            if (useStore.getState().highlights?.agent_id === props.agent_id) {
                for (let ref of refs) {
                    ref.current.visible = true;
                }
            }
        } else {
            for (let ref of refs) {
                ref.current.visible = false;
            }
        }
    });

    return (
        <>
            {locations.map(([location, parcels], i) => (
                <Text
                    key={location}
                    ref={refs[i]}
                    position={[
                        props.nodes[location].x,
                        props.nodes[location].y + 10,
                        5 - (10000 + props.nodes[location].x) / 10000,
                    ]}
                    anchorX={"center"}
                    anchorY={"middle"}
                    textAlign={"center"}
                    fontWeight={"bold"}
                    color={"#ffffff"}
                    fontSize={10}
                    outlineWidth={5}
                    outlineColor={props.nodes[location].color}
                    outlineOpacity={1}
                    outlineBlur={1}
                    strokeColor={"#000000"}
                    strokeWidth={0.1}
                >
                    {parcels}
                </Text>
            ))}
            ;
        </>
    );
};

const NodeView = (props: { node: Node; num_of_nodes: number }) => {
    const ref = useRef<any>(null!);

    const radius = 5;
    const zOffset = (props.node.id / props.num_of_nodes) * 4;
    const onClickNode = new CustomEvent("onClickNode", { detail: props.node });

    useFrame(() => {
        if (useStore.getState().highlights !== null) {
            if (useStore.getState().highlights?.nodes.has(props.node.id)) {
                ref.current.visible = true;
            }
        } else {
            ref.current.visible = false;
        }
    });

    return (
        <>
            <Circle
                args={[radius]}
                position={[props.node.x, props.node.y, -zOffset]}
                material-color={props.node.color}
                onClick={() => {
                    if (useStore.getState().isPicking) {
                        document.dispatchEvent(onClickNode);
                    }
                }}
                onPointerEnter={(e) => {
                    if (useStore.getState().isPicking) {
                        // @ts-ignore
                        e.srcElement.className = "cursor-pointer";
                    } else {
                        if (e.buttons === 1) {
                            // @ts-ignore
                            e.srcElement.className = "cursor-grabbing";
                        } else {
                            // @ts-ignore
                            e.srcElement.className = "cursor-grab";
                        }
                    }
                }}
                onPointerLeave={(e) => {
                    if (e.buttons === 1) {
                        // @ts-ignore
                        e.srcElement.className = "cursor-grabbing";
                    } else {
                        // @ts-ignore
                        e.srcElement.className = "cursor-grab";
                    }
                }}
            />
            <Text
                position={[props.node.x, props.node.y, 4]}
                anchorX={"center"}
                anchorY={"middle"}
                textAlign={"center"}
                fontWeight={"bold"}
                color={"#ffffff"}
                strokeColor={"#000000"}
                strokeWidth={0.05}
                fillOpacity={1}
                fontSize={2}
            >
                {props.node.id}
            </Text>
            <Circle
                ref={ref}
                args={[radius * 3]}
                position={[props.node.x, props.node.y, -10 - zOffset]}
                visible={false}
                material-color={"#f1f5f9"}
            />
        </>
    );
};

const RelationshipView = (props: {
    relationship: Relationship;
    nodes: Node[];
    relationship_index: number;
    num_of_relationships: number;
}) => {
    const ref = useRef<any>(null!);
    const color = props.nodes[props.relationship.small].color;
    const thickness = 2;
    const zOffset = (props.relationship_index / props.num_of_relationships) * 4;

    useFrame(() => {
        if (useStore.getState().highlights !== null) {
            if (
                props.relationship.arrayHas(
                    // @ts-ignore
                    useStore.getState().highlights?.relationship,
                )
            ) {
                ref.current.visible = true;
            }
        } else {
            ref.current.visible = false;
        }
    });

    const points = [
        [
            props.nodes[props.relationship.small].x,
            props.nodes[props.relationship.small].y,
        ],
        [
            props.nodes[props.relationship.large].x,
            props.nodes[props.relationship.large].y,
        ],
    ];

    const distance = Math.sqrt(
        (points[0][0] - points[1][0]) ** 2 + (points[0][1] - points[1][1]) ** 2,
    );
    const angle =
        Math.atan2(points[1][1] - points[0][1], points[1][0] - points[0][0]) -
        Math.PI / 2;

    const midPoint = [
        (points[0][0] + points[1][0]) / 2,
        (points[0][1] + points[1][1]) / 2,
    ];

    return (
        <>
            <Plane
                args={[thickness, distance, 1, 1]}
                material-color={color}
                position={[midPoint[0], midPoint[1], -5 - zOffset]}
                rotation={[0, 0, angle]}
            />
            <Plane
                ref={ref}
                args={[thickness * 5, distance, 1, 1]}
                position={[midPoint[0], midPoint[1], -15 - zOffset]}
                rotation={[0, 0, angle]}
                material-color={"#f1f5f9"}
            />
        </>
    );
};
