cmake_minimum_required(VERSION 3.15...3.30)
project(${SKBUILD_PROJECT_NAME} VERSION ${SKBUILD_PROJECT_VERSION} LANGUAGES C)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

# Platform detection for SunVox library
if(APPLE)
    if(CMAKE_SYSTEM_PROCESSOR STREQUAL "arm64")
        set(SUNVOX_LIB_DIR "${CMAKE_SOURCE_DIR}/sunvox_lib/macos/lib_arm64")
    else()
        set(SUNVOX_LIB_DIR "${CMAKE_SOURCE_DIR}/sunvox_lib/macos/lib_x86_64")
    endif()
    set(SUNVOX_LIB_NAME "sunvox.dylib")
    set(SUNVOX_LIB "${SUNVOX_LIB_DIR}/${SUNVOX_LIB_NAME}")
elseif(UNIX)
    if(CMAKE_SYSTEM_PROCESSOR STREQUAL "aarch64" OR CMAKE_SYSTEM_PROCESSOR STREQUAL "arm64")
        set(SUNVOX_LIB_DIR "${CMAKE_SOURCE_DIR}/sunvox_lib/linux/lib_arm64")
    elseif(CMAKE_SYSTEM_PROCESSOR STREQUAL "x86_64" OR CMAKE_SYSTEM_PROCESSOR STREQUAL "AMD64")
        set(SUNVOX_LIB_DIR "${CMAKE_SOURCE_DIR}/sunvox_lib/linux/lib_x86_64")
    else()
        set(SUNVOX_LIB_DIR "${CMAKE_SOURCE_DIR}/sunvox_lib/linux/lib_x86")
    endif()
    set(SUNVOX_LIB_NAME "sunvox.so")
    set(SUNVOX_LIB "${SUNVOX_LIB_DIR}/${SUNVOX_LIB_NAME}")
elseif(WIN32)
    set(SUNVOX_LIB_DIR "${CMAKE_SOURCE_DIR}/sunvox_lib/windows")
    set(SUNVOX_LIB_NAME "sunvox.dll")
    set(SUNVOX_LIB "${SUNVOX_LIB_DIR}/${SUNVOX_LIB_NAME}")
endif()

set(SUNVOX_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/sunvox_lib/headers")

message(STATUS "SunVox library: ${SUNVOX_LIB}")
message(STATUS "SunVox include: ${SUNVOX_INCLUDE_DIR}")

# Cython compilation
add_custom_command(
    OUTPUT _core.c
    COMMAND Python::Interpreter -m cython
        "${CMAKE_CURRENT_SOURCE_DIR}/src/pysunvox/_core.pyx" --output-file _core.c
    DEPENDS src/pysunvox/_core.pyx src/pysunvox/_sunvox.pxd
)

# Build the extension module
python_add_library(_core MODULE _core.c WITH_SOABI)

# Add include directories
target_include_directories(_core PRIVATE ${SUNVOX_INCLUDE_DIR})

# Define SUNVOX_STATIC_LIB to get direct function declarations
target_compile_definitions(_core PRIVATE SUNVOX_STATIC_LIB)

# Link against the SunVox library
target_link_libraries(_core PRIVATE ${SUNVOX_LIB})

# Set RPATH for finding the library at runtime
if(APPLE)
    set_target_properties(_core PROPERTIES
        INSTALL_RPATH "@loader_path"
        BUILD_WITH_INSTALL_RPATH TRUE
    )
elseif(UNIX)
    set_target_properties(_core PROPERTIES
        INSTALL_RPATH "$ORIGIN"
        BUILD_WITH_INSTALL_RPATH TRUE
    )
endif()

# Install the extension module
install(TARGETS _core DESTINATION pysunvox)

# Install the SunVox library alongside the extension
install(FILES ${SUNVOX_LIB} DESTINATION pysunvox)

# Fix the library reference on macOS (the sunvox.dylib install name is just "sunvox.dylib"
# without any path, so we need to change it to use @loader_path)
if(APPLE)
    install(CODE "
        execute_process(
            COMMAND install_name_tool -change sunvox.dylib @loader_path/sunvox.dylib
                    \"\${CMAKE_INSTALL_PREFIX}/pysunvox/$<TARGET_FILE_NAME:_core>\"
        )
    ")
endif()
