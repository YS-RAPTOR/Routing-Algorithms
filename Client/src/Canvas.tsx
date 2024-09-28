import { Canvas as FiberCanvas, useFrame, useThree } from "@react-three/fiber";
import {
    Line,
    Circle,
    CameraControls,
    OrthographicCamera,
} from "@react-three/drei";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { useStore } from "./lib/api";
import { Node, Relationship } from "./lib/types";
import { forwardRef, useRef, useState } from "react";

import * as api from "./lib/api";

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

    return (
        <div className="flex fill-slate-900 flex-col gap-3 absolute right-3 bottom-3 z-10">
            <Button
                size="icon"
                onClick={() => {
                    api.createMap({});
                    api.rerollParcels({});
                    api.rerollAgents({});
                    api.simulate();
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
                            percent += 5;
                            props.setLoading(percent);
                            if (percent >= 85) {
                                clearInterval(timer);
                                percent = 0;
                            }
                        }, 2500);

                        api.simulate()
                            .then(() => {
                                updateIsLoading(false);
                                clearInterval(timer);
                                percent = 0;
                            })
                            .catch(() => {
                                updateIsLoading(false);
                                props.setSimulating(false);
                                clearInterval(timer);
                                percent = 0;
                            });
                    }
                    props.setSimulating(!props.simulating);
                }}
            >
                {props.simulating ? (
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="18"
                        height="18"
                        fill="#0f172a"
                        viewBox="0 0 256 256"
                        fontStyle="--darkreader-inline-fill: #0f172a;"
                        data-darkreader-inline-fill=""
                    >
                        <path d="M200,40H56A16,16,0,0,0,40,56V200a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V56A16,16,0,0,0,200,40Zm0,160H56V56H200V200Z"></path>
                    </svg>
                ) : (
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="18"
                        height="18"
                        fill="#0f172a"
                        viewBox="0 0 256 256"
                        fontStyle="--darkreader-inline-fill: #0f172a;"
                        data-darkreader-inline-fill=""
                    >
                        <path d="M232.4,114.49,88.32,26.35a16,16,0,0,0-16.2-.3A15.86,15.86,0,0,0,64,39.87V216.13A15.94,15.94,0,0,0,80,232a16.07,16.07,0,0,0,8.36-2.35L232.4,141.51a15.81,15.81,0,0,0,0-27ZM80,215.94V40l143.83,88Z"></path>
                    </svg>
                )}
            </Button>
            <Button
                variant="secondary"
                size="icon"
                onClick={() => {
                    props.camControls.current.reset();
                }}
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
                    fill="#0f172a"
                    viewBox="0 0 256 256"
                    fontStyle="--darkreader-inline-fill: #0f172a;"
                    data-darkreader-inline-fill=""
                >
                    <path d="M240,120H215.63A88.13,88.13,0,0,0,136,40.37V16a8,8,0,0,0-16,0V40.37A88.13,88.13,0,0,0,40.37,120H16a8,8,0,0,0,0,16H40.37A88.13,88.13,0,0,0,120,215.63V240a8,8,0,0,0,16,0V215.63A88.13,88.13,0,0,0,215.63,136H240a8,8,0,0,0,0-16ZM128,200a72,72,0,1,1,72-72A72.08,72.08,0,0,1,128,200Zm0-112a40,40,0,1,0,40,40A40,40,0,0,0,128,88Zm0,64a24,24,0,1,1,24-24A24,24,0,0,1,128,152Z"></path>
                </svg>
            </Button>
        </div>
    );
};

// TODO: Interactions possible:
// Click calculate
// While calculating show progress bar with map greyed out
// Show list of agents in the sidebar with the parcels they are allocated.
// Click on arrow to see rudimentary path taken by the agent (Accordian Style)
// When hovering an agent show map with parcels picked up and dropped off in each location by each agent
// When hovering an agent also shows the path taken by the agent

export const Canvas = (props: {
    simulating: boolean;
    setSimulating: (value: boolean) => void;
}) => {
    // OnClick event handler for the circles
    // Way to highlight circles, lines from outside the canvas
    const isLoading = useStore((state) => state.isLoading);
    const [loading, setLoading] = useState(0);

    const nodes = useStore((state) => state.nodes);
    const relationships = useStore((state) => state.relationships);
    const camControls = useRef<CameraControls>(null!);
    const enabled = nodes.length > 0 && relationships.length > 0;

    return (
        <div className="w-full h-full relative">
            {isLoading && (
                <div className="absolute top-0 left-0 backdrop-blur-sm flex z-20 justify-center items-center w-full h-full">
                    <Progress
                        className="w-3/4"
                        value={!isLoading ? 100 : loading}
                    />
                </div>
            )}
            <ButtonGroup
                simulating={props.simulating}
                setSimulating={props.setSimulating}
                loading={loading}
                setLoading={setLoading}
                camControls={camControls}
            />
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
                <OrthographicCamera position={[0, 0, 1]} makeDefault />
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
            </FiberCanvas>
        </div>
    );
};

const NodeView = (props: { node: Node; num_of_nodes: number }) => {
    const ref = useRef<any>(null!);

    const radius = 5;
    const zOffset = (props.node.id / props.num_of_nodes) * 4;
    const onClickNode = new CustomEvent("onClickNode", { detail: props.node });

    useFrame(() => {
        // Check for highlight
        if (useStore.getState().highlight_color !== null) {
            ref.current.visible = true;
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
            <Circle
                ref={ref}
                args={[radius * 1.5]}
                position={[props.node.x, props.node.y, -10 - zOffset]}
                visible={false}
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
    const ref = useRef(null!);
    const color = props.nodes[props.relationship.small].color;
    const thickness = 2;
    const zOffset = (props.relationship_index / props.num_of_relationships) * 4;

    return (
        <>
            <Line
                points={[
                    [
                        props.nodes[props.relationship.small].x,
                        props.nodes[props.relationship.small].y,
                        -5 - zOffset,
                    ],
                    [
                        props.nodes[props.relationship.large].x,
                        props.nodes[props.relationship.large].y,
                        -5 - zOffset,
                    ],
                ]}
                color={color}
                lineWidth={thickness}
            />
            <Line
                ref={ref}
                points={[
                    [
                        props.nodes[props.relationship.small].x,
                        props.nodes[props.relationship.small].y,
                        -15 - zOffset,
                    ],
                    [
                        props.nodes[props.relationship.large].x,
                        props.nodes[props.relationship.large].y,
                        -15 - zOffset,
                    ],
                ]}
                visible={false}
                lineWidth={8}
            />
        </>
    );
};
