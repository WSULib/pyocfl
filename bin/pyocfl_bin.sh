#!/bin/bash

# requires being run with . in current shell, e.g.
# . bin/pyocfl_bin.sh test_data/test_fe89db792da94587a190b2677984fde0/sr_bac0c73b10654e4bad1a5e7cda3d149e/ raw_obj1
cd $(python pyocfl_bin.py cd $2 -sr $1)