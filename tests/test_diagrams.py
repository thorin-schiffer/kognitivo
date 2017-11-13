from tests import control, assertions


def test_diagram_labels():
    from screens.activity.diagrams.base import DiagramLabelsContainer

    labels_container = DiagramLabelsContainer()
    assert not labels_container.children
    labels_container.values = [1, 2]
    assert len(labels_container.children), 2
    assert labels_container.children[1].text == "1"


def test_diagram_labels_empty():
    from screens.activity.diagrams.base import DiagramLabelsContainer

    labels_container = DiagramLabelsContainer()
    assert not labels_container.children
    labels_container.values = []
    assert not labels_container.children


def test_diagram_elements_zero_data():
    from screens.activity.diagrams.base import DiagramElementsContainer

    elements_container = DiagramElementsContainer()
    elements_container.values = [0, 0, 0]
    assert elements_container.normal_level_line.points == []


def test_diagram_elements_container():
    from screens.activity.diagrams.base import DiagramElementsContainer

    elements_container = DiagramElementsContainer()
    assert elements_container.fill_color is None
    assert elements_container.normal_level_line is None
    assert elements_container.normal_level_label is None
    assert elements_container.half_level_line is None
    assert elements_container.half_level_label is None
    elements_container.values = [1, 2]
    assert elements_container.fill_color is not None
    assert elements_container.normal_level_line is not None
    assert elements_container.normal_level_label is not None
    assert elements_container.half_level_line is not None
    assert elements_container.half_level_label is not None
    elements_container.color = (1, 1, 0)


def test_diagram_elements_container_empty():
    from screens.activity.diagrams.base import DiagramElementsContainer

    elements_container = DiagramElementsContainer()
    elements_container.values = []
    assert elements_container.fill_color is None
    assert elements_container.normal_level_line is None
    assert elements_container.normal_level_label is None
    assert elements_container.half_level_line is None
    assert elements_container.half_level_label is None


def test_diagram_elements_container_placement_inside():
    from screens.activity.diagrams.base import DiagramElementsContainer

    elements_container = DiagramElementsContainer()
    elements_container.values = [1, 2, 3, 4]

    assert elements_container.normal_level_line.points[1] == elements_container.height * .25
    assert elements_container.half_level_line.points[1] == elements_container.height * .125

    assert elements_container.normal_level_label.y == elements_container.height * .25
    assert elements_container.half_level_label.y == elements_container.height * .125


def test_diagram_elements_container_placement_under_100(running_app):
    from screens.activity.diagrams.base import DiagramElementsContainer

    elements_container = DiagramElementsContainer()
    elements_container.values = [0.1, 0.2, 0.3, 0.4]

    assert elements_container.normal_level_line.points[1] == running_app.root_window.height
    assert elements_container.half_level_line.points[1] == running_app.root_window.height

    assert elements_container.normal_level_label.y == running_app.root_window.height
    assert elements_container.half_level_label.y == running_app.root_window.height


def test_bar_diagram_elements_container():
    from screens.activity.diagrams.base import BarDiagramElementsContainer

    bar_container = BarDiagramElementsContainer()
    assert bar_container.bars is None
    bar_container.values = [1, 2, 3, 4]
    assert len(bar_container.bars) == 4
    # max bar + ellipse half size has the whole height of container
    assert bar_container.bars[3][0].size[1] / 2 + bar_container.bars[3][1].size[1] == bar_container.height


def test_bar_diagram_elements_zero_negative_data():
    from screens.activity.diagrams.base import BarDiagramElementsContainer

    bar_container = BarDiagramElementsContainer()
    assert bar_container.bars is None
    bar_container.values = [-1, 0, 0, 4]
    assert bar_container.bars[0][0].size == (0, 0)
    assert bar_container.bars[0][1].size == (0, 0)
    assert bar_container.bars[1][0].size == (0, 0)
    assert bar_container.bars[1][1].size == (0, 0)


def test_filled_line_diagram_elements_container():
    from screens.activity.diagrams.base import FilledLineDiagramElementsContainer

    elements_container = FilledLineDiagramElementsContainer()
    assert elements_container.quads is None
    elements_container.values = [1, 2, 3, 4]
    assert len(elements_container.quads) == 3
    assert elements_container.quads[2].points[5] == elements_container.height


def test_filled_line_diagram_elements_zero_negative():
    from screens.activity.diagrams.base import FilledLineDiagramElementsContainer

    elements_container = FilledLineDiagramElementsContainer()
    assert elements_container.quads is None
    elements_container.values = [-1, 0, 0, 4]
    assert elements_container.quads[0].points[3] == 0
    assert elements_container.quads[1].points[3] == 0


def test_filled_line_diagram_elements_length_1():
    from screens.activity.diagrams.base import FilledLineDiagramElementsContainer

    elements_container = FilledLineDiagramElementsContainer()
    assert elements_container.quads is None
    elements_container.values = [-1]


def test_abstract_diagram():
    from screens.activity.diagrams.base import Diagram, DiagramElementsContainer, DiagramLabelsContainer

    diagram = Diagram()
    diagram.labels_container = DiagramLabelsContainer()
    diagram.elements_container = DiagramElementsContainer()

    diagram.values = {1: 3, 2: 4}
    assert diagram.labels_container.values == [1, 2]
    assert diagram.elements_container.values == [3, 4]
    diagram.color = (1, 1, 1, 1)
    assert diagram.elements_container.fill_color.rgba == diagram.color


def test_day_stats_diagram_empty_ok(empty_data, running_app, root_manager):
    from screens.activity.diagrams import ActivityDayStats
    import settings

    diagram = ActivityDayStats()
    for family in [None, settings.ANALYTICS_FAMILY, settings.ATTENTION_FAMILY, settings.REACTION_FAMILY,
                   settings.MEMORY_FAMILY]:
        diagram.family = family
        assert diagram.color == settings.ACTIVITY_COLORS_TRANSPARENT[family]

    from library_widgets import OkCancelPopup

    assertions.assert_modal_view_shown(running_app, OkCancelPopup)
    popup = control.get_popups(running_app)[0]
    control.press(popup.ok_button)
    assert root_manager.current == 'tasks'
    assertions.assert_modal_view_not_shown(running_app, OkCancelPopup)


def test_day_stats_diagram_empty_cancel(empty_data, running_app, root_manager):
    from screens.activity.diagrams import ActivityDayStats
    import settings

    diagram = ActivityDayStats()
    for family in [None, settings.ANALYTICS_FAMILY, settings.ATTENTION_FAMILY, settings.REACTION_FAMILY,
                   settings.MEMORY_FAMILY]:
        diagram.family = family
        assert diagram.color == settings.ACTIVITY_COLORS_TRANSPARENT[family]

    from library_widgets import OkCancelPopup

    assertions.assert_modal_view_shown(running_app, OkCancelPopup)
    popup = control.get_popups(running_app)[0]
    control.press(popup.cancel_button)
    assert root_manager.current == 'activity'
    assertions.assert_modal_view_not_shown(running_app, OkCancelPopup)


def test_day_stats_diagram_not_empty(not_empty_data, running_app, root_manager):
    from screens.activity.diagrams import ActivityDayStats
    import settings

    diagram = ActivityDayStats()
    diagram.family = None
    from library_widgets import OkCancelPopup

    assertions.assert_modal_view_not_shown(running_app, OkCancelPopup)
    assert diagram.values

    # press again to trigger animations
    diagram.family = settings.ATTENTION_FAMILY
