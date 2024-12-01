import argparse
import logging

import rsm
from lsprotocol import types as lsp
from pygls.server import LanguageServer

server = LanguageServer("rsm-lsp", "v0.1")
app = None


@server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls, params: lsp.DidOpenTextDocumentParams):
    """Text document did open notification."""
    ls.show_message("Text Document Did Open")
    global app
    app = rsm.app.ParserApp(plain=params.text_document.text)
    app.run()
    return "200"


@server.command("list_vars")
def list_vars(ls, *args):
    nodeid = args[0][0]
    logging.debug(f"requested vars at {nodeid}")

    assumptions = []
    for node in app.transformer.tree.traverse():
        if isinstance(node, rsm.nodes.Construct) and "assumption" in node.types:
            assumptions.append(node.nodeid)
        if node.nodeid == nodeid:
            break
    logging.debug(f"found {len(assumptions)} assumptions before node {nodeid}")

    return assumptions


@server.command("next_sibling")
def next_sibling(ls, *args):
    nodeid = args[0][0]
    logging.debug(f"requested next_sibling at {nodeid}")
    current = app.transformer.tree.get_child_by_id(nodeid)
    if current is None:
        logging.debug("no current node")
        return []
    sibling = current.next_sibling()
    if sibling is None:
        logging.debug("no sibling node")
        return []
    return sibling.nodeid


@server.command("prev_sibling")
def prev_sibling(ls, *args):
    nodeid = args[0][0]
    logging.debug(f"requested prev_sibling at {nodeid}")
    return []


def start_server(ws=False):
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

    if ws:
        # use websockets when talking from a browser
        server.start_ws("127.0.0.1", 1234)
    else:
        # use IO when ran as a subprocess
        server.start_io()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ws", default=False, action="store_true")
    args = parser.parse_args()
    start_server(args.ws)
