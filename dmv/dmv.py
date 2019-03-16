import json


class Module:
    """"""
    def __init__(self, name, kind, dependencies):
        """"""
        self.name = name
        self.kind = kind
        self.dependencies = self.parse_dependencies(dependencies)

    def __str__(self):
        """"""
        return "\n".join(self.get_formatted_lines())

    def get_formatted_lines(self):
        """"""
        HEADER_FORMAT = "{0} module: {1}"
        DEPENDENCY_FORMAT = "    dependency: {0}.{1}"

        lines = []
        lines.append(HEADER_FORMAT.format(self.kind, self.name))
        for component, modules in self.dependencies.items():
            for module in modules:
                lines.append(DEPENDENCY_FORMAT.format(component, module))

        return lines 

    def parse_dependencies(self, dependencies):
        """"""
        dependency_table = {}
        for dependency in dependencies:
            component, module = dependency.split(".")
            if component in dependency_table:
                dependency_table[component].append(module)
            else:
                dependency_table[component] = [module]

        return dependency_table


class Component:
    """"""
    def __init__(self, name, modules):
        """"""
        self.name = name
        self.modules = self.parse_modules(modules)
        self.abstractness = self.calculate_abstractness()

    def __str__(self):
        """"""
        HEADER_FORMAT = "component: {0}"
        MODULE_FORMAT = "    {0}"

        lines = []
        lines.append(HEADER_FORMAT.format(self.name))
        for module in self.modules:
            for module_line in module.get_formatted_lines():
                lines.append(MODULE_FORMAT.format(module_line))

        return "\n".join(lines)

    def parse_modules(self, modules):
        """"""
        initialized_module_list = []
        for module in modules:
            initialized_module_list.append(
                Module(
                    module["name"],
                    module["kind"],
                    module["dependencies"],
                )
            )

        return initialized_module_list

    def calculate_abstractness(self):
        abnormal_module_count = 0
        for module in self.modules:
            if module.kind != "normal":
                abnormal_module_count += 1

        if len(self.modules) > 0:
            return abnormal_module_count / len(self.modules)
        else:
            return 0


with open("test.json", "r") as json_file:
    components = []
    for component in json.load(json_file):
        components.append(Component(component["name"], component["modules"]))

for component in components:
    print(component)

for component in components:
    print(component.name, component.abstractness)
