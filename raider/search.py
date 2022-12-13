from raider.flow import Flow
from raider.utils import list_hyfiles, list_projects


class Matches:
    def __init__(self, raider):
        self.raider = raider
        self.results = {}

    def match_projects(self, search):
        self.results = self.raider.projects.search_projects(search)

    def match_hyfiles(self, search):
        self.results = self.raider.projects.search_hyfiles(
            self.results, search
        )

    def match_flows(self, search_flows, search_flowgraphs):
        self.results = self.raider.projects.search_flows(
            self.results, search_flows, search_flowgraphs
        )


class Search:
    def __init__(self, raider, args):
        self.raider = raider
        self.args = args
        self.matches = Matches(raider)

    def search(self):
        self.matches.match_projects(self.args.projects)
        self.matches.match_hyfiles(self.args.hyfiles)
        if self.print_flows_enabled or self.print_flowgraphs_enabled:
            for project in self.matches.results:
                self.raider.projects[project].load()
            self.matches.match_flows(self.args.flows, self.args.graphs)

            results = self.matches.results
            for project in list(results):
                for hyfile in list(results[project]):
                    flows = results[project][hyfile]["flows"]
                    flowgraphs = results[project][hyfile]["flowgraphs"]
                    if any(
                        [
                            (not self.print_flows_enabled and not flowgraphs),
                            (not self.print_flowgraphs_enabled and not flows),
                            (not flows and not flowgraphs),
                        ]
                    ):
                        del self.matches.results[project][hyfile]

                if not results[project]:
                    del self.matches.results[project]

    def print(self):
        projects_padding = 0
        for item in self.matches.results:
            project = self.raider.projects[item]
            project.print(projects_padding)

            for hyfile in self.matches.results[item]:
                hyfiles_padding = projects_padding + 4
                hyfiles_flows = self.matches.results[item]
                flowstore = project.flowstore

                if hyfile in hyfiles_flows:
                    project.print_hyfile(hyfile, spacing=hyfiles_padding)
                    if self.print_flowgraphs_enabled:
                        for flowgraph_id in hyfiles_flows[hyfile][
                            "flowgraphs"
                        ]:
                            flowgraphs_padding = hyfiles_padding + 4
                            flowgraph = flowstore.flowgraphs[flowgraph_id]
                            start_flow = flowgraph.start
                            start_flow_name = flowstore.get_flow_name_by_flow(
                                start_flow
                            )
                            if flowgraph.test:
                                test_flow_name = (
                                    flowstore.get_flow_name_by_flow(
                                        flowgraph.test
                                    )
                                )
                            else:
                                test_flow_name = None

                            project.print_flowgraph(
                                flowgraph_id,
                                start_flow_name,
                                test_flow_name,
                                spacing=flowgraphs_padding,
                            )
                    if self.print_flows_enabled:
                        for flow in hyfiles_flows[hyfile]["flows"]:
                            if self.print_flowgraphs_enabled:
                                flows_padding = flowgraphs_padding + 2
                            else:
                                flows_padding = hyfiles_padding + 4
                            project.print_flow(flow, spacing=flows_padding)

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

    @property
    def print_flowgraphs_enabled(self):
        if isinstance(self.args.graphs, str):
            return True
        return False
