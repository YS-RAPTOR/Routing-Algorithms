import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useEffect, useState } from "react";
import { Canvas, SimulatorSidebar } from "@/Canvas";
import * as api from "./lib/api";
import { Progress } from "@/components/ui/progress";

const App = () => {
    const [simulating, setSimulating] = useState(false);
    const isLoading = api.useStore((state) => state.isLoading);
    const [loading, setLoading] = useState(0);
    useEffect(() => {
        const handleNodeClick = (e: Event) => {
            console.log(e);
        };

        document.addEventListener("onClickNode", handleNodeClick);
        return () => {
            document.removeEventListener("onClickNode", handleNodeClick);
        };
    }, []);

    return (
        <ResizablePanelGroup
            direction="horizontal"
            className="relative w-dvh flex h-dvh rounded-lg"
        >
            {isLoading && (
                <div
                    className="absolute top-0 left-0 backdrop-blur-sm flex z-20 justify-center items-center w-full h-full"
                    onClick={(e) => {
                        e.stopPropagation();
                    }}
                >
                    <Progress
                        className="w-3/4"
                        value={!isLoading ? 100 : loading}
                    />
                </div>
            )}
            <ResizablePanel defaultSize={75} className="h-dvh">
                <Canvas
                    simulating={simulating}
                    setSimulating={setSimulating}
                    loading={loading}
                    setLoading={setLoading}
                />
            </ResizablePanel>
            <ResizableHandle withHandle />
            <>
                <ResizablePanel
                    maxSize={50}
                    minSize={15}
                    defaultSize={25}
                    className="h-dvh"
                >
                    {simulating ? <SimulatorSidebar /> : <Sidebar />}
                </ResizablePanel>
            </>
        </ResizablePanelGroup>
    );
};

const Sidebar = () => {
    return (
        <Tabs defaultValue="map" className="p-2 w-full">
            <TabsList className="w-full">
                <TabsTrigger className="w-full" value="map">
                    Map
                </TabsTrigger>
                <TabsTrigger className="w-full" value="parcels">
                    Parcels
                </TabsTrigger>
                <TabsTrigger className="w-full" value="agents">
                    Agents
                </TabsTrigger>
            </TabsList>
            <TabsContent value="map">
                <MapSettings />
            </TabsContent>
            <TabsContent value="parcels">
                <ParcelsSettings />
            </TabsContent>
            <TabsContent value="agents">
                <AgentsSettings />
            </TabsContent>
        </Tabs>
    );
};

// Ayush
const MapSettings = () => {
    return <div>Map Settings</div>;
};

// Winston
const ParcelsSettings = () => {
    return <div>Parcels Settings</div>;
};

// Franklin
const AgentsSettings = () => {
    return <div>Agents Settings</div>;
};

export default App;
