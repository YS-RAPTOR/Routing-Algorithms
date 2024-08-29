const py = @cImport({
    @cInclude("Python.h");
});

const std = @import("std");
const simulator_impl = @import("simulator.zig");

const PyObject = [*c]py.PyObject;

// Define the struct for the Python object
const Simulator_Wrapper = extern struct {
    ob_base: py.PyObject,
    data: ?*simulator_impl.Simulator,
};

// Define the init and dealloc functions for the Python object
fn simulator_init(self: [*c]Simulator_Wrapper, args: PyObject, kwds: PyObject) callconv(.C) c_int {
    _ = kwds;

    var root_node: PyObject = undefined;
    var all_parcels: PyObject = undefined;

    if (py.PyArg_ParseTuple(args, "OO", &root_node, &all_parcels) == 0) {
        return -1;
    }

    if (py.PyList_Check(all_parcels) == 0) {
        py.PyErr_SetString(py.PyExc_TypeError, "Second argument must be a list of parcels");
        return -1;
    }

    self.*.data = simulator_impl.Simulator.init(root_node, all_parcels) catch {
        return -1;
    };
    return 0;
}

fn simulator_dealloc(self: [*c]Simulator_Wrapper) callconv(.C) void {
    if (self.*.data != null) {
        self.*.data.?.deinit();
    }
    (py.Py_TYPE(self).*.tp_free.?)(self);
}

// Define the methods for the Python object
fn simulator_simulate(self: [*c]Simulator_Wrapper, args: PyObject) PyObject {
    if (self.*.data == null) {
        py.PyErr_SetString(py.PyExc_TypeError, "Simulator hasn't initialized properly");
        return null;
    }

    var agent_allocation: PyObject = undefined;

    if (py.PyArg_ParseTuple(args, "O", &agent_allocation) == 0) {
        return null;
    }

    if (py.PyList_Check(agent_allocation) == 0) {
        py.PyErr_SetString(py.PyExc_TypeError, "First argument must be a list of agent_allocations");
        return null;
    }
    const results = self.*.data.?.simulate(agent_allocation) catch return null;
    const list: PyObject = py.PyList_New(@intCast(results.items.len));
    if (list == null) {
        return py.PyErr_NoMemory();
    }

    for (results.items, 0..) |result, i| {
        const sub_list: PyObject = py.PyList_New(3);
        if (sub_list == null) {
            return py.PyErr_NoMemory();
        }

        const index = py.PyLong_FromLong(@intCast(i));
        const distance = py.PyFloat_FromDouble(result.total_distance_travelled);
        const parcels = py.PyLong_FromLong(result.total_parcels_delivered);

        if (index == null or distance == null or parcels == null) {
            py.Py_DECREF(list);
            py.Py_DECREF(sub_list);
            return py.PyErr_NoMemory();
        }
        _ = py.PyList_SetItem(sub_list, 0, index);
        _ = py.PyList_SetItem(sub_list, 1, parcels);
        _ = py.PyList_SetItem(sub_list, 2, distance);
        _ = py.PyList_SetItem(list, @intCast(i), sub_list);
    }
    return list;
}

fn simulator_set_parcels(self: [*c]Simulator_Wrapper, args: PyObject) PyObject {
    if (self.*.data == null) {
        py.PyErr_SetString(py.PyExc_TypeError, "Simulator hasn't initialized properly");
        return null;
    }
    var parcels: PyObject = undefined;

    if (py.PyArg_ParseTuple(args, "O", &parcels) == 0) {
        return null;
    }
    if (py.PyList_Check(parcels) == 0) {
        py.PyErr_SetString(py.PyExc_TypeError, "First argument must be a list of parcels");
        return null;
    }
    self.*.data.?.set_parcels(parcels) catch return null;
    return py.Py_NewRef(py.Py_None());
}
fn simulator_get_agent_results(self: [*c]Simulator_Wrapper, args: PyObject) PyObject {
    if (self.*.data == null) {
        py.PyErr_SetString(py.PyExc_TypeError, "Simulator hasn't initialized properly");
        return null;
    }
    var index: PyObject = undefined;

    if (py.PyArg_ParseTuple(args, "O", &index) == 0) {
        return null;
    }

    if (py.PyLong_Check(index) == 0) {
        py.PyErr_SetString(py.PyExc_TypeError, "First argument must be an integer");
        return null;
    }

    const agents = self.*.data.?.get_agents(@intCast(py.PyLong_AsUnsignedLong(index)));
    const list: PyObject = py.PyList_New(@intCast(agents.len));
    if (list == null) {
        return py.PyErr_NoMemory();
    }

    for (agents, 0..) |a, i| {
        const sub_list: PyObject = py.PyList_New(3);
        if (sub_list == null) {
            return py.PyErr_NoMemory();
        }

        const is_valid = py.PyBool_FromLong(@intFromBool(a.is_valid));
        const distance = py.PyFloat_FromDouble(a.distance_travelled);
        const parcels = py.PyLong_FromLong(a.parcels_delivered);

        if (is_valid == null or distance == null or parcels == null) {
            py.Py_DECREF(list);
            py.Py_DECREF(sub_list);
            return py.PyErr_NoMemory();
        }
        _ = py.PyList_SetItem(sub_list, 0, is_valid);
        _ = py.PyList_SetItem(sub_list, 1, parcels);
        _ = py.PyList_SetItem(sub_list, 2, distance);
        _ = py.PyList_SetItem(list, @intCast(i), sub_list);
    }
    return list;
}

var simulator_methods = [_]py.PyMethodDef{
    .{
        .ml_name = "simulate",
        .ml_meth = @ptrCast(&simulator_simulate),
        .ml_flags = py.METH_VARARGS,
        .ml_doc = "Simulates according to the agent allocation",
    },
    .{
        .ml_name = "set_parcels",
        .ml_meth = @ptrCast(&simulator_set_parcels),
        .ml_flags = py.METH_VARARGS,
        .ml_doc = "Sets the parcels for the simulator",
    },
    .{
        .ml_name = "get_agent_results",
        .ml_meth = @ptrCast(&simulator_get_agent_results),
        .ml_flags = py.METH_VARARGS,
        .ml_doc = "Sets the parcels for the simulator",
    },
    .{},
};

var simulator_type = py.PyTypeObject{
    .ob_base = .{
        .ob_base = .{
            .ob_refcnt = 1,
            .ob_type = null,
        },
        .ob_size = 0,
    },
    .tp_name = "libSim.Simulator",
    .tp_basicsize = @intCast(@sizeOf(Simulator_Wrapper)),
    .tp_flags = py.Py_TPFLAGS_DEFAULT,
    .tp_doc = "Simulator object",
    .tp_methods = &simulator_methods,
    .tp_members = null,
    .tp_new = py.PyType_GenericNew,
    .tp_init = @ptrCast(&simulator_init),
    .tp_dealloc = @ptrCast(&simulator_dealloc),
};

var simulation_module = py.PyModuleDef{
    .m_base = .{
        .ob_base = .{
            .ob_refcnt = 1,
            .ob_type = null,
        },
        .m_init = null,
        .m_index = 0,
        .m_copy = null,
    },
    .m_name = "libSim",
    .m_doc = "Zig simulation module",
    .m_size = -1,
};

export fn PyInit_libSim() PyObject {
    if (py.PyType_Ready(&simulator_type) < 0)
        return null;

    const mod = py.PyModule_Create(&simulation_module) orelse return null;

    py.Py_INCREF(&simulator_type);
    if (py.PyModule_AddObject(mod, "Simulator", @ptrCast(&simulator_type)) < 0) {
        py.Py_DECREF(&simulator_type);
        py.Py_DECREF(mod);
        return null;
    }

    return mod;
}
