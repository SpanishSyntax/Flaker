"""Terminal UI, ANSI styling, and interactive menu engine for CLI tools."""

import os
import select
import sys
import termios
import tty
from typing import Any, Sequence


class UI:
    def __init__(self, app_name: str = "flaker", icon: str = "❄️", badge_color: str = "1;34"):
        self.app_name = app_name
        self.icon = icon
        self.badge_color = badge_color
        self._color_mode = "auto"

    def set_color_mode(self, mode: str):
        self._color_mode = mode.lower()

    @property
    def use_color(self) -> bool:
        if self._color_mode == "never":
            return False
        if self._color_mode == "always":
            return True
        if "NO_COLOR" in os.environ:
            return False
        if os.environ.get("CLICOLOR_FORCE", "0") != "0" or "FORCE_COLOR" in os.environ:
            return True
        return sys.stdout.isatty() or os.environ.get("COLORTERM") in ("truecolor", "24bit")

    def style(self, text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.use_color else text

    def bold(self, text: str) -> str:
        return self.style(text, "1")

    def dim(self, text: str) -> str:
        return self.style(text, "90")

    def blue(self, text: str) -> str:
        return self.style(text, "1;34")

    def cyan(self, text: str) -> str:
        return self.style(text, "0;36")

    def bold_cyan(self, text: str) -> str:
        return self.style(text, "1;36")

    def green(self, text: str) -> str:
        return self.style(text, "0;32")

    def bold_green(self, text: str) -> str:
        return self.style(text, "1;32")

    def yellow(self, text: str) -> str:
        return self.style(text, "1;33")

    def red(self, text: str) -> str:
        return self.style(text, "1;31")

    def magenta(self, text: str) -> str:
        return self.style(text, "1;35")

    def badge(self) -> str:
        return self.style(f"{self.icon} [{self.app_name}]", self.badge_color)

    def status(self, symbol: str, message: str, code: str = "1") -> str:
        return f"{self.badge()} {self.style(f'{symbol} {message}', code)}"

    def success(self, msg: str):
        print(self.status("✔", msg, "1;32"))

    def info(self, msg: str, symbol: str = "ℹ️"):
        print(self.status(symbol, msg, "1;34"))

    def warn(self, msg: str):
        print(self.status("⚠️", msg, "1;33"))

    def error(self, msg: str):
        print(self.status("✘", msg, "1;31"), file=sys.stderr)

    def action(self, msg: str, symbol: str = "⚡"):
        print(self.status(symbol, msg, "0;36"))

    def header(self, title: str, width: int = 76):
        border = self.blue("=" * width)
        print(f"\n{border}\n {self.bold(title)}\n{border}")

    def subheader(self, title: str, width: int = 76):
        rule_part = self.dim("-" * max(0, width - len(title) - 5))
        print(f"\n{self.cyan(f'--- {title}')} {rule_part}")

    # -------------------------------------------------------------------------
    # Interactive Terminal Engine (Arrow / Spacebar Menus)
    # -------------------------------------------------------------------------
    def _read_key(self) -> str:
        """Reads a single keypress or ANSI escape sequence from stdin."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                # Check if this is an escape sequence or a single ESC press
                r, _, _ = select.select([sys.stdin], [], [], 0.05)
                if not r:
                    return "esc"
                ch2 = sys.stdin.read(1)
                if ch2 == "[":
                    ch3 = sys.stdin.read(1)
                    if ch3 == "A":
                        return "up"
                    if ch3 == "B":
                        return "down"
                    if ch3 == "C":
                        return "right"
                    if ch3 == "D":
                        return "left"
                    if ch3 in ("1", "2", "3", "4", "5", "6"):
                        sys.stdin.read(1)  # consume trailing '~'
                        return "other"
                return "esc"
            if ch in ("\r", "\n"):
                return "enter"
            if ch == " ":
                return "space"
            if ch == "\x03":  # Ctrl+C
                return "ctrl_c"
            if ch == "\x04":  # Ctrl+D
                return "ctrl_d"
            if ch in ("k", "K"):
                return "up"
            if ch in ("j", "J"):
                return "down"
            if ch in ("a", "A"):
                return "a"
            if ch in ("q", "Q"):
                return "q"
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    @staticmethod
    def _normalize_options(options: Sequence[Any]) -> list[tuple[str, str, str]]:
        """
        Normalizes option entries into (key, label, description).
        Accepts:
          - "name" -> (name, name, "")
          - ("key", "label") -> (key, label, "")
          - ("key", "label", "description") -> (key, label, description)
        """
        result = []
        for opt in options:
            if isinstance(opt, (list, tuple)):
                if len(opt) == 1:
                    result.append((str(opt[0]), str(opt[0]), ""))
                elif len(opt) == 2:
                    result.append((str(opt[0]), str(opt[1]), ""))
                else:
                    result.append((str(opt[0]), str(opt[1]), str(opt[2])))
            else:
                result.append((str(opt), str(opt), ""))
        return result

    def select(
        self,
        title: str,
        options: Sequence[Any],
        default_index: int = 0,
    ) -> str:
        """
        Single-select interactive menu with arrow key navigation.
        Returns the chosen option's key.
        """
        items = self._normalize_options(options)
        if not items:
            return ""

        # Fallback for non-interactive / non-TTY
        if not sys.stdin.isatty():
            print(f"\n{self.badge()} {self.bold(title)}")
            for idx, (k, lbl, desc) in enumerate(items, 1):
                extra = f" - {desc}" if desc else ""
                print(f"  [{idx}] {lbl}{extra}")
            ans = input("Choice [1]: ").strip()
            if ans.isdigit() and 1 <= int(ans) <= len(items):
                return items[int(ans) - 1][0]
            return items[0][0]

        current = max(0, min(default_index, len(items) - 1))
        rendered_lines = 0

        # Hide cursor
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        try:
            while True:
                lines = []
                lines.append(f"{self.badge()} {self.bold(title)}")
                lines.append(self.dim("  (Use ↑/↓ or j/k to navigate, Enter to select, q/Ctrl+C to cancel)"))
                lines.append("")

                for idx, (key, label, desc) in enumerate(items):
                    desc_str = f" {self.dim(desc)}" if desc else ""
                    if idx == current:
                        pointer = self.bold_cyan("❯")
                        item_text = self.bold_cyan(label)
                    else:
                        pointer = " "
                        item_text = label
                    lines.append(f"  {pointer} {item_text}{desc_str}")

                # Erase previous frame if already rendered
                if rendered_lines > 0:
                    sys.stdout.write(f"\033[{rendered_lines}F")
                for line in lines:
                    sys.stdout.write(f"\033[2K{line}\n")
                sys.stdout.flush()
                rendered_lines = len(lines)

                key = self._read_key()
                if key == "up":
                    current = (current - 1) % len(items)
                elif key == "down":
                    current = (current + 1) % len(items)
                elif key == "enter":
                    break
                elif key in ("ctrl_c", "ctrl_d", "q", "esc"):
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    raise KeyboardInterrupt

            # Clear interactive block and print clean outcome
            sys.stdout.write(f"\033[{rendered_lines}F")
            for _ in range(rendered_lines):
                sys.stdout.write("\033[2K\n")
            sys.stdout.write(f"\033[{rendered_lines}F")
            print(f"{self.badge()} {self.dim(title)} {self.bold_green(items[current][1])}")
            sys.stdout.flush()
            return items[current][0]
        finally:
            # Restore cursor
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()

    def multiselect(
        self,
        title: str,
        options: Sequence[Any],
        preselected: Sequence[str] | set[str] | None = None,
    ) -> list[str]:
        """
        Multi-select interactive menu with arrow key navigation and spacebar toggling.
        Returns list of selected option keys.
        """
        items = self._normalize_options(options)
        if not items:
            return []

        selected_keys: set[str] = set(preselected) if preselected else set()

        # Fallback for non-interactive / non-TTY
        if not sys.stdin.isatty():
            print(f"\n{self.badge()} {self.bold(title)}")
            for idx, (k, lbl, desc) in enumerate(items, 1):
                mark = "[*]" if k in selected_keys else "[ ]"
                extra = f" - {desc}" if desc else ""
                print(f"  {mark} [{idx}] {lbl}{extra}")
            ans = input("Select numbers (comma/space separated): ").strip()
            chosen = []
            for tok in ans.replace(",", " ").split():
                if tok.isdigit() and 1 <= int(tok) <= len(items):
                    chosen.append(items[int(tok) - 1][0])
            return chosen if chosen else list(selected_keys)

        current = 0
        rendered_lines = 0

        # Hide cursor
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        try:
            while True:
                lines = []
                lines.append(f"{self.badge()} {self.bold(title)}")
                lines.append(self.dim("  (↑/↓ to navigate, Space to toggle, 'a' for all, Enter to confirm)"))
                lines.append("")

                for idx, (key, label, desc) in enumerate(items):
                    is_checked = key in selected_keys
                    if is_checked:
                        check = self.bold_green("[✔]")
                    else:
                        check = self.dim("[ ]")

                    desc_str = f" {self.dim(desc)}" if desc else ""

                    if idx == current:
                        pointer = self.bold_cyan("❯")
                        lbl_styled = self.bold_cyan(label) if is_checked else self.bold(label)
                    else:
                        pointer = " "
                        lbl_styled = self.green(label) if is_checked else label

                    lines.append(f"  {pointer} {check} {lbl_styled}{desc_str}")

                # Erase previous frame if already rendered
                if rendered_lines > 0:
                    sys.stdout.write(f"\033[{rendered_lines}F")
                for line in lines:
                    sys.stdout.write(f"\033[2K{line}\n")
                sys.stdout.flush()
                rendered_lines = len(lines)

                key = self._read_key()
                if key == "up":
                    current = (current - 1) % len(items)
                elif key == "down":
                    current = (current + 1) % len(items)
                elif key == "space":
                    cur_key = items[current][0]
                    if cur_key in selected_keys:
                        selected_keys.remove(cur_key)
                    else:
                        selected_keys.add(cur_key)
                elif key == "a":
                    # Toggle all
                    if len(selected_keys) == len(items):
                        selected_keys.clear()
                    else:
                        selected_keys = {k for k, _, _ in items}
                elif key == "enter":
                    break
                elif key in ("ctrl_c", "ctrl_d", "q", "esc"):
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    raise KeyboardInterrupt

            # Clear interactive block and print clean outcome
            sys.stdout.write(f"\033[{rendered_lines}F")
            for _ in range(rendered_lines):
                sys.stdout.write("\033[2K\n")
            sys.stdout.write(f"\033[{rendered_lines}F")
            chosen_labels = [lbl for k, lbl, _ in items if k in selected_keys]
            print(f"{self.badge()} {self.dim(title)} {self.bold_green(', '.join(chosen_labels) if chosen_labels else 'none')}")
            sys.stdout.flush()
            return [k for k, _, _ in items if k in selected_keys]
        finally:
            # Restore cursor
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()


ui = UI()
