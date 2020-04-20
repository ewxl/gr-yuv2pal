#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: elof
# GNU Radio version: 3.8.1.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import eng_notation
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio.qtgui import Range, RangeWidget
import configparser as ConfigParser
import soapy
import yuv2pal

from gnuradio import qtgui

class pal_fm_tx(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "pal_fm_tx")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self._vc_sens_config = ConfigParser.ConfigParser()
        self._vc_sens_config.read('settings_pal')
        try: vc_sens = self._vc_sens_config.getfloat("main", "fmgain")
        except: vc_sens = 1
        self.vc_sens = vc_sens
        self._vc_rf_config = ConfigParser.ConfigParser()
        self._vc_rf_config.read('settings_pal')
        try: vc_rf = self._vc_rf_config.getint("main", "rf")
        except: vc_rf = 1
        self.vc_rf = vc_rf
        self._vc_if_config = ConfigParser.ConfigParser()
        self._vc_if_config.read('settings_pal')
        try: vc_if = self._vc_if_config.getint("main", "if")
        except: vc_if = 0
        self.vc_if = vc_if
        self._vc_fc_config = ConfigParser.ConfigParser()
        self._vc_fc_config.read('settings_pal')
        try: vc_fc = self._vc_fc_config.getfloat("main", "fc")
        except: vc_fc = 5800e6
        self.vc_fc = vc_fc
        self.sens = sens = vc_sens
        self.rf_gain = rf_gain = vc_rf
        self.if_gain = if_gain = vc_if
        self.fc = fc = vc_fc

        ##################################################
        # Blocks
        ##################################################
        self._sens_tool_bar = Qt.QToolBar(self)
        self._sens_tool_bar.addWidget(Qt.QLabel('Sensitivity' + ": "))
        self._sens_line_edit = Qt.QLineEdit(str(self.sens))
        self._sens_tool_bar.addWidget(self._sens_line_edit)
        self._sens_line_edit.returnPressed.connect(
            lambda: self.set_sens(eng_notation.str_to_num(str(self._sens_line_edit.text()))))
        self.top_grid_layout.addWidget(self._sens_tool_bar)
        self._if_gain_range = Range(0, 47, 1, vc_if, 200)
        self._if_gain_win = RangeWidget(self._if_gain_range, self.set_if_gain, 'IF Gain', "counter_slider", int)
        self.top_grid_layout.addWidget(self._if_gain_win)
        self._fc_tool_bar = Qt.QToolBar(self)
        self._fc_tool_bar.addWidget(Qt.QLabel('Fc' + ": "))
        self._fc_line_edit = Qt.QLineEdit(str(self.fc))
        self._fc_tool_bar.addWidget(self._fc_line_edit)
        self._fc_line_edit.returnPressed.connect(
            lambda: self.set_fc(eng_notation.str_to_num(str(self._fc_line_edit.text()))))
        self.top_grid_layout.addWidget(self._fc_tool_bar)
        self.yuv_to_576i_0 = yuv2pal.yuv_to_576i(
            height=576,
            width=720,
        )
        self.yuv576i2pal_0 = yuv2pal.yuv576i2pal()
        self.soapy_sink_0 = None
        if "hackrf" == 'custom':
            dev = 'driver=uhd'
        else:
            dev = 'driver=' + "hackrf"

        self.soapy_sink_0 = soapy.sink(1, dev, '', 20e6, "fc32", '')

        self.soapy_sink_0.set_gain_mode(0,False)
        self.soapy_sink_0.set_gain_mode(1,False)

        self.soapy_sink_0.set_frequency(0, fc)
        self.soapy_sink_0.set_frequency(1, 100.0e6)

        # Made antenna sanity check more generic
        antList = self.soapy_sink_0.listAntennas(0)

        if len(antList) > 1:
            # If we have more than 1 possible antenna
            if len("TX/RX") == 0 or "TX/RX" not in antList:
                print("ERROR: Please define ant0 to an allowed antenna name.")
                strAntList = str(antList).lstrip('(').rstrip(')').rstrip(',')
                print("Allowed antennas: " + strAntList)
                exit(0)

            self.soapy_sink_0.set_antenna(0,"TX/RX")

        if 1 > 1:
            antList = self.soapy_sink_0.listAntennas(1)
            # If we have more than 1 possible antenna
            if len(antList) > 1:
                if len('TX') == 0 or 'TX' not in antList:
                    print("ERROR: Please define ant1 to an allowed antenna name.")
                    strAntList = str(antList).lstrip('(').rstrip(')').rstrip(',')
                    print("Allowed antennas: " + strAntList)
                    exit(0)

                self.soapy_sink_0.set_antenna(1,'TX')

        # Setup IQ Balance
        if "hackrf" != 'uhd':
            if (self.soapy_sink_0.IQ_balance_support(0)):
                self.soapy_sink_0.set_iq_balance(0,0)

            if (self.soapy_sink_0.IQ_balance_support(1)):
                self.soapy_sink_0.set_iq_balance(1,0)

        # Setup Frequency correction
        if (self.soapy_sink_0.freq_correction_support(0)):
            self.soapy_sink_0.set_frequency_correction(0,0)

        if (self.soapy_sink_0.freq_correction_support(1)):
            self.soapy_sink_0.set_frequency_correction(1,0)

        if "hackrf" == 'sidekiq' or "True" == 'False':
            self.soapy_sink_0.set_gain(0,10)
            self.soapy_sink_0.set_gain(1,0)
        else:
            if "hackrf" == 'bladerf':
                 self.soapy_sink_0.set_gain(0,"txvga1", -35)
                 self.soapy_sink_0.set_gain(0,"txvga2", 0)
            elif "hackrf" == 'uhd':
                self.soapy_sink_0.set_gain(0,"PGA", 24)
                self.soapy_sink_0.set_gain(1,"PGA", 0)
            else:
                 self.soapy_sink_0.set_gain(0,"PGA", 24)
                 self.soapy_sink_0.set_gain(1,"PGA", 0)
                 self.soapy_sink_0.set_gain(0,"PAD", 0)
                 self.soapy_sink_0.set_gain(1,"PAD", 0)
                 self.soapy_sink_0.set_gain(0,"IAMP", 0)
                 self.soapy_sink_0.set_gain(1,"IAMP", 0)
                 self.soapy_sink_0.set_gain(0,"txvga1", -35)
                 self.soapy_sink_0.set_gain(0,"txvga2", 0)
                 # Only hackrf uses VGA name, so just ch0
                 self.soapy_sink_0.set_gain(0,"VGA", if_gain)
        _rf_gain_check_box = Qt.QCheckBox('RF Gain')
        self._rf_gain_choices = {True: 1, False: 0}
        self._rf_gain_choices_inv = dict((v,k) for k,v in self._rf_gain_choices.items())
        self._rf_gain_callback = lambda i: Qt.QMetaObject.invokeMethod(_rf_gain_check_box, "setChecked", Qt.Q_ARG("bool", self._rf_gain_choices_inv[i]))
        self._rf_gain_callback(self.rf_gain)
        _rf_gain_check_box.stateChanged.connect(lambda i: self.set_rf_gain(self._rf_gain_choices[bool(i)]))
        self.top_grid_layout.addWidget(_rf_gain_check_box)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=5,
                decimation=4,
                taps=None,
                fractional_bw=None)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            1280*2, #size
            20e6, #samp_rate
            "", #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-.4, 0.8)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.blocks_uchar_to_float_0 = blocks.uchar_to_float()
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(2**-8)
        self.blocks_file_descriptor_source_0 = blocks.file_descriptor_source(gr.sizeof_char*1, 0, False)
        self.blocks_char_to_float_1 = blocks.char_to_float(1, 2**8)
        self.blocks_char_to_float_0 = blocks.char_to_float(1, 2**8)
        self.analog_frequency_modulator_fc_0 = analog.frequency_modulator_fc(sens)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_frequency_modulator_fc_0, 0), (self.soapy_sink_0, 0))
        self.connect((self.blocks_char_to_float_0, 0), (self.yuv576i2pal_0, 1))
        self.connect((self.blocks_char_to_float_1, 0), (self.yuv576i2pal_0, 2))
        self.connect((self.blocks_file_descriptor_source_0, 0), (self.yuv_to_576i_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.yuv576i2pal_0, 0))
        self.connect((self.blocks_uchar_to_float_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.analog_frequency_modulator_fc_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.yuv576i2pal_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.yuv_to_576i_0, 1), (self.blocks_char_to_float_0, 0))
        self.connect((self.yuv_to_576i_0, 2), (self.blocks_char_to_float_1, 0))
        self.connect((self.yuv_to_576i_0, 0), (self.blocks_uchar_to_float_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "pal_fm_tx")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_vc_sens(self):
        return self.vc_sens

    def set_vc_sens(self, vc_sens):
        self.vc_sens = vc_sens
        self.set_sens(self.vc_sens)

    def get_vc_rf(self):
        return self.vc_rf

    def set_vc_rf(self, vc_rf):
        self.vc_rf = vc_rf
        self.set_rf_gain(self.vc_rf)

    def get_vc_if(self):
        return self.vc_if

    def set_vc_if(self, vc_if):
        self.vc_if = vc_if
        self.set_if_gain(self.vc_if)

    def get_vc_fc(self):
        return self.vc_fc

    def set_vc_fc(self, vc_fc):
        self.vc_fc = vc_fc
        self.set_fc(self.vc_fc)

    def get_sens(self):
        return self.sens

    def set_sens(self, sens):
        self.sens = sens
        Qt.QMetaObject.invokeMethod(self._sens_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.sens)))
        self._vc_sens_config = ConfigParser.ConfigParser()
        self._vc_sens_config.read('settings_pal')
        if not self._vc_sens_config.has_section("main"):
        	self._vc_sens_config.add_section("main")
        self._vc_sens_config.set("main", "fmgain", str(self.sens))
        self._vc_sens_config.write(open('settings_pal', 'w'))
        self.analog_frequency_modulator_fc_0.set_sensitivity(self.sens)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self._rf_gain_callback(self.rf_gain)
        self._vc_rf_config = ConfigParser.ConfigParser()
        self._vc_rf_config.read('settings_pal')
        if not self._vc_rf_config.has_section("main"):
        	self._vc_rf_config.add_section("main")
        self._vc_rf_config.set("main", "rf", str(self.rf_gain))
        self._vc_rf_config.write(open('settings_pal', 'w'))
        self.soapy_sink_0.set_gain(0,"AMP", self.rf_gain)

    def get_if_gain(self):
        return self.if_gain

    def set_if_gain(self, if_gain):
        self.if_gain = if_gain
        self._vc_if_config = ConfigParser.ConfigParser()
        self._vc_if_config.read('settings_pal')
        if not self._vc_if_config.has_section("main"):
        	self._vc_if_config.add_section("main")
        self._vc_if_config.set("main", "if", str(self.if_gain))
        self._vc_if_config.write(open('settings_pal', 'w'))
        self.soapy_sink_0.set_gain(0,"VGA", self.if_gain)

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc
        Qt.QMetaObject.invokeMethod(self._fc_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.fc)))
        self._vc_fc_config = ConfigParser.ConfigParser()
        self._vc_fc_config.read('settings_pal')
        if not self._vc_fc_config.has_section("main"):
        	self._vc_fc_config.add_section("main")
        self._vc_fc_config.set("main", "fc", str(self.fc))
        self._vc_fc_config.write(open('settings_pal', 'w'))
        self.soapy_sink_0.set_frequency(0, self.fc)





def main(top_block_cls=pal_fm_tx, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
