cmake_minimum_required(VERSION 3.5)
project(ydAPI)
set(EXECUTABLE_OUTPUT_PATH ../build)
include_directories(./include)
include_directories(./example)

add_library(example1 ./example/Example1.cpp)
add_library(example2 ./example/Example2.cpp)
add_library(example3 ./example/Example3.cpp)
add_library(example4 ./example/Example4.cpp)
add_library(example5 ./example/Example5.cpp)
add_library(example6 ./example/Example6.cpp)
add_library(example7 ./example/Example7.cpp)
add_library(example8 ./example/Example8.cpp)

add_executable(test ./example/ydExample.cpp)
target_link_libraries(
    test 
    example1
    example2
    example3
    example4
    example5
    example6
    example7
    example8
    /home/du/桌面/ydClient_1_108_36_33/ydAPI/linux64/libyd.so
)