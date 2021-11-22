import sys
import json
import argparse
from os.path import join

sys.path.append("../utility")
from file import check_folder_structure

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute planar section using Meshlab.")
    parser.add_argument("config", help="path to the config file")
    parser.add_argument("--height",
                        type=float,
                        help="height of person in cm")
    parser.add_argument("--n_planes",
                        type=int,
                        default=1,
                        help="number of cross planes (default=0)")
    parser.add_argument("--planeaxis",
                        type=str,
                        choices=['X Axis', 'Y Axis', 'Z Axis'],
                        default="Z Axis",
                        help="""the slicing plane will be done perpendicular to the axis. OPTIONS: \'X Axis\', 
                        \'Y Axis\', \'Z Axis\' (default)""")

    args = parser.parse_args()

    if not args.config and \
            not args.height and \
            not args.n_planes:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.config is not None:
        with open(args.config) as json_file:
            config = json.load(json_file)
            check_folder_structure(config["path_dataset"])
    assert config is not None

    if args.height:
        from meshlab_filters import *
        ms = load_mesh(config)
        align_and_center(ms)
        clean(ms)
        planar_section(ms, args.height, args.n_planes, args.planeaxis)
        save_mesh(config, ms)

    print("Aligned mesh, planar sections "
          "and meshlab filter script saved to %s" % join(config["path_dataset"], "scene/"))

    sys.stdout.flush()
