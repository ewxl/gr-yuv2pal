INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_YUV2PAL yuv2pal)

FIND_PATH(
    YUV2PAL_INCLUDE_DIRS
    NAMES yuv2pal/api.h
    HINTS $ENV{YUV2PAL_DIR}/include
        ${PC_YUV2PAL_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    YUV2PAL_LIBRARIES
    NAMES gnuradio-yuv2pal
    HINTS $ENV{YUV2PAL_DIR}/lib
        ${PC_YUV2PAL_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/yuv2palTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(YUV2PAL DEFAULT_MSG YUV2PAL_LIBRARIES YUV2PAL_INCLUDE_DIRS)
MARK_AS_ADVANCED(YUV2PAL_LIBRARIES YUV2PAL_INCLUDE_DIRS)
