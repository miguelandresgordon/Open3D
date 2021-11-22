import pymeshlab
from os.path import join


def load_mesh(config):
    # load mesh
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(join(config["path_dataset"], "scene/integrated.ply"))
    return ms


def align_and_center(ms):
    # align and center filters
    ms.transform_align_to_principal_axis()
    ms.transform_translate_center_set_origin(traslmethod='Center on Scene BBox')
    ms.matrix_freeze_current_matrix()


def clean(ms):
    # cleaning filters
    ms.remove_isolated_pieces_wrt_diameter()
    ms.remove_duplicate_faces()
    ms.remove_duplicate_vertices()
    ms.remove_zero_area_faces()
    ms.remove_unreferenced_vertices()
    ms.repair_non_manifold_edges()
    ms.repair_non_manifold_vertices_by_splitting()


def planar_section(ms, real_height, n_planes, planeaxis):
    # save geometric measures to a dictionary
    out_dict = ms.compute_geometric_measures()
    bounding_box = out_dict["bbox"]
    # scale mesh to real world dimensions
    model_height = bounding_box.dim_z()
    scale_factor = real_height / model_height
    ms.transform_scale_normalize(axisx=scale_factor)
    # compute planar section given number of cross planes
    for i in range(n_planes):
        ms.set_current_mesh(0)
        offset = float((real_height / 2) - real_height * ((n_planes - i) / (n_planes + 1)))
        ms.compute_planar_section(planeaxis=planeaxis, planeoffset=offset)


def save_mesh(config, ms):
    # save aligned mesh and section in separated files and filter script in .mlx format
    for i in range(int(ms.number_meshes())):
        if i == 0:
            ms.set_current_mesh(i)
            ms.save_current_mesh(join(config["path_dataset"], "scene/integrated_aligned.ply"))
        else:
            ms.set_current_mesh(i)
            ms.save_current_mesh(join(config["path_dataset"], "scene/sect_%03d.ply" % i))
    ms.save_filter_script(join(config["path_dataset"], "scene/section_filter_script.mlx"))
