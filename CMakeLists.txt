cmake_minimum_required(VERSION 3.16)
project(colombia_development LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(colombia_core INTERFACE)
target_include_directories(colombia_core INTERFACE shared/cpp/include/colombia)

add_executable(territorial_risk programs/01-territorial-development/cpp/apps/territorial_risk.cpp)
target_include_directories(territorial_risk PRIVATE programs/01-territorial-development/cpp/include)
target_link_libraries(territorial_risk PRIVATE colombia_core)

add_executable(fraud_risk programs/02-fraud-identity/cpp/apps/fraud_risk.cpp)
target_include_directories(fraud_risk PRIVATE programs/02-fraud-identity/cpp/include)
target_link_libraries(fraud_risk PRIVATE colombia_core)

enable_testing()
add_executable(core_tests shared/cpp/tests/test_core.cpp)
target_include_directories(core_tests PRIVATE
  programs/01-territorial-development/cpp/include
  programs/02-fraud-identity/cpp/include
)
target_link_libraries(core_tests PRIVATE colombia_core)
add_test(NAME core_tests COMMAND core_tests)
