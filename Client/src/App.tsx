import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const App = () => {
    return (
        <ResizablePanelGroup
            direction="horizontal"
            className="w-dvh flex h-dvh rounded-lg border "
        >
            <ResizablePanel defaultSize={75} className="h-dvh">
                <Canvas />
            </ResizablePanel>
            <ResizableHandle withHandle />
            <ResizablePanel
                maxSize={50}
                minSize={15}
                defaultSize={25}
                className="h-dvh"
            >
                <Sidebar />
            </ResizablePanel>
        </ResizablePanelGroup>
    );
};

const Canvas = () => {
    return <div className="w-full h-full bg-red-100">Canvas</div>;
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
