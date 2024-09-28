import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useEffect, useState } from "react";
import { Canvas } from "@/Canvas";
import * as api from "./lib/api";

const App = () => {
    const [simulating, setSimulating] = useState(false);
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
            className="w-dvh flex h-dvh rounded-lg"
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
