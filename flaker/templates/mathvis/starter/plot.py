import numpy as np
import plotly.graph_objects as go
from rich import print as rprint

from plotter import PlotConfigurator

OUTPUT_FILE = "index.html"


def generate_l_membrane():
    """Generates the data for the classic MATLAB logo (L-shaped membrane)."""
    # Create a grid from -1 to 1
    x = np.linspace(-1, 1, 60)
    y = np.linspace(-1, 1, 60)
    X, Y = np.meshgrid(x, y)

    # Convert to polar coordinates
    R = np.sqrt(X**2 + Y**2) + 1e-5
    Theta = np.arctan2(Y, X)

    # Shift angle to range [0, 2pi]
    Theta = np.where(Theta < 0, Theta + 2 * np.pi, Theta)

    # The dominant eigenfunction has an angular dependence of sin(2/3 * (theta - pi/2))
    # We multiply by a radial decay function to create the curved peak
    Z = np.sin(2 / 3 * (Theta - np.pi / 2)) * (R ** (2 / 3)) * np.exp(-R)

    # Mask out the first quadrant (x > 0 and y > 0) to create the "L" shape
    mask = (X > 0) & (Y > 0)
    Z[mask] = np.nan

    return x, y, Z


def main():
    rprint(
        "[bold cyan]🥚 TU Delft / Systems & Control Easter Egg Initialized[/bold cyan]"
    )
    rprint("[bold]Rendering:[/bold] First Eigenfunction of the L-Shaped Membrane...")

    config = PlotConfigurator()
    fig = config.fig

    x, y, z = generate_l_membrane()

    # Add the 3D surface plot
    fig.add_trace(
        go.Surface(
            x=x,
            y=y,
            z=z,
            colorscale="Jet",  # The classic retro MATLAB colorscale
            showscale=False,  # Hide the colorbar for a clean logo look
            contours=dict(
                z=dict(
                    show=True, usecolormap=True, highlightcolor="white", project_z=True
                )
            ),
        )
    )

    # Theme it as a floating logo without gridlines or axes
    config.apply_theme(
        title="<b>Why MATLAB?</b><br><sup>First Eigenfunction of the L-shaped Membrane</sup>",
        paper_bgcolor="#f4f4f9",  # Matches your HTML template background
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(
                eye=dict(x=-1.5, y=-1.5, z=1.2)  # Classic MATLAB viewing angle
            ),
        ),
    )

    config.export(OUTPUT_FILE)
    rprint(
        f"✅ [bold green]Membrane rendered and injected into {OUTPUT_FILE}[/bold green]"
    )


if __name__ == "__main__":
    main()
