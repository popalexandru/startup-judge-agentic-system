"""Run from the project directory: python -m app.main \"Your idea\"."""

import argparse

from app.graph import graph
from app.state import StartupState


def print_step_update(node_name: str, update: dict) -> None:
    produced_fields = ", ".join(update)
    print(f"[STREAM] {node_name} -> {produced_fields}")


def run_streamed_graph(initial_state: StartupState) -> StartupState:
    final_state: StartupState = dict(initial_state)
    for event in graph.stream(initial_state):
        for node_name, update in event.items():
            print_step_update(node_name, update)
            final_state.update(update)
    return final_state


def main() -> None:
    parser = argparse.ArgumentParser(description="Startup Judge - analyses and verdict")
    parser.add_argument("idea", help="Startup idea, wrapped in quotes")
    args = parser.parse_args()
    if not args.idea.strip():
        parser.error("The startup idea must be a non-empty string.")

    initial_state: StartupState = {"idea": args.idea}
    print("[GRAPH] Starting analysis")
    print(f"[GRAPH] idea: {args.idea}")

    final_state = run_streamed_graph(initial_state)

    print("\nResult")
    print(f"Score: {final_state['final_score']}/100")
    print(f"Verdict: {final_state['verdict']}")
    print(f"Recommendation: {final_state['recommendation']}")


if __name__ == "__main__":
    main()
