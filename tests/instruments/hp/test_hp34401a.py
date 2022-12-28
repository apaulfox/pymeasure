#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import pytest
import math
import time
import logging
from pymeasure.instruments.hp import HP34401A

# pytest.skip('Only work with connected hardware', allow_module_level=True)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TestHP8116A:
    """
    Unit tests for HP34401A class.

    This test suite, needs the following setup to work properly:
        - A HP34401A device should be connected to the computer;
        - The device's address must be set in the RESOURCE constant.
    """

    RESOURCE = 'GPIB0::16'
    instr = HP34401A(RESOURCE)

    FUNCTIONS = ["DCV", "DCV_RATIO", "ACV", "DCI", "ACI", "R2W",
                 "R4W", "FREQ", "PERIOD", "CONTINUITY", "DIODE"]

    FUNCTIONS_WITH_RANGE = ["DCV", "ACV", "DCI", "ACI",
                            "R2W", "R4W", "FREQ", "PERIOD"]

    TEST_RANGES = {
        "DCV": [0.1, 1, 10], "ACV": [0.1, 1, 10], "DCI": [0.1, 1, 3],
        "ACI": [1, 3], "R2W": [100, 1e3, 10e3], "R4W": [100, 1e3, 10e3],
        "FREQ": [0.1, 1, 10], "PERIOD": [0.1, 1, 10]}

    @pytest.fixture
    def make_resetted_instr(self):
        self.instr.reset()
        self.instr.check_errors()
        self.instr.write("*RST")
        self.instr.reset()
        return self.instr

    def test_correct_model_by_idn(self, make_resetted_instr):
        instr = make_resetted_instr
        assert "34401a" in instr.id.lower()

    @pytest.mark.parametrize("function_", FUNCTIONS)
    def test_given_function_when_set_then_function_is_set(self, make_resetted_instr, function_):
        instr = make_resetted_instr
        instr.function_ = function_
        assert len(instr.check_errors()) == 0
        assert instr.function_ == function_

    @pytest.mark.parametrize("function_", FUNCTIONS)
    def test_given_function_is_set_then_reading_avaliable(self, make_resetted_instr, function_):
        instr = make_resetted_instr
        instr.function_ = function_
        assert len(instr.check_errors()) == 0
        assert instr.reading is not None

    @pytest.mark.parametrize("function_", FUNCTIONS_WITH_RANGE)
    def test_given_function_is_set_then_range_avaliable(self, make_resetted_instr, function_):
        instr = make_resetted_instr
        instr.function_ = function_
        assert len(instr.check_errors()) == 0
        assert instr.range_ is not None

    @pytest.mark.parametrize("function_", FUNCTIONS_WITH_RANGE)
    def test_given_function_is_set_then_auto_range_is_enabled(self, make_resetted_instr, function_):
        instr = make_resetted_instr
        instr.function_ = function_
        assert len(instr.check_errors()) == 0
        assert instr.auto_range_enabled == True

    @pytest.mark.parametrize("function_", FUNCTIONS_WITH_RANGE)
    def test_given_function_and_range_when_set_then_ratio_correct(self, make_resetted_instr, function_):
        for range in self.TEST_RANGES[function_]:
            instr = make_resetted_instr
            instr.function_ = function_
            instr.range_ = range
            assert len(instr.check_errors()) == 0
            assert instr.range_ == range

    @pytest.mark.parametrize("function_", FUNCTIONS_WITH_RANGE)
    def test_autorange_enable(self, make_resetted_instr, function_):
        instr = make_resetted_instr
        instr.function_ = function_
        instr.auto_range_enabled = True
        assert len(instr.check_errors()) == 0
        assert instr.auto_range_enabled == True

    @pytest.mark.parametrize("function_", FUNCTIONS_WITH_RANGE)
    def test_autorange_disable(self, make_resetted_instr, function_):
        instr = make_resetted_instr
        instr.function_ = function_
        instr.auto_range_enabled = False
        assert len(instr.check_errors()) == 0
        assert instr.auto_range_enabled == False

    def test_dcv_range_min_max(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.function_ = "DCV"
        instr.range_ = "MIN"
        assert len(instr.check_errors()) == 0
        assert instr.range_ == 0.1
        instr.range_ = "MAX"
        assert len(instr.check_errors()) == 0
        assert instr.range_ == 1000

    def test_display_enable(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.display_enabled = True
        assert len(instr.check_errors()) == 0
        assert instr.display_enabled == True

    def test_display_disable(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.display_enabled = False
        assert len(instr.check_errors()) == 0
        assert instr.display_enabled == False

    @pytest.mark.parametrize("function_", ["DCV", "ACV", "DCI", "R2W"])
    def test_resolution(self, make_resetted_instr, function_):
        instr: HP34401A = make_resetted_instr
        instr.function_ = function_
        instr.range_ = 1
        instr.resolution = 0.0001
        assert len(instr.check_errors()) == 0
        assert instr.resolution == 0.0001

    @pytest.mark.parametrize("function_", ["DCV", "DCI", "R2W"])
    @pytest.mark.parametrize("nplc", [0.02, 1, 100])
    def test_nplc(self, make_resetted_instr, function_, nplc):
        instr = make_resetted_instr
        instr.function_ = function_
        instr.nplc = nplc
        assert len(instr.check_errors()) == 0
        assert instr.nplc == nplc

    @pytest.mark.parametrize("function_", ["FREQ", "PERIOD"])
    @pytest.mark.parametrize("gate_time", [0.01, 0.01, 1])
    def test_gate_time(self, make_resetted_instr, function_, gate_time):
        instr = make_resetted_instr
        instr.function_ = function_
        instr.gate_time = gate_time
        assert len(instr.check_errors()) == 0
        assert instr.gate_time == gate_time

    @pytest.mark.parametrize("detector_bandwidth", [3, 20, 200])
    def test_detector_bandwidth(self, make_resetted_instr, detector_bandwidth):
        instr = make_resetted_instr
        instr.function_ = "FREQ"
        instr.detector_bandwidth = detector_bandwidth
        assert len(instr.check_errors()) == 0
        assert instr.detector_bandwidth == detector_bandwidth

    @pytest.mark.parametrize("enable", [True, False])
    def test_autozero(self, make_resetted_instr, enable):
        instr = make_resetted_instr
        instr.autozero_enabled = enable
        assert len(instr.check_errors()) == 0
        assert instr.autozero_enabled == enable

    def test_single_autozero(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.autozero_enabled = True
        instr.trigger_single_autozero()
        assert len(instr.check_errors()) == 0
        assert instr.autozero_enabled == False

    def test_auto_input_impedance(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.auto_input_impedance_enabled = True
        assert len(instr.check_errors()) == 0
        assert instr.auto_input_impedance_enabled == True
        instr.auto_input_impedance_enabled = False
        assert len(instr.check_errors()) == 0
        assert instr.auto_input_impedance_enabled == False

    def test_terminals_used(self, make_resetted_instr):
        instr = make_resetted_instr
        assert instr.terminals_used in ["FRONT", "REAR"]
        assert len(instr.check_errors()) == 0
