#!/bin/bash

for fname in input/*;
do
    echo "Inference mesh ($fname) ..."
    python -m lrm.inferrer --model_name openlrm-base-obj-1.0 --source_image "$fname" --export_mesh
    echo "Inference video ($fname) ..."
    python -m lrm.inferrer --model_name openlrm-base-obj-1.0 --source_image "$fname" --export_video
done
