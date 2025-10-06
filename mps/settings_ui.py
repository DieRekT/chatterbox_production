from __future__ import annotations

import json
import os
from typing import Dict, Any

from PyQt6 import QtCore, QtWidgets

from .settings_loader import (
    resolve_settings,
    save_user_settings,
    export_user_settings,
    import_user_settings,
    reset_user_settings,
)


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(640, 480)
        self._vars: dict[str, QtWidgets.QLineEdit] = {}

        layout = QtWidgets.QVBoxLayout(self)
        tabs = QtWidgets.QTabWidget()
        layout.addWidget(tabs, 1)

        s = resolve_settings()

        # App tab
        tab_app = QtWidgets.QWidget()
        form_app = QtWidgets.QFormLayout(tab_app)
        form_app.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self._add_field(form_app, "app.log_level", s.app.log_level)
        self._add_field(form_app, "app.ui_theme", s.app.ui_theme)
        tabs.addTab(tab_app, "App")

        # Storage tab
        tab_storage = QtWidgets.QWidget()
        form_st = QtWidgets.QFormLayout(tab_storage)
        form_st.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self._add_field(form_st, "storage.recordings_dir", s.storage.recordings_dir)
        self._add_field(form_st, "storage.snapshots_dir", s.storage.snapshots_dir)
        self._add_field(form_st, "storage.max_days_to_keep", str(s.storage.max_days_to_keep))
        tabs.addTab(tab_storage, "Storage")

        # Video tab (devices only, minimal)
        tab_video = QtWidgets.QScrollArea()
        tab_video.setWidgetResizable(True)
        inner = QtWidgets.QWidget()
        form_vid = QtWidgets.QFormLayout(inner)
        form_vid.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        for cam_name, cam in s.video.cams.items():
            self._add_field(form_vid, f"video.cams.{cam_name}.device", cam.device)
        tab_video.setWidget(inner)
        tabs.addTab(tab_video, "Video")

        # Motion tab
        tab_motion = QtWidgets.QWidget()
        form_m = QtWidgets.QFormLayout(tab_motion)
        form_m.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self._add_field(form_m, "motion.enabled", str(s.motion.enabled).lower())
        self._add_field(form_m, "motion.sensitivity", str(s.motion.sensitivity))
        self._add_field(form_m, "motion.min_area_px", str(s.motion.min_area_px))
        tabs.addTab(tab_motion, "Motion")

        # Buttons
        btns = QtWidgets.QHBoxLayout()
        layout.addLayout(btns)
        btn_save = QtWidgets.QPushButton("Save")
        btn_export = QtWidgets.QPushButton("Export")
        btn_import = QtWidgets.QPushButton("Import")
        btn_reset = QtWidgets.QPushButton("Reset")
        btn_close = QtWidgets.QPushButton("Close")
        for b in (btn_save, btn_export, btn_import, btn_reset):
            btns.addWidget(b)
        btns.addStretch(1)
        btns.addWidget(btn_close)

        btn_save.clicked.connect(self._save)
        btn_export.clicked.connect(self._export)
        btn_import.clicked.connect(self._import)
        btn_reset.clicked.connect(self._reset)
        btn_close.clicked.connect(self.accept)

    def _add_field(self, form: QtWidgets.QFormLayout, key: str, value: str) -> None:
        edit = QtWidgets.QLineEdit()
        edit.setText(value)
        edit.setPlaceholderText(key)
        self._vars[key] = edit
        form.addRow(QtWidgets.QLabel(key), edit)

    def _save(self) -> None:
        patch: Dict[str, Any] = {}
        for k, widget in self._vars.items():
            self._assign(patch, k.split("."), widget.text())
        try:
            save_user_settings(patch)
            QtWidgets.QMessageBox.information(self, "Settings", "Saved. Some changes may require restart.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Settings", f"Failed to save: {e}")

    def _assign(self, d: Dict[str, Any], keys: list[str], val: str) -> None:
        cur: Dict[str, Any] = d
        for k in keys[:-1]:
            cur = cur.setdefault(k, {})  # type: ignore[assignment]
        # basic casts
        if val in ("true", "false"):
            scalar: Any = (val == "true")
        else:
            try:
                scalar = float(val) if "." in val else int(val)
            except Exception:
                scalar = val
        cur[keys[-1]] = scalar

    def _export(self) -> None:
        data = export_user_settings()
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Settings", os.getcwd(), "JSON (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            QtWidgets.QMessageBox.information(self, "Export", "Exported settings.")

    def _import(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Settings", os.getcwd(), "JSON (*.json)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                import_user_settings(data)
                QtWidgets.QMessageBox.information(self, "Import", "Imported. Restart recommended.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Import failed", str(e))

    def _reset(self) -> None:
        reset_user_settings()
        QtWidgets.QMessageBox.information(self, "Reset", "Settings reset to defaults.")

import json
from typing import Dict, Any
from PyQt6 import QtWidgets

from .settings_loader import (
    resolve_settings,
    save_user_settings,
    export_user_settings,
    import_user_settings,
    reset_user_settings,
)


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(640, 480)

        layout = QtWidgets.QVBoxLayout(self)

        tabs = QtWidgets.QTabWidget()
        layout.addWidget(tabs, 1)

        s = resolve_settings()
        self._fields: Dict[str, QtWidgets.QLineEdit] = {}

        # App
        w_app = QtWidgets.QWidget(); tabs.addTab(w_app, "App")
        app_form = QtWidgets.QFormLayout(w_app)
        self._add_field(app_form, "app.log_level", s.app.log_level)
        self._add_field(app_form, "app.ui_theme", s.app.ui_theme)

        # Storage
        w_store = QtWidgets.QWidget(); tabs.addTab(w_store, "Storage")
        st_form = QtWidgets.QFormLayout(w_store)
        self._add_field(st_form, "storage.recordings_dir", s.storage.recordings_dir)
        self._add_field(st_form, "storage.snapshots_dir", s.storage.snapshots_dir)
        self._add_field(st_form, "storage.max_days_to_keep", str(s.storage.max_days_to_keep))

        # Video (devices only for brevity)
        w_vid = QtWidgets.QWidget(); tabs.addTab(w_vid, "Video")
        v_form = QtWidgets.QFormLayout(w_vid)
        for cam_name, cam in s.video.cams.items():
            self._add_field(v_form, f"video.cams.{cam_name}.device", cam.device)

        # Motion
        w_mot = QtWidgets.QWidget(); tabs.addTab(w_mot, "Motion")
        m_form = QtWidgets.QFormLayout(w_mot)
        self._add_field(m_form, "motion.enabled", str(s.motion.enabled).lower())
        self._add_field(m_form, "motion.sensitivity", str(s.motion.sensitivity))
        self._add_field(m_form, "motion.min_area_px", str(s.motion.min_area_px))

        # Buttons
        btns = QtWidgets.QDialogButtonBox()
        btn_save = btns.addButton("Save", QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        btn_export = btns.addButton("Export", QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        btn_import = btns.addButton("Import", QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        btn_reset = btns.addButton("Reset", QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        btn_close = btns.addButton("Close", QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
        layout.addWidget(btns)

        btn_save.clicked.connect(self._save)
        btn_export.clicked.connect(self._export)
        btn_import.clicked.connect(self._import)
        btn_reset.clicked.connect(self._reset)
        btn_close.clicked.connect(self.reject)

    def _add_field(self, form: QtWidgets.QFormLayout, key: str, value: str) -> None:
        le = QtWidgets.QLineEdit(self)
        le.setText(value)
        form.addRow(key, le)
        self._fields[key] = le

    def _save(self) -> None:
        patch: Dict[str, Any] = {}
        for k, widget in self._fields.items():
            self._assign(patch, k.split("."), widget.text())
        try:
            save_user_settings(patch)
            QtWidgets.QMessageBox.information(self, "Settings", "Saved. Some changes may require restart.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Settings", f"Failed to save: {e}")

    def _assign(self, d: Dict[str, Any], keys: list[str], val: str) -> None:
        cur: Dict[str, Any] = d
        for k in keys[:-1]:
            if k not in cur or not isinstance(cur[k], dict):
                cur[k] = {}
            cur = cur[k]  # type: ignore[index]
        # try to cast
        val_cast: Any = val
        if val in ("true", "false"):
            val_cast = val == "true"
        else:
            try:
                if "." in val:
                    val_cast = float(val)
                else:
                    val_cast = int(val)
            except Exception:
                val_cast = val
        cur[keys[-1]] = val_cast

    def _export(self) -> None:
        data = export_user_settings()
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Settings", filter="JSON (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            QtWidgets.QMessageBox.information(self, "Export", "Exported settings.")

    def _import(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Settings", filter="JSON (*.json)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                import_user_settings(data)
                QtWidgets.QMessageBox.information(self, "Import", "Imported. Restart recommended.")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Import failed", str(e))

    def _reset(self) -> None:
        reset_user_settings()
        QtWidgets.QMessageBox.information(self, "Reset", "Settings reset to defaults.")
