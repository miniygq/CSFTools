"""
Beare earth extraction
Author: Jianbo Qi
Date: 2017-1-15
"""
import argparse
import laspy
import CSF
import numpy as np
import time

if __name__ == "__main__":
    parse = argparse.ArgumentParser()
    parse.add_argument("-i", help="Input las file.", required=True)
    parse.add_argument("-cloth_resolution", type=float, help="Cloth simulation grid resolution.",default=0.5)
    parse.add_argument("-bSlopeSmooth", type=bool, help="Handle steep slope after simulation.",default=True)
    parse.add_argument("-rigidness", type=int, help="Rigidness of cloth.", default=1)
    parse.add_argument("-classify_threshold", type=float,
                       help="Distance used to classify point into ground and non-ground.",default=0.5)
    parse.add_argument("-o", help="Output las file of ground points.", required=True)
    parse.add_argument("-save_mode", help="Save only the ground part of the whole cloud: ground, non_ground, all",
                       default="all")
    args = parse.parse_args()

    input_las_file = args.i
    output_las_file = args.o


    # python 3.9 不在使用此方法，perf_counter（）代替 clock（）
    # start = time.clock()
    start = time.perf_counter()

    csf = CSF.CSF()
    if args.cloth_resolution is not None:
        csf.params.cloth_resolution = args.cloth_resolution
    if args.bSlopeSmooth is not None:
        csf.params.bSlopeSmooth = args.bSlopeSmooth
    if args.rigidness is not None:
        csf.params.rigidness = args.rigidness
    if args.classify_threshold is not None:
        csf.params.class_threshold = args.classify_threshold

    input_File = laspy.read(input_las_file)
    xyz = np.vstack((input_File.x, input_File.y, input_File.z)).transpose()
    csf.setPointCloud(xyz)
    ground = CSF.VecInt()
    non_ground = CSF.VecInt()
    csf.do_filtering(ground, non_ground)
    points = input_File.points
    out_File = laspy.LasData(input_File.header)
    if args.save_mode == "ground": # save ground part
        classification = [1 for i in range(0, len(points))]  
        # 2 for ground
        for i in range(0, len(ground)):
            classification[ground[i]] = 2
        out_File.classification = classification
        out_File.points = points[out_File.classification  == 2]

    if args.save_mode == "non_ground":
        # non_ground_points = points[non_ground]
        # out_File.points = non_ground_points
        # classification = [1 for i in range(0, len(non_ground))]  # 1 for non-ground
        # out_File.classification = classification

        # 1 for non_ground
        classification = [1 for i in range(0, len(points))]  
        for i in range(0, len(ground)):
            classification[ground[i]] = 2
        for i in range(0, len(non_ground)):
            classification[non_ground[i]] = 1
        out_File.classification = classification
        out_File.points = points[out_File.classification == 1]

    if args.save_mode == "all":
        out_File.points = points
        classification = [1 for i in range(0, len(points))]  # 1 for non-ground
        for i in range(0, len(ground)):
            classification[ground[i]] = 2
        for i in range(0, len(non_ground)):
            classification[non_ground[i]] = 1
        out_File.classification = classification

    out_File.write(output_las_file)

    end = time.perf_counter()
    print("Done.")
    print("Time: ", "%.3fs" % (end - start))