"""FlowLite layout engines.

Layout is a pluggable stage: an engine receives a measured
:class:`~flowlite.model.Diagram` and assigns positions, returning the diagram
plus the canvas size. Later changes add layered and radial engines; the renderer
stays agnostic to which one ran.
"""
