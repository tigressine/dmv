#! /usr/bin/env python3
"""Create an I/A graph of a software architecture.

This small piece of software is inspired by the metrics found in the textbook
"Clean Architecture" by Robert Martin.

Written by Tiger Sachse.
"""
import sys
import json
import pathlib
import matplotlib.pyplot


class ComponentGraph:
    """Contain and organize a software architecture's component graph."""
    def __init__(self, components, check_graph_validity=True):
        """Initialize this graph with all components, then calculate metrics."""
        self.components = {}
        for component in components:
            self.components[component["name"]] = {
                "modules" : self._load_component_modules(component),
            }

        if check_graph_validity:
            self._check_graph_validity()

        self._calculate_component_abstractness()
        self._calculate_component_instability()

    def __iter__(self):
        """Provide an iterator to iterate over all components."""
        return iter(self.components)

    def __getitem__(self, component):
        """Allow access to underlying components dictionary with [] indexing."""
        return self.components[component]

    def _load_component_modules(self, component):
        """Load a component's modules into the graph."""
        component_modules = {}
        for module in component["modules"]:
            component_modules[module["name"]] = {
                "kind" : module["kind"],
                "dependencies" : self._load_module_dependencies(module),
            }

        return component_modules

    def _load_module_dependencies(self, module):
        """Load a module's dependencies into the graph."""
        module_dependencies = {}
        for dependency in module["dependencies"]:
            target_component, target_module = dependency.split(".")
            if target_component in module_dependencies:
                module_dependencies[target_component].append(target_module)
            else:
                module_dependencies[target_component] = [target_module]

        return module_dependencies

    def _check_graph_validity(self):
        """Ensure all module's dependencies exist."""
        for component in self.components.values():
            for module in component["modules"].values():
                for dependency in module["dependencies"].items():
                    self._check_dependency_validity(dependency)

    def _check_dependency_validity(self, dependency):
        """Ensure a specific dependency exists."""
        target_component, target_modules = dependency
        if target_component not in self.components:
            raise KeyError(
                "component '{0}' does not exist".format(
                    target_component,
                )
            )

        for target_module in target_modules:
            if target_module not in self.components[target_component]["modules"]:
                raise KeyError(
                    "module '{0}' does not exist in component '{1}'".format(
                        target_module,
                        target_component,
                    )
                )
            
    def _calculate_component_abstractness(self):
        """Calculate the abstractness of all components."""
        for component in self.components.values():
            if len(component["modules"]) > 0:
                abnormal_module_count = 0
                for module in component["modules"].values():
                    if module["kind"] != "normal":
                        abnormal_module_count += 1

                component["abstractness"] = (
                    abnormal_module_count / len(component["modules"])
                )
            else:
                component["abstractness"] = 0

    def _calculate_component_instability(self):
        """Calculate the instability of all components."""
        def calculate_instability(fan_in_dependencies, fan_out_dependencies):
            """Calculate instability from fan in and fan out dependencies."""
            divisor = fan_in_dependencies + fan_out_dependencies
            if divisor != 0:
                return fan_out_dependencies / divisor
            else:
                return 0.0

        for component in self.components.values():
            component["fan_out_dependencies"] = 0
            for module in component["modules"].values():
                if len(module["dependencies"]) > 0:
                    component["fan_out_dependencies"] += 1

        for component in self.components.values():
            component["fan_in_dependencies"] = 0

        for component in self.components.values():
            for module in component["modules"].values():
                for target_component in module["dependencies"]:
                    self.components[target_component]["fan_in_dependencies"] += 1

        for component in self.components.values():
            component["instability"] = calculate_instability(
                component["fan_in_dependencies"],
                component["fan_out_dependencies"],
            )

    def to_file(self, file_name):
        """Write this graph to a file with it's calculated metrics."""
        COMPONENT_LINE_FORMAT = "Component '{0}'\n"
        COMPONENT_STATS_LINE_FORMAT = (
            "Abstractness: {0:.3f}, Instability: {1:.3f}\n"
        )
        MODULE_LINE_FORMAT = "    Module '{0}'\n"
        DEPENDENCY_LINE_FORMAT = "        Dependency '{0}.{1}'\n"

        with open(file_name, "w") as open_file:
            for component_name, component_values in self.components.items():
                open_file.write(COMPONENT_LINE_FORMAT.format(component_name))
                open_file.write(
                    COMPONENT_STATS_LINE_FORMAT.format(
                        component_values["abstractness"],
                        component_values["instability"],
                    )
                )
                modules = component_values["modules"].items()
                for module_name, module_values in modules:
                    open_file.write(MODULE_LINE_FORMAT.format(module_name))
                    dependencies = module_values["dependencies"].items()
                    for target_component, target_modules in dependencies:
                        for target_module in target_modules:
                            open_file.write(
                                DEPENDENCY_LINE_FORMAT.format(
                                    target_component,
                                    target_module,
                                )
                            )
                open_file.write("\n")


def error(*arguments, exit_code=1, **keyword_arguments):
    """Format an error and exit the program."""
    print("DMV Error:", *arguments, file=sys.stderr, **keyword_arguments)
    exit(exit_code)


# Main entry point to the script.
if __name__ == "__main__":
    DATA_FILE_FORMAT = "{0}.data"
    GRAPH_FILE_FORMAT = "{0}.png"
    TITLE_FORMAT = "I/A GRAPH FOR {0}"

    if len(sys.argv) < 2:
        error("Please pass a JSON filename as your first argument.")
    else:
        file_name = pathlib.Path(sys.argv[1]).stem

    # Attempt to load the JSON file into a ComponentGraph.
    try:
        with open(sys.argv[1], "r") as open_file:
            components = ComponentGraph(json.load(open_file))
    except FileNotFoundError:
        error("\"'{0}' not found\"".format(sys.argv[1]))
    except json.JSONDecodeError:
        error("\"could not parse '{0}'\"".format(sys.argv[1]))
    except KeyError as key_error:
        error("{0}".format(str(key_error)))

    # Write the ComponentGraph and its metrics to a file.
    components.to_file(DATA_FILE_FORMAT.format(file_name))

    # Create a new plot using each component's 'instability' and 'abstractness'
    # values as points. Plot these points and save the graph to a file.
    matplotlib.pyplot.title(TITLE_FORMAT.format(file_name.upper()))
    matplotlib.pyplot.xlabel("Abstractness")
    matplotlib.pyplot.ylabel("Instability")

    x_values = [components[component]["instability"] for component in components]
    y_values = [components[component]["abstractness"] for component in components]
    
    axes = matplotlib.pyplot.gca()
    axes.set_xlim((-0.1, 1.1))
    axes.set_ylim((-0.1, 1.1))
    matplotlib.pyplot.plot((0.0, 1.0), (1.0, 0.0), color="black", zorder=0)
    matplotlib.pyplot.scatter(x_values, y_values, color="green", zorder=100)
    
    matplotlib.pyplot.savefig(GRAPH_FILE_FORMAT.format(file_name))
