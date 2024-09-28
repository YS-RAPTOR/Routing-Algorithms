export class Node {
    id: number;
    x: number;
    y: number;
    color: string;
    highlighted: boolean = false;

    constructor(id: number, x: number, y: number, color: string) {
        this.id = id;
        this.x = x;
        this.y = y;
        this.color = color;
    }
}

export class Relationship {
    small: number;
    large: number;
    highlighted: boolean = false;

    constructor(first: number, second: number) {
        if (first < second) {
            this.small = first;
            this.large = second;
        } else {
            this.small = second;
            this.large = first;
        }
    }

    equals(other: Relationship) {
        return this.small === other.small && this.large === other.large;
    }

    arrayHas(arr: Relationship[]): boolean {
        for (let i = 0; i < arr.length; i++) {
            if (this.equals(arr[i])) {
                return true;
            }
        }
        return false;
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
    const relationships: Relationship[] = [];

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
        );

        for (let j = 0; j < nodes[i].neighbours.length; j++) {
            const relationship = new Relationship(
                nodes[i].id,
                nodes[i].neighbours[j],
            );
            if (!relationship.arrayHas(relationships)) {
                relationships.push(relationship);
            }
        }
    }
    return { nodeArray, relationships };
};
