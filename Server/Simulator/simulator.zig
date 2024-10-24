const std = @import("std");
const py = @cImport({
    @cInclude("Python.h");
});

const PyObject = [*c]py.PyObject;

const Id = isize;
const Location = isize;

const Parcel = struct {
    id: Id,
    location: Location,
};

const AgentInfo = struct {
    id: Id,
    max_capacity: u32,
    max_distance: f32,
};

const Node = struct {
    id: Id,
    x: f32,
    y: f32,
    neighbours: std.ArrayList(*Node),

    const Self = @This();

    fn init(py_root_node: PyObject, allocator: std.mem.Allocator, visited: *std.AutoHashMap(Id, *Node)) !*Self {
        var tmp = py.PyObject_GetAttrString(py_root_node, "id");
        if (tmp == null) {
            py.PyErr_SetString(py.PyExc_TypeError, "Object does not have an id attribute");
            return error.NodeInitFailed;
        }
        const id: Id = @intCast(py.PyLong_AsLong(tmp));

        if (visited.contains(id)) {
            return visited.get(id).?;
        }

        tmp = py.PyObject_GetAttrString(py_root_node, "x");
        if (tmp == null) {
            py.PyErr_SetString(py.PyExc_TypeError, "Object does not have an x attribute");
            return error.NodeInitFailed;
        }
        const x = py.PyFloat_AsDouble(tmp);

        tmp = py.PyObject_GetAttrString(py_root_node, "y");
        if (tmp == null) {
            py.PyErr_SetString(py.PyExc_TypeError, "Object does not have an y attribute");
            return error.NodeInitFailed;
        }
        const y = py.PyFloat_AsDouble(tmp);

        tmp = py.PyObject_GetAttrString(py_root_node, "neighbours");
        var neighbours = std.ArrayList(*Node).init(allocator);
        if (tmp == null) {
            py.PyErr_SetString(py.PyExc_TypeError, "Object does not have an neighbours attribute");
            return error.NodeInitFailed;
        }

        const len = py.PyList_Size(tmp);

        const self: *Self = try allocator.create(Self);
        self.id = id;
        self.x = @floatCast(x);
        self.y = @floatCast(y);
        try visited.put(id, self);

        var i: i32 = 0;
        while (i < len) : (i += 1) {
            const neighbour = py.PyList_GetItem(tmp, i);
            const n = try Node.init(neighbour, allocator, visited);
            try neighbours.append(n);
        }

        self.neighbours = neighbours;
        return self;
    }

    fn find_immediate_by_id(self: *const Self, id: Id) ?*Self {
        for (self.neighbours.items) |neighbour| {
            if (neighbour.id == id) {
                return neighbour;
            }
        }
        return null;
    }

    fn simple_distance(self: *const Self, other: *const Self) f32 {
        const dx = other.x - self.x;
        const dy = other.y - self.y;
        return @floatCast(@sqrt(dx * dx + dy * dy));
    }

    fn find_route(self: *Self, target: Location, route: *std.ArrayList(Location)) !void {
        if (route.items.len != 0) {
            return error.RouteError;
        }

        var temp_arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
        var temp_allocator = temp_arena.allocator();

        errdefer temp_arena.deinit();
        defer temp_arena.deinit();

        const dl = std.DoublyLinkedList(*Self);
        var queue = dl{};
        const s = try temp_allocator.create(dl.Node);
        s.data = self;
        queue.append(s);

        var visited = std.AutoHashMap(Id, void).init(temp_allocator);
        try visited.put(self.id, {});

        var parent = std.AutoHashMap(Id, ?Id).init(temp_allocator);
        try parent.put(self.id, null);

        while (queue.len > 0) {
            const current = queue.popFirst().?;

            if (current.data.id == target) {
                var id: ?Id = current.data.id;

                while (id) |i| {
                    try route.append(i);
                    id = parent.get(i).?;
                }
                return;
            }

            for (current.data.neighbours.items) |neighbour| {
                if (visited.contains(neighbour.id)) {
                    continue;
                }
                try visited.put(neighbour.id, {});
                try parent.put(neighbour.id, current.data.id);
                const n = try temp_allocator.create(dl.Node);
                n.data = neighbour;
                queue.append(n);
            }
        }

        return error.RouteError;
    }
};

const SubSimulator = struct {
    all_parcels: std.ArrayList(Parcel),
    root_node: *Node,
    agents: std.ArrayList(Agent),

    pub const Performance = struct {
        total_distance_travelled: f64,
        total_parcels_delivered: i64,
    };

    const Agent = struct {
        info: AgentInfo = undefined,
        distance_travelled: f64 = 0,
        parcels_delivered: i64 = 0,
        is_valid: bool = true,
        is_running: bool = true,
        progress: f32 = 0,
        locations_to_visit: std.ArrayList(Location) = undefined,
        current_location: *Node = undefined,
        target_location: *Node = undefined,
        current_target: Location = 0,
        route: std.ArrayList(Location) = undefined,
        allocator: std.mem.Allocator = undefined,
        current_parcel_to_deliver: Location = undefined,
        distance_to_target: f32 = undefined,

        const AgentSelf = @This();

        fn init(
            info: AgentInfo,
            parcels_allocated: std.ArrayList(Id),
            all_parcels: *std.AutoHashMap(Id, Location),
            agent_starting_location: *Node,
            allocator: std.mem.Allocator,
        ) !AgentSelf {
            if (parcels_allocated.items[0] != -1) {
                return .{
                    .is_valid = false,
                };
            }

            for (parcels_allocated.items, 0..) |parcel_id, i| {
                if (parcel_id == -1) {
                    continue;
                }

                for (parcels_allocated.items, 0..) |other_id, j| {
                    if (i == j) {
                        continue;
                    }

                    if (parcel_id == other_id) {
                        return .{
                            .is_valid = false,
                        };
                    }
                }
            }

            var num_parcels: usize = 0;
            var temp_arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
            defer temp_arena.deinit();
            errdefer temp_arena.deinit();

            var parcels_to_deliver = std.ArrayList(?Parcel).init(temp_arena.allocator());

            for (parcels_allocated.items) |parcel_id| {
                if (parcel_id == -1) {
                    num_parcels = 0;
                    try parcels_to_deliver.append(null);
                    continue;
                }
                num_parcels += 1;

                if (num_parcels > info.max_capacity) {
                    for (parcels_to_deliver.items) |parcel| {
                        if (parcel) |p| {
                            try all_parcels.put(p.id, p.location);
                        }
                    }

                    return .{
                        .is_valid = false,
                    };
                }

                const parcel = all_parcels.get(parcel_id) orelse {
                    for (parcels_to_deliver.items) |parcel| {
                        if (parcel) |p| {
                            try all_parcels.put(p.id, p.location);
                        }
                    }
                    return .{
                        .is_valid = false,
                    };
                };
                try parcels_to_deliver.append(.{
                    .id = parcel_id,
                    .location = parcel,
                });
                _ = all_parcels.remove(parcel_id);
            }

            var locations_to_visit = try std.ArrayList(Location).initCapacity(
                allocator,
                parcels_to_deliver.items.len,
            );

            var i = parcels_to_deliver.items.len;
            while (i > 0) {
                i -= 1;
                if (parcels_to_deliver.items[i]) |p| {
                    try locations_to_visit.append(p.location);
                } else {
                    try locations_to_visit.append(0);
                }
            }
            _ = locations_to_visit.pop();

            var self: AgentSelf = .{
                .info = info,
                .distance_travelled = 0.0,
                .parcels_delivered = 0,
                .is_valid = true,
                .is_running = true,
                .progress = 0.0,
                .locations_to_visit = locations_to_visit,
                .current_location = agent_starting_location,
                .allocator = allocator,
                .route = std.ArrayList(Location).init(allocator),
            };

            _ = self.calculate_route();

            if (self.is_running) {
                while (self.route.items.len == 0) {
                    if (!self.calculate_route()) {
                        self.is_valid = false;
                        return self;
                    }
                }
                self.current_target = self.route.pop();
                self.target_location = self.current_location.find_immediate_by_id(self.current_target) orelse {
                    self.is_valid = false;
                    return self;
                };
                self.distance_to_target = self.current_location.simple_distance(self.target_location);
            }

            return self;
        }

        fn calculate_route(self: *AgentSelf) bool {
            if (self.locations_to_visit.items.len == 0) {
                self.is_running = false;
                return false;
            }

            self.current_parcel_to_deliver = self.locations_to_visit.pop();
            self.current_location.find_route(self.current_parcel_to_deliver, &self.route) catch {
                self.is_valid = false;
                return false;
            };

            self.current_target = self.route.pop();
            return true;
        }

        fn step(self: *AgentSelf) bool {
            if (!self.is_running or !self.is_valid) {
                return false;
            }

            if (self.distance_travelled >= self.info.max_distance) {
                self.distance_travelled = self.info.max_distance;
                return false;
            }

            if (self.progress >= self.distance_to_target) {
                self.current_location = self.target_location;
                self.progress -= self.distance_to_target;
                while (self.route.items.len == 0) {
                    if (self.current_location.id != 0) {
                        self.parcels_delivered += 1;
                    }
                    if (!self.calculate_route()) {
                        return false;
                    }
                }
                self.current_target = self.route.pop();
                self.target_location = self.current_location.find_immediate_by_id(self.current_target) orelse {
                    self.is_valid = false;
                    return false;
                };
                self.distance_to_target = self.current_location.simple_distance(self.target_location);
            }

            self.distance_travelled += 1.0;
            self.progress += 1.0;
            return true;
        }
    };

    const Self = @This();

    pub fn init(
        root_node: *Node,
        all_parcels: std.ArrayList(Parcel),
        allocator: std.mem.Allocator,
        agent_allocation: PyObject,
    ) !Self {
        var key: PyObject = undefined;
        var value: PyObject = undefined;
        var pos: py.Py_ssize_t = 0;

        var agents = std.ArrayList(Agent).init(allocator);

        var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
        defer arena.deinit();
        errdefer arena.deinit();

        var parcel_map = std.AutoHashMap(Id, Location).init(arena.allocator());

        for (all_parcels.items) |parcel| {
            try parcel_map.put(parcel.id, parcel.location);
        }

        while (py.PyDict_Next(agent_allocation, &pos, &key, &value) != 0) {
            var info: AgentInfo = undefined;
            var tmp = py.PyObject_GetAttrString(key, "id");
            if (tmp == null) {
                py.PyErr_SetString(py.PyExc_TypeError, "Object does not have an id attribute");
                return error.AgentInitializationFalied;
            }
            info.id = @intCast(py.PyLong_AsLong(tmp));

            tmp = py.PyObject_GetAttrString(key, "max_capacity");
            if (tmp == null) {
                py.PyErr_SetString(py.PyExc_TypeError, "Object does not have an max_capacity attribute");
                return error.AgentInitializationFalied;
            }
            info.max_capacity = @intCast(py.PyLong_AsLong(tmp));

            tmp = py.PyObject_GetAttrString(key, "max_dist");
            if (tmp == null) {
                py.PyErr_SetString(py.PyExc_TypeError, "Object does not have an max_dist attribute");
                return error.AgentInitializationFalied;
            }
            info.max_distance = @floatCast(py.PyFloat_AsDouble(tmp));

            if (py.PyList_Check(value) == 0) {
                py.PyErr_SetString(py.PyExc_TypeError, "Agent allocation should be a List");
                return error.AgentInitializationFalied;
            }

            const len = py.PyList_Size(value);
            var parcels_allocated = try std.ArrayList(Id).initCapacity(arena.allocator(), @intCast(len));

            var i: i32 = 0;
            while (i < len) : (i += 1) {
                tmp = py.PyList_GetItem(value, i);
                if (tmp == null) {
                    py.PyErr_SetString(py.PyExc_TypeError, "Object does not have an id attribute");
                    return error.AgentInitializationFalied;
                }

                const parcel_id: i32 = @truncate(py.PyLong_AsLong(tmp));
                try parcels_allocated.append(parcel_id);
            }

            try agents.append(try Agent.init(
                info,
                parcels_allocated,
                &parcel_map,
                root_node,
                allocator,
            ));
        }

        return .{
            .root_node = root_node,
            .all_parcels = all_parcels,
            .agents = agents,
        };
    }

    pub fn simulate(self: *Self) !Performance {
        while (true) {
            var done: u32 = 0;
            for (self.agents.items) |*agent| {
                if (agent.step()) {
                    done += 1;
                }
            }
            if (done == 0) {
                break;
            }
        }

        var performance: Performance = .{
            .total_distance_travelled = 0.0,
            .total_parcels_delivered = 0,
        };

        for (self.agents.items) |agent| {
            if (agent.is_valid) {
                performance.total_distance_travelled += agent.distance_travelled;
                performance.total_parcels_delivered += agent.parcels_delivered;
            }
        }
        return performance;
    }
};

pub const Simulator = struct {
    root_node: *Node,
    all_parcels: std.ArrayList(Parcel),
    sub_simulators: std.ArrayList(SubSimulator),

    main_arena: std.heap.ArenaAllocator,
    sub_arena: std.heap.ArenaAllocator,

    const Self = @This();

    pub fn init(py_root_node: PyObject, py_parcels: PyObject) !*Self {
        var temp_arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
        defer temp_arena.deinit();
        errdefer temp_arena.deinit();

        var main_arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
        errdefer main_arena.deinit();

        var sub_arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
        errdefer sub_arena.deinit();

        const self: *Self = try main_arena.allocator().create(Self);
        self.main_arena = main_arena;
        self.sub_arena = sub_arena;

        var visited = std.AutoHashMap(Id, *Node).init(temp_arena.allocator());
        self.root_node = try Node.init(
            py_root_node,
            self.main_arena.allocator(),
            &visited,
        );

        try self.set_parcels(py_parcels);
        return self;
    }

    pub fn deinit(self: *Self) void {
        self.sub_arena.deinit();
        self.main_arena.deinit();
    }

    pub fn set_parcels(self: *Self, py_parcels: PyObject) !void {
        const len = py.PyList_Size(py_parcels);
        self.all_parcels = try std.ArrayList(Parcel).initCapacity(self.main_arena.allocator(), @intCast(len));
        var i: i32 = 0;

        while (i < len) : (i += 1) {
            const parcel = py.PyList_GetItem(py_parcels, i);

            var tmp = py.PyObject_GetAttrString(parcel, "id");
            if (tmp == null) {
                py.PyErr_SetString(py.PyExc_TypeError, "Object does not have an id attribute");
                return error.NodeInitFailed;
            }
            const id: Id = @intCast(py.PyLong_AsLong(tmp));

            tmp = py.PyObject_GetAttrString(parcel, "location");
            if (tmp == null) {
                py.PyErr_SetString(py.PyExc_TypeError, "Object does not have an location attribute");
                return error.NodeInitFailed;
            }
            const location: Location = @intCast(py.PyLong_AsLong(tmp));

            try self.all_parcels.append(.{
                .id = id,
                .location = location,
            });
        }
    }

    pub fn simulate(self: *Self, list_of_agent_allocations: PyObject) !std.ArrayList(SubSimulator.Performance) {
        _ = self.sub_arena.reset(.free_all);

        const len = py.PyList_Size(list_of_agent_allocations);
        var i: i32 = 0;

        self.sub_simulators = try std.ArrayList(SubSimulator).initCapacity(self.sub_arena.allocator(), @intCast(len));
        var results = try std.ArrayList(SubSimulator.Performance).initCapacity(self.sub_arena.allocator(), @intCast(len));
        while (i < len) : (i += 1) {
            const agent_allocation = py.PyList_GetItem(list_of_agent_allocations, i);
            if (py.PyDict_Check(agent_allocation) == 0) {
                py.PyErr_SetString(py.PyExc_TypeError, "Agent allocation should be a Dict");
            }

            var sub_simulator = try SubSimulator.init(
                self.root_node,
                self.all_parcels,
                self.sub_arena.allocator(),
                agent_allocation,
            );

            try self.sub_simulators.append(sub_simulator);
            try results.append(try sub_simulator.simulate());
        }

        return results;
    }

    pub fn get_agents(self: *const Self, simulator_index: u32) []SubSimulator.Agent {
        return self.sub_simulators.items[simulator_index].agents.items;
    }
};
