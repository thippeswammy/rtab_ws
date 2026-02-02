cmake_minimum_required(VERSION 3.8)
project(rtabmap_bringup)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-exist -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/velodyne_filter.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME velodyne_filter
)

ament_package()
