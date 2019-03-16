import sys
import json


class ComponentGraph:
    def __init__(self, components, check_graph_validity=True):
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
        """"""
        return iter(self.components)

    def __getitem__(self, component):
        """"""
        return self.components[component]

    def _load_component_modules(self, component):
        """"""
        component_modules = {}
        for module in component["modules"]:
            component_modules[module["name"]] = {
                "kind" : module["kind"],
                "dependencies" : self._load_module_dependencies(module),
            }

        return component_modules

    def _load_module_dependencies(self, module):
        """"""
        module_dependencies = {}
        for dependency in module["dependencies"]:
            target_component, target_module = dependency.split(".")
            if target_component in module_dependencies:
                module_dependencies[target_component].append(target_module)
            else:
                module_dependencies[target_component] = [target_module]

        return module_dependencies

    def _check_graph_validity(self):
        """"""
        for component in self.components.values():
            for module in component["modules"].values():
                for dependency in module["dependencies"].items():
                    self._check_dependency_validity(dependency)

    def _check_dependency_validity(self, dependency):
        """"""
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
        """"""
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
        """"""
        def calculate_instability(fan_in_dependencies, fan_out_dependencies):
            """"""
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


def error(*arguments, exit_code=1, **keyword_arguments):
    """"""
    print("DMV Error:", *arguments, file=sys.stderr, **keyword_arguments)
    exit(exit_code)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        error("Please pass a JSON filename as your first argument.")

    try:
        with open(sys.argv[1], "r") as open_file:
            components = ComponentGraph(json.load(open_file))
    except FileNotFoundError:
        error("\"'{0}' not found\"".format(sys.argv[1]))
    except json.JSONDecodeError:
        error("\"could not parse '{0}'\"".format(sys.argv[1]))
    except KeyError as key_error:
        error("{0}".format(str(key_error)))

    for component in components:
        print(components[component])
