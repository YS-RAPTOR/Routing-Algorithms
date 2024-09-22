export class Node {
    id: number;
    x: number;
    y: number;
    color: string;
    neighbours: number[];

    constructor(
        id: number,
        x: number,
        y: number,
        color: string,
        neighbours: number[],
    ) {
        this.id = id;
        this.x = x;
        this.y = y;
        this.color = color;
        this.neighbours = neighbours;
    }
}

export const CreateNodeArray = (
    numNodes: number,
    nodes: [
        {
            id: number;
            x: number;
            y: number;
            color: number[];
            neighbours: number[];
        },
    ],
) => {
    const nodeArray: Node[] = Array(numNodes);

    for (let i = 0; i < numNodes; i++) {
        var colorStr = "#";
        for (let j = 0; j < 3; j++) {
            const hex = nodes[i].color[j].toString(16);
            colorStr += hex.length === 1 ? "0" + hex : hex;
        }

        nodeArray[nodes[i].id] = new Node(
            nodes[i].id,
            nodes[i].x,
            nodes[i].y,
            colorStr,
            nodes[i].neighbours,
        );
    }
    return nodeArray;
};
