"""
This file is part of the Fourier-Bessel Partile-In-Cell code (FB-PIC)
It allows the use of the MKL library for FFT.
"""
# Note: this code is partially inspired by https://github.com/LCAV/mkl_fft
# For this reason, the corresponding copyright is reproduced here:

# Copyright (c) 2016 Ivan Dokmanic, Robin Scheibler
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

import sys
import ctypes
import numpy as np

# Load the MKL Library for the current plateform
if sys.platform == 'linux':
    mkl = ctypes.CDLL('libmkl_rt.so')
elif sys.platform == 'darwin':
    mkl = ctypes.CDLL('libmkl_rt.dylib')
elif sys.platform == 'win32':
    mkl = ctypes.CDLL('libmkl_rt.dll')

# Define a set of flags that are passed to the MKL library
# The values of these flags are copied from mkl_dfti.h
DFTI_PRECISION              = ctypes.c_int(3)
DFTI_BACKWARD_SCALE         = ctypes.c_int(5)
DFTI_NUMBER_OF_TRANSFORMS   = ctypes.c_int(7)
DFTI_PLACEMENT              = ctypes.c_int(11)
DFTI_INPUT_STRIDES          = ctypes.c_int(12)
DFTI_OUTPUT_STRIDES         = ctypes.c_int(13)
DFTI_INPUT_DISTANCE         = ctypes.c_int(14)
DFTI_OUTPUT_DISTANCE        = ctypes.c_int(15)
DFTI_COMPLEX                = ctypes.c_int(32)
DFTI_SINGLE                 = ctypes.c_int(35)
DFTI_DOUBLE                 = ctypes.c_int(36)
DFTI_NOT_INPLACE            = ctypes.c_int(44)


class MKLFFT( object ):
    """
    TODO
    """

    def __init__( self, a ):
        """
        TODO
        """

        # Perform a few checks on the array type and shape
        assert a.ndim == 2
        assert a.dtype == np.complex128
        self.shape = a.shape

        # Prepare the descriptor for the FFT:
        # from complex128 to complex128, along the axis 0 of a 2D array
        descriptor = ctypes.c_void_p(0)
        length = ctypes.c_int(a.shape[0])
        ifft_scale = ctypes.c_double( 1. / a.shape[0] )
        n_transforms = ctypes.c_int(a.shape[1])
        distance = ctypes.c_int(a.strides[1] // a.itemsize)
        # For strides, the C type used *must* be long
        strides = (ctypes.c_long*2)(0, a.strides[0] // a.itemsize)
        mkl.DftiCreateDescriptor( ctypes.byref(descriptor),
            DFTI_DOUBLE, DFTI_COMPLEX, ctypes.c_int(1), length)
        mkl.DftiSetValue(descriptor, DFTI_NUMBER_OF_TRANSFORMS, n_transforms)
        mkl.DftiSetValue(descriptor, DFTI_INPUT_DISTANCE, distance)
        mkl.DftiSetValue(descriptor, DFTI_OUTPUT_DISTANCE, distance)
        mkl.DftiSetValue(descriptor, DFTI_INPUT_STRIDES, ctypes.byref(strides))
        mkl.DftiSetValue(descriptor, DFTI_OUTPUT_STRIDES, ctypes.byref(strides))
        mkl.DftiSetValue(descriptor, DFTI_PLACEMENT, DFTI_NOT_INPLACE)
        mkl.DftiSetValue(descriptor, DFTI_BACKWARD_SCALE, ifft_scale)
        mkl.DftiCommitDescriptor(descriptor)
        self.descriptor = descriptor

    def transform( self, array_in, array_out ):
        """
        TODO
        """
        # Perform a few checks
        assert array_in.shape == self.shape
        assert array_in.dtype == np.complex128
        assert array_out.shape == self.shape
        assert array_out.dtype == np.complex128

        # Compute the FFT
        mkl.DftiComputeForward( self.descriptor,
            array_in.ctypes.data_as( ctypes.c_void_p ),
            array_out.ctypes.data_as( ctypes.c_void_p ) )

    def inverse_transform( self, array_in, array_out ):
        """
        TODO
        """
        # Perform a few checks
        assert array_in.shape == self.shape
        assert array_in.dtype == np.complex128
        assert array_out.shape == self.shape
        assert array_out.dtype == np.complex128

        # Compute the FFT
        mkl.DftiComputeBackward( self.descriptor,
            array_in.ctypes.data_as( ctypes.c_void_p ),
            array_out.ctypes.data_as( ctypes.c_void_p ) )

    def __del__( self ):
        """
        TODO
        """
        mkl.DftiFreeDescriptor( ctypes.byref(self.descriptor) )
