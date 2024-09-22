import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import * as api from "./lib/api";
import { useQuery } from "@tanstack/react-query";

const App = () => {
    const [simulating, setSimulating] = useState(false);
    const SimulateQuery = useQuery({
        queryKey: ["simulate"],
        queryFn: () => api.simulate(simulating),
    });

    return (
        <ResizablePanelGroup
            direction="horizontal"
            className="w-dvh flex h-dvh rounded-lg border "
        >
            <ResizablePanel defaultSize={75} className="h-dvh">
                <Canvas simulating={simulating} setSimulating={setSimulating} />
            </ResizablePanel>
            <ResizableHandle withHandle />
            <>
                <ResizablePanel
                    maxSize={50}
                    minSize={15}
                    defaultSize={25}
                    className="h-dvh"
                >
                    {simulating ? <div></div> : <Sidebar />}
                </ResizablePanel>
            </>
        </ResizablePanelGroup>
    );
};

const Canvas = (props: {
    simulating: boolean;
    setSimulating: (value: boolean) => void;
}) => {
    return (
        <div className="w-full h-full relative">
            <Button
                className="absolute left-1/2 bottom-14 -translate-x-1/2 z-10"
                variant={props.simulating ? "destructive" : "default"}
                onClick={() => {
                    props.setSimulating(!props.simulating);
                }}
            >
                {props.simulating ? "Stop Simulation" : "Run Simulation"}
            </Button>
            <canvas className=""></canvas>
        </div>
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
