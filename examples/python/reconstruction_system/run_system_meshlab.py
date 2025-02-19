# ----------------------------------------------------------------------------
# -                        Open3D: www.open3d.org                            -
# ----------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2018-2021 www.open3d.org
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# ----------------------------------------------------------------------------

# examples/python/reconstruction_system/run_system_meshlab.py

import argparse
import datetime
import json
import sys
import time
from os.path import join
from initialize_config import initialize_config

sys.path.append("../utility")
from file import check_folder_structure

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reconstruction system")
    parser.add_argument("config", help="path to the config file")
    parser.add_argument("--make",
                        help="Step 1) make fragments from RGBD sequence.",
                        action="store_true")
    parser.add_argument(
        "--register",
        help="Step 2) register all fragments to detect loop closure.",
        action="store_true")
    parser.add_argument("--refine",
                        help="Step 3) refine rough registrations",
                        action="store_true")
    parser.add_argument(
        "--integrate",
        help="Step 4) integrate the whole RGBD sequence to make final mesh.",
        action="store_true")
    parser.add_argument(
        "--slac",
        help="Step 5) (optional) run slac optimization for fragments.",
        action="store_true")
    parser.add_argument(
        "--slac_integrate",
        help="Step 6) (optional) integrate fragements using slac to make final "
             "pointcloud / mesh.",
        action="store_true")
    parser.add_argument("--debug_mode",
                        help="turn on debug mode.",
                        action="store_true")
    parser.add_argument(
        '--device',
        help="(optional) select processing device for slac and slac_integrate. "
             "[example: cpu:0, cuda:0].",
        type=str,
        default='cpu:0')
    parser.add_argument(
        "--planar_section",
        nargs=2,
        metavar=("real_height", "n_planes"),
        help="""align, clean and compute planar section using Meshlab. 
        Inputs: real person height (cm), number of cross planes.""",
    )

    args = parser.parse_args()

    if not args.make and \
            not args.register and \
            not args.refine and \
            not args.integrate and \
            not args.slac and \
            not args.slac_integrate and \
            not args.planar_section:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # check folder structure
    if args.config is not None:
        with open(args.config) as json_file:
            config = json.load(json_file)
            initialize_config(config)
            check_folder_structure(config["path_dataset"])
    assert config is not None

    if args.debug_mode:
        config['debug_mode'] = True
    else:
        config['debug_mode'] = False

    config['device'] = args.device

    print("====================================")
    print("Configuration")
    print("====================================")
    for key, val in config.items():
        print("%40s : %s" % (key, str(val)))

    times = [0, 0, 0, 0, 0, 0, 0]
    if args.make:
        start_time = time.time()
        import make_fragments

        make_fragments.run(config)
        times[0] = time.time() - start_time
    if args.register:
        start_time = time.time()
        import register_fragments

        register_fragments.run(config)
        times[1] = time.time() - start_time
    if args.refine:
        start_time = time.time()
        import refine_registration

        refine_registration.run(config)
        times[2] = time.time() - start_time
    if args.integrate:
        start_time = time.time()
        import integrate_scene

        integrate_scene.run(config)
        times[3] = time.time() - start_time
    if args.slac:
        start_time = time.time()
        import slac

        slac.run(config)
        times[4] = time.time() - start_time
    if args.slac_integrate:
        start_time = time.time()
        import slac_integrate

        slac_integrate.run(config)
        times[5] = time.time() - start_time
    if args.planar_section:
        start_time = time.time()
        from meshlab_filters import *

        real_height, n_planes = args.planar_section
        ms = load_mesh(config)
        align_and_center(ms)
        clean(ms)
        planar_section(ms, float(real_height), int(n_planes), planeaxis='Z Axis')
        save_mesh(config, ms)
        times[6] = time.time() - start_time

    print("====================================")
    print("Elapsed time (in h:m:s)")
    print("====================================")
    print("- Making fragments       %s" % datetime.timedelta(seconds=times[0]))
    print("- Register fragments     %s" % datetime.timedelta(seconds=times[1]))
    print("- Refine registration    %s" % datetime.timedelta(seconds=times[2]))
    print("- Integrate frames       %s" % datetime.timedelta(seconds=times[3]))
    print("- SLAC                   %s" % datetime.timedelta(seconds=times[4]))
    print("- SLAC Integrate         %s" % datetime.timedelta(seconds=times[5]))
    print("- Compute planar section %s" % datetime.timedelta(seconds=times[6]))
    print("- Total                  %s" % datetime.timedelta(seconds=sum(times)))
    print("Aligned mesh and planar sections saved to: "
          "%s" % join(config["path_dataset"], "scene/"))

    sys.stdout.flush()
