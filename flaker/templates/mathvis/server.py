import os
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from rich import print as rprint

HTML_FILE = "index.html"

# JavaScript snippet dynamically injected into the HTML
AUTO_RELOAD_JS = b"""
<script>
  let lastMtime = null;
  setInterval(() => {
    fetch('/_mtime')
      .then(response => response.text())
      .then(mtime => {
        if (lastMtime === null) {
          lastMtime = mtime; // Initial load
        } else if (lastMtime !== mtime) {
          console.log("File change detected. Reloading...");
          location.reload(); // Refresh browser
        }
      })
      .catch(err => {}); // Fail silently if server restarts
  }, 1000); // Check every second
</script>
"""


class DynamicFileHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Keep the terminal quiet

    def do_GET(self):
        # 1. Handle the hidden timestamp checking endpoint
        if self.path == "/_mtime":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            if os.path.exists(HTML_FILE):
                mtime = str(os.path.getmtime(HTML_FILE))
                self.wfile.write(mtime.encode("utf-8"))
            else:
                self.wfile.write(b"0")
            return

        # 2. Handle the standard index.html request
        if not os.path.exists(HTML_FILE):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404: Dashboard file not found.")
            return

        with open(HTML_FILE, "rb") as f:
            content = f.read()

        # Inject the auto-reload script securely before the closing body tag
        if b"</body>" in content:
            content = content.replace(b"</body>", AUTO_RELOAD_JS + b"</body>")
        else:
            # Fallback if Plotly formats it weirdly
            content += AUTO_RELOAD_JS

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main():
    server = HTTPServer(("127.0.0.1", 0), DynamicFileHandler)
    host, port, *_ = server.server_address

    rprint(
        "\n[bold box]─────────────────────────────────────────────────────────────────[/bold box]"
    )
    rprint(" 🚀 [bold green]Live-Reload Dashboard Server Active[/bold green]")
    rprint(f" 🌐 Target URL: [bold cyan]http://{host}:{port}[/bold cyan]")
    rprint(f" 📄 Serving: [yellow]{os.path.abspath(HTML_FILE)}[/yellow]")
    rprint(
        "[bold box]─────────────────────────────────────────────────────────────────[/bold box]\n"
    )

    # 1. Open the browser FIRST
    webbrowser.open(f"http://{host}:{port}")

    # 2. THEN start the blocking server loop
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        rprint("\n[bold red]Shutting down dashboard server...[/bold red]")
        server.server_close()


if __name__ == "__main__":
    main()
