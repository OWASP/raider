from raider.flow import Flow
from raider.utils import list_projects, list_hyfiles


class Matches:
    def __init__(self, raider):
        self.raider = raider
        self.projects = []
        self.hyfiles = {}
        self.flows = {}

    def match_projects(self, search):
        self.projects = self.raider.projects.search_projects(search)

    def match_hyfiles(self, search):
        self.hyfiles = self.raider.projects.search_hyfiles(self.projects, search)

    def match_flows(self, search):
        self.flows = self.raider.projects.search_flows(self.hyfiles, search)

class Search:
    def __init__(self, raider, args):
        self.raider = raider
        self.args = args
        self.matches = Matches(raider)

    def search(self):
        self.matches.match_projects(self.args.projects)
        self.matches.match_hyfiles(self.args.hyfiles)
        if self.print_flows_enabled:
            for project in self.matches.projects:
                self.raider.projects[project].load()
            self.matches.match_flows(self.args.flows)


    def print_projects(self, spacing:int=0):
        projects_padding = spacing
        for item in self.matches.projects:
            self.raider.projects[item].print(projects_padding)

    def print_hyfiles(self, spacing:int=0):
        for key, value in self.matches.hyfiles.items():
            hyfiles_padding = projects_padding = spacing
            project = self.raider.projects[key]
            if value:
                hyfiles_padding += 4
                project.print(projects_padding)

                project.print_hyfiles(
                    matches=value,
                    spacing=hyfiles_padding)

    def print_flows(self, spacing:int=0):
        for item in self.matches.flows.keys():
            flows_padding = hyfiles_padding = projects_padding = spacing
            project = self.raider.projects[item]
            if project.name in self.matches.hyfiles:
                hyfiles_padding += 4
                flows_padding += 4
                project.print(projects_padding)

            for hyfile in self.matches.flows[project.name].keys():
                flows_padding = hyfiles_padding
                flows = self.matches.flows[project.name][hyfile]
                if flows:
                    flows_padding += 4
                    project.print_hyfiles(
                        matches=[hyfile],
                        spacing=hyfiles_padding)
                    project.print_flows(hyfile=hyfile,
                                        matches=flows,
                                        spacing=flows_padding)

    @property
    def print_projects_enabled(self):
        if isinstance(self.args.projects, str):
            return True
        return False

    @property
    def print_hyfiles_enabled(self):
        if isinstance(self.args.hyfiles, str):
            return True
        return False

    @property
    def print_flows_enabled(self):
        if isinstance(self.args.flows, str):
            return True
        return False

            
