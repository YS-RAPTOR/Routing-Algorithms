const std = @import("std");

pub fn build(b: *std.Build) void {
    var target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    if (target.result.os.tag == .windows) {
        const query: std.Target.Query = .{
            .os_tag = .windows,
            .abi = .msvc,
            .cpu_arch = target.query.cpu_arch,
        };
        target = b.resolveTargetQuery(query);
    }

    const lib = b.addSharedLibrary(.{
        .name = "Sim",
        .root_source_file = b.path("simulator_python.zig"),
        .target = target,
        .optimize = optimize,
    });
    lib.linkLibC();
    lib.linkSystemLibrary("Python3");
    b.installArtifact(lib);

    const lib_unit_tests = b.addTest(.{
        .root_source_file = b.path("simulator_python.zig"),
        .target = target,
        .optimize = optimize,
    });

    const run_lib_unit_tests = b.addRunArtifact(lib_unit_tests);
    const test_step = b.step("test", "Run unit tests");
    test_step.dependOn(&run_lib_unit_tests.step);
}
