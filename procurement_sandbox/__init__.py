"""Procurement sandbox - not SAP connected.

An S/4HANA-shaped OData v2 mock of the purchase order, material stock and
purchase requisition APIs, persisted in SQLite, for wiring Demand Pulse to a
procurement object. See CONTRACT.md.
"""

from .app import create_app  # noqa: F401
