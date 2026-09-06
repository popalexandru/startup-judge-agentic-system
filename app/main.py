"""Run from the project directory: python -m app.main \"Your idea\"."""

import argparse

from rich.console import Console

from app.graph import MAX_ITERATIONS, graph, route_after_judge
from app.state import StartupState

console = Console()


def print_step_update(node_name: str, update: dict) -> None:
    produced_fields = ", ".join(update)
    console.print(
        "[bold green][STREAM][/bold green] "
        f"[cyan]{node_name}[/cyan] -> [white]{produced_fields}[/white]"
    )


def print_route_after_judge(state: StartupState) -> None:
    route = route_after_judge(state)
    verdict = state["verdict"]
    iteration = state.get("iteration", 0)

    if route == "improve":
        console.print(
            "[bold yellow][ROUTE][/bold yellow] "
            f"[red]{verdict}[/red] at iteration {iteration}/{MAX_ITERATIONS} -> "
            "[yellow]improve[/yellow]"
        )
    else:
        console.print(
            "[bold yellow][ROUTE][/bold yellow] "
            f"[green]{verdict}[/green] -> [yellow]end[/yellow]"
        )


def run_streamed_graph(initial_state: StartupState) -> StartupState:
    final_state: StartupState = dict(initial_state)
    for event in graph.stream(initial_state):
        for node_name, update in event.items():
            print_step_update(node_name, update)
            final_state.update(update)
            if node_name == "judge":
                print_route_after_judge(final_state)
    return final_state


def print_sources(state: StartupState) -> None:
    sources = state.get("research_sources", [])
    if not sources:
        return

    console.print("\n[bold]Research Sources[/bold]")
    for index, source in enumerate(sources[:3], start=1):
        console.print(f"{index}. [cyan]{source['title']}[/cyan]")
        console.print(f"   [blue]{source['url']}[/blue]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Startup Judge - analyses and verdict")
    parser.add_argument("idea", help="Startup idea, wrapped in quotes")
    args = parser.parse_args()
    if not args.idea.strip():
        parser.error("The startup idea must be a non-empty string.")

    initial_state: StartupState = {"idea": args.idea}
    console.print("[bold blue][GRAPH][/bold blue] Starting analysis")
    console.print(f"[bold blue][GRAPH][/bold blue] idea: [white]{args.idea}[/white]")

    final_state = run_streamed_graph(initial_state)

    console.print("\n[bold]Result[/bold]")
    console.print(f"[bold]Score:[/bold] {final_state['final_score']}/100")
    console.print(f"[bold]Verdict:[/bold] {final_state['verdict']}")
    console.print(f"[bold]Recommendation:[/bold] {final_state['recommendation']}")
    print_sources(final_state)


if __name__ == "__main__":
    main()
