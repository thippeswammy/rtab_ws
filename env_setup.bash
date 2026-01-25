#!/bin/bash
# RTAB-Map + LibTorch Environment Setup

# 1. Export LibTorch to LD_LIBRARY_PATH (Needed for rtabmap to find system libs)
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/media/thippe/SDV/Ubuntu/rtab_ws/libtorch_cxx11/libtorch/lib

# 2. Source the workspace
if [ -f "install/setup.bash" ]; then
    source install/setup.bash
    echo "✅ RTAB-Map workspace sourced with LibTorch paths."
else
    echo "⚠️  install/setup.bash not found. Did you run 'colcon build' yet?"
fi
