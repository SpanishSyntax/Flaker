from typing import Any
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class PlotConfigurator:
    """Applies standard theming and export rules to any Plotly figure."""

    DEFAULT_LAYOUT = {
        "template": "plotly",
        "margin": dict(l=50, r=50, t=60, b=50),
    }

    def __init__(self, fig: go.Figure | None = None):
        # Accept an existing figure (like subplots) or create a new one
        self.fig = fig if fig else go.Figure()

    def apply_theme(self, title: str | None = None, **kwargs) -> go.Figure:
        """Applies your standardized styling without hiding the base Figure object."""
        layout = dict(self.DEFAULT_LAYOUT)
        if title:
            layout["title_text"] = title

        layout.update(kwargs)
        self.fig.update_layout(**layout)
        return self.fig  # Return the raw figure so you can use standard Plotly methods

    def export(self, filepath: str, **kwargs) -> None:
        """Smart export routing based on file extension."""
        if filepath.endswith(".html"):
            settings = {
                "include_plotlyjs": "cdn",
                "default_height": "calc(100vh - 16px)",
                "full_html": True,
            }
            settings.update(kwargs)
            self.fig.write_html(filepath, **settings)
        elif filepath.endswith((".png", ".svg", ".pdf")):
            # Requires `pip install -U kaleido`
            self.fig.write_image(filepath, **kwargs)
        else:
            raise ValueError("Unsupported file format.")
