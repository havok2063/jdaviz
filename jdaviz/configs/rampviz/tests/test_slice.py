import pytest
from jdaviz.configs.cubeviz.plugins.slice.slice import Slice
from jdaviz.configs.imviz.plugins.parsers import HAS_ROMAN_DATAMODELS


@pytest.mark.skipif(not HAS_ROMAN_DATAMODELS, reason="roman_datamodels is not installed")
def test_slice(rampviz_helper, roman_level_1_ramp):
    app = rampviz_helper.app
    sl = Slice(app=app)

    # No data yet
    assert len(sl.slice_selection_viewers) == 2  # group-viewer, diff-viewer
    assert len(sl.slice_indicator_viewers) == 1  # integration-viewer
    assert len(sl.valid_indicator_values_sorted) == 0
    assert len(sl.valid_selection_values_sorted) == 0

    # Make sure nothing crashes if plugin used without data]
    sl.vue_play_next()
    sl.vue_play_start_stop()
    assert not sl.is_playing

    rampviz_helper.load_data(roman_level_1_ramp, data_label='test')
    app.add_data_to_viewer("group-viewer", "test[DATA]")
    app.add_data_to_viewer("diff-viewer", "test[DATA]")
    app.add_data_to_viewer("integration-viewer", "Ramp (mean)")
    sv = rampviz_helper.viewers['integration-viewer']._obj

    # sample ramp only has 10 groups
    assert len(sv.slice_values) == 10
    assert len(sl.valid_indicator_values_sorted) == 10
    slice_values = sl.valid_selection_values_sorted
    assert len(slice_values) == 10

    assert sl.value == slice_values[len(slice_values) // 2]
    assert rampviz_helper.app.get_viewer("group-viewer").slice == len(slice_values) // 2
    assert rampviz_helper.app.get_viewer("group-viewer").state.slices[-1] == 5
    assert rampviz_helper.app.get_viewer("diff-viewer").state.slices[-1] == 5
    rampviz_helper.select_group(slice_values[0])
    assert rampviz_helper.app.get_viewer("group-viewer").slice == 0
    assert sl.value == slice_values[0]

    rampviz_helper.select_group(slice_values[1])
    assert sl.value == slice_values[1]

    # Retrieve updated slice_values
    slice_values = sl.valid_selection_values_sorted

    # Test player buttons API

    sl.vue_goto_first()
    assert sl.value == slice_values[0]

    sl.vue_goto_last()
    assert sl.value == slice_values[-1]

    sl.vue_play_next()  # Should automatically wrap to beginning
    assert sl.value == slice_values[0]

    sl.vue_play_start_stop()  # Start
    assert sl.is_playing
    assert sl._player.is_alive()
    sl.vue_play_next()  # Should be no-op
    sl.vue_goto_last()  # Should be no-op
    sl.vue_goto_first()  # Should be no-op
    sl.vue_play_start_stop()  # Stop
    assert not sl.is_playing
    assert not sl._player
    # NOTE: Hard to check sl.slice here because it is non-deterministic.


@pytest.mark.skipif(not HAS_ROMAN_DATAMODELS, reason="roman_datamodels is not installed")
def test_indicator_settings(rampviz_helper, roman_level_1_ramp):
    rampviz_helper.load_data(roman_level_1_ramp, data_label='test')
    app = rampviz_helper.app
    app.add_data_to_viewer("group-viewer", "test[DATA]")
    app.add_data_to_viewer("integration-viewer", "Ramp (mean)")
    sl = rampviz_helper.plugins['Slice']._obj
    sv = app.get_viewer('integration-viewer')
    indicator = sv.slice_indicator

    assert sl.show_indicator is True
    assert indicator._show_if_inactive is True
    assert sl.show_value is True
    assert indicator.label.visible is True

    sl.show_indicator = False
    assert indicator._show_if_inactive is False

    sl.show_value = False
    assert indicator.label.visible is False


@pytest.mark.skipif(not HAS_ROMAN_DATAMODELS, reason="roman_datamodels is not installed")
def test_init_slice(rampviz_helper, roman_level_1_ramp):
    rampviz_helper.load_data(roman_level_1_ramp, data_label='test')

    fv = rampviz_helper.app.get_viewer('group-viewer')
    sl = rampviz_helper.plugins['Slice']
    slice_values = sl._obj.valid_selection_values_sorted

    assert sl.value == slice_values[len(slice_values)//2]
    assert fv.slice == 5
    assert fv.state.slices == (0, 0, 5)
