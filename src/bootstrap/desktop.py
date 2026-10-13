"""PySide6 desktop shell — thin wrapper around ChannelPipeline."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget,
)

from src.bootstrap.cli import _build_pipeline
from src.config.settings import load_settings
from src.utils.logging_setup import configure_logging


class PipelineWorker(QThread):
    line = Signal(str)
    done = Signal(int)

    def __init__(self, config_path: Path | None, topic: str, count: int, dry_run: bool) -> None:
        super().__init__()
        self._config_path = config_path
        self._topic = topic
        self._count = count
        self._dry_run = dry_run

    def run(self) -> None:  # noqa: D401
        pipeline = _build_pipeline(self._config_path)
        pipeline.on_log = self.line.emit
        rc = asyncio.run(pipeline.run(self._topic, self._count, self._dry_run))
        self.done.emit(rc)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("faceless-yt-channel-generator")
        self.resize(880, 620)
        self._config_path: Path | None = None

        root = QWidget()
        layout = QVBoxLayout(root)

        cfg_row = QHBoxLayout()
        self.cfg_label = QLabel("config: default")
        cfg_btn = QPushButton("Load config…")
        cfg_btn.clicked.connect(self._pick_config)
        cfg_row.addWidget(cfg_btn)
        cfg_row.addWidget(self.cfg_label)
        layout.addLayout(cfg_row)

        self.topic = QLineEdit()
        self.topic.setPlaceholderText("topic seed (e.g. 'stoic philosophy for night shift workers')")
        layout.addWidget(self.topic)

        self.count = QLineEdit("1")
        layout.addWidget(self.count)

        run_row = QHBoxLayout()
        self.run_btn = QPushButton("Generate")
        self.run_btn.clicked.connect(self._run)
        self.dry_btn = QPushButton("Dry run")
        self.dry_btn.clicked.connect(lambda: self._run(dry=True))
        run_row.addWidget(self.run_btn)
        run_row.addWidget(self.dry_btn)
        layout.addLayout(run_row)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)
        self.setCentralWidget(root)

    def _pick_config(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select config", str(Path.cwd()), "TOML (*.toml)")
        if path:
            self._config_path = Path(path)
            self.cfg_label.setText(f"config: {path}")

    def _run(self, dry: bool = False) -> None:
        topic = self.topic.text().strip()
        if not topic:
            self.log_view.append("[warn] topic is empty")
            return
        try:
            count = max(1, int(self.count.text().strip() or "1"))
        except ValueError:
            count = 1
        self.run_btn.setEnabled(False)
        self._worker = PipelineWorker(self._config_path, topic, count, dry)
        self._worker.line.connect(self.log_view.append)
        self._worker.done.connect(self._on_done)
        self._worker.start()

    def _on_done(self, rc: int) -> None:
        self.run_btn.setEnabled(True)
        self.log_view.append(f"[done] exit code {rc}")


def main() -> int:
    configure_logging(verbose=False)
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())