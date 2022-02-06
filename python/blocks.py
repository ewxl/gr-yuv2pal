import numpy as np
import sys
import signal
import os

from gnuradio import gr
from gnuradio import blocks
from gnuradio.filter import firdes
from gnuradio.fft import window

from codecs import decode
from gnuradio import analog
from gnuradio import filter

class interleaver625(gr.sync_block): 

    def __init__(self):  
        gr.sync_block.__init__(
            self,
            name='interleaver', 
            in_sig=[np.dtype("643072B")],
            out_sig=[np.dtype("643072B")]
        )
    def work(self, input_items, output_items):
        for i,frame in enumerate(input_items[0]):
            frame = frame.reshape(628,1024)
            out = output_items[0][i].reshape(628,1024)
            out[:] = 0
            out[:625//2] = frame[:624:2]
            out[625//2+1:625] = frame[1:624:2]
        return len(output_items[0])
# -*- coding: utf-8 -*-


class line720_1024interleaved(gr.hier_block2):
    def __init__(self):
        gr.hier_block2.__init__(
            self, "720 to 1024 interleaved",
                gr.io_signature(1, 1, gr.sizeof_char*1),
                gr.io_signature(1, 1, gr.sizeof_char*1),
        )

        ##################################################
        # Blocks
        ##################################################
        self.interleaver625 = interleaver625()
        self.blocks_vector_to_stream_1 = blocks.vector_to_stream(gr.sizeof_char*1024, 628)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_char*1, 1024)
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_char*1024, 628)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_char*1, 1024)
        self.blocks_stream_mux_0_0 = blocks.stream_mux(gr.sizeof_char*1024, [576,26*2])
        self.blocks_stream_mux_0 = blocks.stream_mux(gr.sizeof_char*1, [242,720,62])
        self.blocks_skiphead_0 = blocks.skiphead(gr.sizeof_char*1, 600*1024)
        self.blocks_null_source_0_1 = blocks.null_source(gr.sizeof_char*1024)
        self.blocks_null_source_0_0 = blocks.null_source(gr.sizeof_char*1)
        self.blocks_null_source_0 = blocks.null_source(gr.sizeof_char*1)
        self.blocks_keep_m_in_n_1 = blocks.keep_m_in_n(gr.sizeof_char, 625*1024, 628*1024, 0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_keep_m_in_n_1, 0), (self.blocks_skiphead_0, 0))
        self.connect((self.blocks_null_source_0, 0), (self.blocks_stream_mux_0, 2))
        self.connect((self.blocks_null_source_0_0, 0), (self.blocks_stream_mux_0, 0))
        self.connect((self.blocks_null_source_0_1, 0), (self.blocks_stream_mux_0_0, 1))
        self.connect((self.blocks_skiphead_0, 0), (self, 0))
        self.connect((self.blocks_stream_mux_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_stream_mux_0_0, 0), (self.blocks_stream_to_vector_1, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.blocks_stream_mux_0_0, 0))
        self.connect((self.blocks_stream_to_vector_1, 0), (self.interleaver625, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_keep_m_in_n_1, 0))
        self.connect((self.blocks_vector_to_stream_1, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.interleaver625, 0), (self.blocks_vector_to_stream_1, 0))
        self.connect((self, 0), (self.blocks_stream_mux_0, 1))



class uv_fix(gr.sync_block): 
    def __init__(self,):  
        gr.sync_block.__init__(
            self,
            name='uv fix', 
            in_sig=[np.uint8],
            out_sig=[np.int8]
        )

    def work(self, input_items, output_items):
        output_items[0][:] = input_items[0]-128
        return len(output_items[0])
# -*- coding: utf-8 -*-

class yuv576i2pal(gr.hier_block2):
    def __init__(self):
        gr.hier_block2.__init__(
            self, "YUV 576i to PAL",
                gr.io_signaturev(3, 3, [gr.sizeof_float*1, gr.sizeof_float*1, gr.sizeof_float*1]),
                gr.io_signature(1, 1, gr.sizeof_float*1),
        )

        ##################################################
        # Variables
        ##################################################
        self.sync = sync = b'eJzt0SEOACAMBMH+/9MFh8BRUdLM+WUCZL4v9gr5mD4K05+37Bifz+fz+Xw+n8/n8/l8Pp/P5/P5\nfD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8\nPp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+RNX\nvbv+ffo//q+7r57B5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5\nfD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD6fz+fz+Xw+n8/n8/l8\nPp/P5/P5fD6fz+fz+Xw+n8/n8/l8Pp/P5/P5fD7/9vV9/QJF65uM\n'
        self.pal_fc = pal_fc = 4433618.75

        ##################################################
        # Blocks
        ##################################################
        self.low_pass_filter_0 = filter.fir_filter_fff(
            1,
            firdes.low_pass(
                1,
                16e6,
                5.5e6,
                16e6*0.03,
                window.WIN_HAMMING,
                6.76))
        self.blocks_vector_source_x_0 = blocks.vector_source_f(np.unpackbits(np.fromstring(decode(decode(sync,"base64"),"zip"),np.uint8)), True, 1, [])
        self.blocks_stream_mux_1 = blocks.stream_mux(gr.sizeof_float*1, [12*16,(64-12)*16,12*16,(64-12)*16])
        self.blocks_stream_mux_0 = blocks.stream_mux(gr.sizeof_gr_complex*1, [6*16,36,(64-6)*16-36,6*16,36,(64-6)*16-36])
        self.blocks_multiply_xx_2 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_1 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vff(1)
        self.blocks_multiply_const_vxx_2 = blocks.multiply_const_cc(0.5)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_ff(-0.3)
        self.blocks_multiply_const_vxx_0_1 = blocks.multiply_const_ff(0.7)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(0.7)
        self.blocks_keep_m_in_n_1 = blocks.keep_m_in_n(gr.sizeof_float, 625*1024, 626*1024, 0)
        self.blocks_keep_m_in_n_0 = blocks.keep_m_in_n(gr.sizeof_gr_complex, 625*1024, 626*1024, 0)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.analog_sig_source_x_0_0 = analog.sig_source_c(16e6, analog.GR_SIN_WAVE, pal_fc, 1, 0, 0)
        self.analog_const_source_x_9 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 1)
        self.analog_const_source_x_8 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 0)
        self.analog_const_source_x_7 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, -1)
        self.analog_const_source_x_6 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 0)
        self.analog_const_source_x_5 = analog.sig_source_c(0, analog.GR_CONST_WAVE, 0, 0, 0)
        self.analog_const_source_x_4 = analog.sig_source_c(0, analog.GR_CONST_WAVE, 0, 0, 0.15*np.exp(-3/4*1j*np.pi))
        self.analog_const_source_x_3 = analog.sig_source_c(0, analog.GR_CONST_WAVE, 0, 0, 0)
        self.analog_const_source_x_2 = analog.sig_source_c(0, analog.GR_CONST_WAVE, 0, 0, 0)
        self.analog_const_source_x_1 = analog.sig_source_c(0, analog.GR_CONST_WAVE, 0, 0, 0.15*np.exp(3/4*1j*np.pi))
        self.analog_const_source_x_0 = analog.sig_source_c(0, analog.GR_CONST_WAVE, 0, 0, 0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_stream_mux_0, 0))
        self.connect((self.analog_const_source_x_1, 0), (self.blocks_stream_mux_0, 1))
        self.connect((self.analog_const_source_x_2, 0), (self.blocks_stream_mux_0, 2))
        self.connect((self.analog_const_source_x_3, 0), (self.blocks_stream_mux_0, 3))
        self.connect((self.analog_const_source_x_4, 0), (self.blocks_stream_mux_0, 4))
        self.connect((self.analog_const_source_x_5, 0), (self.blocks_stream_mux_0, 5))
        self.connect((self.analog_const_source_x_6, 0), (self.blocks_stream_mux_1, 0))
        self.connect((self.analog_const_source_x_7, 0), (self.blocks_stream_mux_1, 1))
        self.connect((self.analog_const_source_x_8, 0), (self.blocks_stream_mux_1, 2))
        self.connect((self.analog_const_source_x_9, 0), (self.blocks_stream_mux_1, 3))
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_multiply_const_vxx_2, 0))
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self.blocks_add_xx_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.blocks_complex_to_float_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_complex_to_float_0, 1), (self.blocks_multiply_xx_2, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.blocks_multiply_const_vxx_0_1, 0))
        self.connect((self.blocks_keep_m_in_n_0, 0), (self.blocks_multiply_xx_1, 0))
        self.connect((self.blocks_keep_m_in_n_1, 0), (self.blocks_multiply_xx_2, 2))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0_1, 0), (self.blocks_add_xx_0, 2))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_2, 0), (self.blocks_complex_to_float_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_add_xx_0, 3))
        self.connect((self.blocks_multiply_xx_1, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.blocks_multiply_xx_2, 0), (self.blocks_add_xx_0, 4))
        self.connect((self.blocks_stream_mux_0, 0), (self.blocks_keep_m_in_n_0, 0))
        self.connect((self.blocks_stream_mux_1, 0), (self.blocks_keep_m_in_n_1, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.low_pass_filter_0, 0), (self, 0))
        self.connect((self, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self, 1), (self.blocks_multiply_xx_0, 0))
        self.connect((self, 2), (self.blocks_multiply_xx_2, 1))


    def get_sync(self):
        return self.sync

    def set_sync(self, sync):
        self.sync = sync
        self.blocks_vector_source_x_0.set_data(np.unpackbits(np.fromstring(decode(decode(self.sync,"base64"),"zip"),np.uint8)), [])

    def get_pal_fc(self):
        return self.pal_fc

    def set_pal_fc(self, pal_fc):
        self.pal_fc = pal_fc
        self.analog_sig_source_x_0_0.set_frequency(self.pal_fc)


# -*- coding: utf-8 -*-
class yuv_to_576i(gr.hier_block2):
    def __init__(self, height=576, width=720):
        gr.hier_block2.__init__(
            self, "YUV420 to 576i (625)",
                gr.io_signature(1, 1, gr.sizeof_char*1),
                gr.io_signaturev(3, 3, [gr.sizeof_char*1, gr.sizeof_char*1, gr.sizeof_char*1]),
        )

        ##################################################
        # Parameters
        ##################################################
        self.height = height
        self.width = width

        ##################################################
        # Variables
        ##################################################
        self.y = y = width*height
        self.v = v = y//4
        self.u = u = y//4

        ##################################################
        # Blocks
        ##################################################
        self.uv_fix_1 = uv_fix()
        self.uv_fix_0 = uv_fix()
        self.line720_1024interleaved_2 = line720_1024interleaved()
        self.line720_1024interleaved_1 = line720_1024interleaved()
        self.line720_1024interleaved_0 = line720_1024interleaved()
        self.blocks_vector_to_stream_1 = blocks.vector_to_stream(gr.sizeof_char*1, 720)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_char*1, 720)
        self.blocks_stream_to_vector_0_0 = blocks.stream_to_vector(gr.sizeof_char*1, 720)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_char*1, 720)
        self.blocks_repeat_3 = blocks.repeat(gr.sizeof_char*720, 2)
        self.blocks_repeat_2 = blocks.repeat(gr.sizeof_char*720, 2)
        self.blocks_repeat_1 = blocks.repeat(gr.sizeof_char*1, 2)
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_char*1, 2)
        self.blocks_keep_m_in_n_2 = blocks.keep_m_in_n(gr.sizeof_char, v, y+u+v, y+u)
        self.blocks_keep_m_in_n_1 = blocks.keep_m_in_n(gr.sizeof_char, u, y+u+v, y)
        self.blocks_keep_m_in_n_0 = blocks.keep_m_in_n(gr.sizeof_char, y, y+u+v, 0)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_keep_m_in_n_0, 0), (self.line720_1024interleaved_0, 0))
        self.connect((self.blocks_keep_m_in_n_1, 0), (self.uv_fix_0, 0))
        self.connect((self.blocks_keep_m_in_n_2, 0), (self.uv_fix_1, 0))
        self.connect((self.blocks_repeat_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_repeat_1, 0), (self.blocks_stream_to_vector_0_0, 0))
        self.connect((self.blocks_repeat_2, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.blocks_repeat_3, 0), (self.blocks_vector_to_stream_1, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.blocks_repeat_2, 0))
        self.connect((self.blocks_stream_to_vector_0_0, 0), (self.blocks_repeat_3, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.line720_1024interleaved_1, 0))
        self.connect((self.blocks_vector_to_stream_1, 0), (self.line720_1024interleaved_2, 0))
        self.connect((self.line720_1024interleaved_0, 0), (self, 0))
        self.connect((self.line720_1024interleaved_1, 0), (self, 1))
        self.connect((self.line720_1024interleaved_2, 0), (self, 2))
        self.connect((self, 0), (self.blocks_keep_m_in_n_0, 0))
        self.connect((self, 0), (self.blocks_keep_m_in_n_1, 0))
        self.connect((self, 0), (self.blocks_keep_m_in_n_2, 0))
        self.connect((self.uv_fix_0, 0), (self.blocks_repeat_0, 0))
        self.connect((self.uv_fix_1, 0), (self.blocks_repeat_1, 0))


    def get_height(self):
        return self.height

    def set_height(self, height):
        self.height = height
        self.set_y(self.width*self.height)

    def get_width(self):
        return self.width

    def set_width(self, width):
        self.width = width
        self.set_y(self.width*self.height)

    def get_y(self):
        return self.y

    def set_y(self, y):
        self.y = y
        self.set_u(self.y//4)
        self.set_v(self.y//4)
        self.blocks_keep_m_in_n_0.set_m(self.y)
        self.blocks_keep_m_in_n_0.set_n(self.y+self.u+self.v)
        self.blocks_keep_m_in_n_1.set_offset(self.y)
        self.blocks_keep_m_in_n_1.set_n(self.y+self.u+self.v)
        self.blocks_keep_m_in_n_2.set_offset(self.y+self.u)
        self.blocks_keep_m_in_n_2.set_n(self.y+self.u+self.v)

    def get_v(self):
        return self.v

    def set_v(self, v):
        self.v = v
        self.blocks_keep_m_in_n_0.set_n(self.y+self.u+self.v)
        self.blocks_keep_m_in_n_1.set_n(self.y+self.u+self.v)
        self.blocks_keep_m_in_n_2.set_m(self.v)
        self.blocks_keep_m_in_n_2.set_n(self.y+self.u+self.v)

    def get_u(self):
        return self.u

    def set_u(self, u):
        self.u = u
        self.blocks_keep_m_in_n_0.set_n(self.y+self.u+self.v)
        self.blocks_keep_m_in_n_1.set_m(self.u)
        self.blocks_keep_m_in_n_1.set_n(self.y+self.u+self.v)
        self.blocks_keep_m_in_n_2.set_offset(self.y+self.u)
        self.blocks_keep_m_in_n_2.set_n(self.y+self.u+self.v)


