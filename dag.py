import modules
import lsp
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import re

from node import Node


def draw_dag_interactive(dag, outfile):
    net = Network(notebook=True, directed=True)
    net.from_nx(dag)
    net.show_buttons(filter_=["physics"])
    net.toggle_physics(True)
    net.show(outfile)


def assemble_symbol_table(root_path: str, uri: str, module_sources):
    symbols = {}
    for module_source in module_sources:
        if module_source["definition"] is not None:
            module_symbols = lsp.get_document_symbols(
                root_path=root_path, uri=module_source["definition"]["uri"]
            )
            if len(module_source["only"]) > 0:
                for symbol in module_symbols:
                    if (
                        symbol["name"] in module_source["only"]
                        and symbol["containerName"] == module_source["name"]
                    ):
                        symbols[symbol["name"]] = {
                            "symbol": symbol,
                            "source": module_source,
                        }
            else:
                for symbol in module_symbols:
                    if symbol["containerName"] == module_source["name"]:
                        symbols[symbol["name"]] = {
                            "symbol": symbol,
                            "source": module_source["name"],
                        }

    internal_symbols = lsp.get_document_symbols(root_path=root_path, uri=uri)
    for symbol in internal_symbols:
        symbols[symbol["name"]] = {"symbol": symbol, "source": "internal"}

    return symbols


def fetch_range(lines: list[str], symbol_range):
    start_line, start_char = (
        symbol_range["start"]["line"],
        symbol_range["start"]["character"],
    )
    end_line, end_char = (
        symbol_range["end"]["line"],
        symbol_range["end"]["character"],
    )

    lines[start_line] = lines[start_line][start_char:]
    lines[end_line] = lines[end_line][:end_char]

    symbol_text = "\n".join(lines[start_line : end_line + 1])
    return symbol_text


def generate_dag(root_path, uri):
    module_sources = modules.get_module_sources(root_path, uri)
    internal_symbols = lsp.get_document_symbols(root_path=root_path, uri=uri)
    symbols = assemble_symbol_table(root_path, uri, module_sources)

    graph = nx.DiGraph()

    with open(uri, mode="r") as f:
        lines = f.read().split("\n")
        for symbol in internal_symbols:
            v = Node(name=symbol["name"], uri=uri)
            print(v)
            graph.add_node(str(v))
            symbol_text = fetch_range(lines, symbol["location"]["range"])
            for token in re.split(r"[ \(\)\+\-\*\/\=,:]", symbol_text):
                if token in symbols:
                    u = Node(
                        name=token, uri=symbols[token]["symbol"]["location"]["uri"]
                    )
                    graph.add_edge(str(u), str(v))
                    # print(
                    #     symbol["name"]
                    #     + " depends on "
                    #     + token
                    #     + " from "
                    #     + symbols[token]["symbol"]["location"]["uri"]
                    # )
    return graph


if __name__ == "__main__":
    root_path = (
        "/Users/anthony/Documents/climate_code_conversion/dependency_graphs/source"
    )
    uri = "/Users/anthony/Documents/climate_code_conversion/dependency_graphs/source/client.f90"

    graph = generate_dag(root_path=root_path, uri=uri)


    # TODO: generate a graph that incorporates all the source files in the project.
    draw_dag_interactive(graph, "graph.html")
