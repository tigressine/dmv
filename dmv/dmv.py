import sys
import json


class ComponentGraph:
    def __init__(self, components, check_graph_validity=True):
        self.components = {}
        for component in components:
            component_modules = self._load_component_modules(component)
            self.components[component["name"]] = component_modules

        if check_graph_validity:
            self._check_graph_validity()

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
            for module in component.values():
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
            if target_module not in self.components[target_component]:
                raise KeyError(
                    "module '{0}' does not exist in component '{1}'".format(
                        target_module,
                        target_component,
                    )
                )

'''
    def calculate_component_abstractness(self):
        """"""
        for component in self.components:
            abnormal_module_count = 0
            for module in component.modules:
                if module.kind != "normal":
                    abnormal_module_count += 1

            if len(component.modules) > 0:
                component.abstractness = (
                    abnormal_module_count / len(component.modules)
                )
            else:
                component.abstractness = 0

    def calculate_component_stability(self):
        """"""
        for component in self.components:
            component.fan_out_dependencies = 0
            for module in component.modules:
                if len(module.dependencies) > 0:
                    component.fan_out_dependencies += 1

        fan_in_dependency_counts = {}
        for component in self.components:
            for module in component.modules:
                for dependency in module.dependencies.keys():
                    if dependency in fan_in_dependency_counts:
                        fan_in_dependency_counts[dependency] += 1
                    else:
                        fan_in_dependency_counts[dependency] = 1
        for component in self.components:
'''

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

    print(components.components)
